from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.deps import get_current_user, get_db
from app.core.scopes import video_scope
from app.core.audit import write_audit_log
from app.models.farm import Field
from app.models.identity import User
from app.models.prediction import VideoDiagnosis
from app.models.video import Frame, Video, VideoStatus
from app.modules.ingestion.service import ingestion_service
from app.modules.reporting.result_contract import disease_slug, result_state, severity_name
from app.schemas.video import (
    VideoAnalysisDiagnosis,
    VideoAnalysisEvidence,
    VideoAnalysisResponse,
    VideoStatusResponse,
    VideoUploadResponse,
)
from app.worker import process_video

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.get("")
async def list_videos(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    field_id: str | None = Query(None),
    status_filter: VideoStatus | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    stmt = select(Video).join(Video.field).join(Field.farm).where(video_scope(current_user))
    if field_id:
        stmt = stmt.where(Video.field_id == field_id)
    if status_filter:
        stmt = stmt.where(Video.status == status_filter)
    videos = (await db.execute(stmt.order_by(Video.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return [{"video_id": video.id, "field_id": video.field_id, "status": video.status, "created_at": video.created_at, "duration_seconds": video.duration_seconds, "error_detail": video.error_detail} for video in videos]

@router.get("/{video_id}")
async def get_video(
    video_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    video = (await db.execute(select(Video).join(Video.field).join(Field.farm).where(Video.id == video_id, video_scope(current_user)))).scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"video_id": video.id, "field_id": video.field_id, "status": video.status, "created_at": video.created_at, "duration_seconds": video.duration_seconds, "quality_score": video.quality_score, "usable_frames_count": video.usable_frames_count, "total_frames_extracted": video.total_frames_extracted, "error_detail": video.error_detail}

@router.post("", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    field_id: Annotated[str, Form(...)],
    consent: Annotated[bool, Form(...)],
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    field_result = await db.execute(select(Field).join(Field.farm).where(Field.id == field_id, video_scope(current_user)))
    if field_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Field not found")
    video = await ingestion_service.init_upload(
        file=file,
        field_id=field_id,
        user_id=current_user.id,
        consent=consent,
        db=db,
    )
    await write_audit_log(
        db,
        actor_user_id=current_user.id,
        action="video.uploaded",
        entity_type="video",
        entity_id=video.id,
        metadata={"field_id": field_id},
    )
    await db.commit()

    # Launch processing pipeline as background task
    process_video.delay(video.id)

    return VideoUploadResponse(
        video_id=video.id,
        field_id=video.field_id,
        status=video.status,
        filename=file.filename or "video.mp4",
        created_at=video.created_at,
    )

@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(
    video_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Video).join(Video.field).join(Field.farm).where(Video.id == video_id, video_scope(current_user))
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoStatusResponse(
        video_id=video.id,
        status=video.status,
        quality_score=video.quality_score,
        usable_frames_count=video.usable_frames_count,
        total_frames_extracted=video.total_frames_extracted,
        error_detail=video.error_detail,
    )

@router.get("/{video_id}/analysis", response_model=VideoAnalysisResponse)
async def get_video_analysis(
    video_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(Video)
        .join(Video.field).join(Field.farm)
        .options(selectinload(Video.diagnoses).selectinload(VideoDiagnosis.disease))
        .where(Video.id == video_id, video_scope(current_user))
    )
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status == VideoStatus.insufficient_evidence:
        return VideoAnalysisResponse(
            video_id=video.id,
            crop="soybean",
            result_state="insufficient_evidence",
            evidence=VideoAnalysisEvidence(
                frames_analyzed=video.total_frames_extracted or 0,
                supporting_frames=0,
                quality_score=video.quality_score,
            ),
            retake_guidance=video.error_detail or "Retake the video in better light with steady coverage of the crop canopy.",
        )

    if video.status == VideoStatus.failed:
        return VideoAnalysisResponse(
            video_id=video.id,
            crop="soybean",
            result_state="failed",
            evidence=VideoAnalysisEvidence(
                frames_analyzed=video.total_frames_extracted or 0,
                supporting_frames=0,
                quality_score=video.quality_score,
            ),
            retake_guidance=video.error_detail or "The scan could not be completed. Retry or upload a new video.",
        )

    if video.status != VideoStatus.ready:
        raise HTTPException(
            status_code=409,
            detail=f"Analysis not ready. Current status: {video.status.value}",
        )

    diagnosis_row = video.diagnoses[0] if video.diagnoses else None
    if not diagnosis_row:
        raise HTTPException(status_code=409, detail="Analysis completed without a persisted diagnosis")

    return VideoAnalysisResponse(
        video_id=video.id,
        diagnosis_id=diagnosis_row.id,
        crop="soybean",
        result_state=result_state(diagnosis_row),
        diagnosis=VideoAnalysisDiagnosis(
            disease=disease_slug(diagnosis_row),
            is_unknown=diagnosis_row.is_unknown,
            confidence=diagnosis_row.confidence,
            confidence_band=diagnosis_row.confidence_band.value,
            severity=severity_name(diagnosis_row.severity_level),
            affected_plant_estimate=diagnosis_row.affected_plant_estimate or 0.0,
        ),
        evidence=VideoAnalysisEvidence(
            frames_analyzed=video.total_frames_extracted or 0,
            supporting_frames=diagnosis_row.supporting_frames or 0,
            quality_score=video.quality_score,
        ),
        model_versions={
            "aggregation": diagnosis_row.aggregation_model_version,
        },
    )

@router.get("/{video_id}/frames")
async def get_video_frames(
    video_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Frame).join(Frame.video).join(Video.field).join(Field.farm).where(Frame.video_id == video_id, video_scope(current_user)).order_by(Frame.sequence_index)
    result = await db.execute(stmt)
    frames = result.scalars().all()
    return [
        {
            "id": f.id,
            "sequence_index": f.sequence_index,
            "blur_score": f.blur_score,
            "exposure_score": f.exposure_score,
            "is_selected": f.is_selected,
            "evidence_url": f"/api/v1/videos/{video_id}/frames/{f.id}/content",
        }
        for f in frames
    ]


@router.get("/{video_id}/frames/{frame_id}/content")
async def get_frame_content(
    video_id: str,
    frame_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(Frame)
        .join(Frame.video).join(Video.field).join(Field.farm)
        .where(Frame.id == frame_id, Frame.video_id == video_id, video_scope(current_user))
    )
    result = await db.execute(stmt)
    frame = result.scalar_one_or_none()
    if not frame or not Path(frame.storage_path).is_file():
        raise HTTPException(status_code=404, detail="Evidence frame not found")
    return FileResponse(frame.storage_path, media_type="image/jpeg", filename=f"frame-{frame.sequence_index}.jpg")
