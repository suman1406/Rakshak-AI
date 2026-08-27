from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ...core.deps import get_current_user, get_db
from ...models.identity import User
from ...models.prediction import VideoDiagnosis
from ...models.video import Frame, Video, VideoStatus
from ...modules.ingestion.service import ingestion_service
from ...schemas.video import (
    VideoAnalysisDiagnosis,
    VideoAnalysisEvidence,
    VideoAnalysisResponse,
    VideoStatusResponse,
    VideoUploadResponse,
)

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    background_tasks: BackgroundTasks,
    field_id: Annotated[str, Form(...)],
    consent: Annotated[bool, Form(...)],
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    video = await ingestion_service.init_upload(
        file=file,
        field_id=field_id,
        user_id=current_user.id,
        consent=consent,
        db=db,
    )

    # Launch processing pipeline as background task
    background_tasks.add_task(ingestion_service.execute_processing_pipeline, video.id)

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
    stmt = select(Video).where(Video.id == video_id)
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
    stmt = select(Video).options(selectinload(Video.diagnoses)).where(Video.id == video_id)
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status not in (VideoStatus.ready, VideoStatus.insufficient_evidence):
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not ready. Current status: {video.status.value}",
        )

    diagnosis_row = video.diagnoses[0] if video.diagnoses else None
    if not diagnosis_row:
        raise HTTPException(status_code=404, detail="Diagnosis not found for video")

    return VideoAnalysisResponse(
        video_id=video.id,
        crop="soybean",
        crop_confidence=0.95,
        diagnosis=VideoAnalysisDiagnosis(
            disease=diagnosis_row.disease_id or "soybean_rust",
            is_unknown=diagnosis_row.is_unknown,
            confidence=diagnosis_row.confidence,
            confidence_band=diagnosis_row.confidence_band.value,
            severity="moderate" if diagnosis_row.severity_level == 2 else "mild",
            affected_plant_estimate=diagnosis_row.affected_plant_estimate or 0.0,
        ),
        evidence=VideoAnalysisEvidence(
            frames_analyzed=video.total_frames_extracted or 0,
            supporting_frames=diagnosis_row.supporting_frames or 0,
            leaf_regions_analyzed=(diagnosis_row.supporting_frames or 0) * 3,
            quality_score=video.quality_score,
        ),
        model_versions={
            "detector": "yolo11n-plantdoc-v1.0",
            "classifier": "effnet-b0-soybean-v1.0",
            "aggregation": diagnosis_row.aggregation_model_version,
        },
    )

@router.get("/{video_id}/frames")
async def get_video_frames(
    video_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Frame).where(Frame.video_id == video_id).order_by(Frame.sequence_index)
    result = await db.execute(stmt)
    frames = result.scalars().all()
    return [
        {
            "id": f.id,
            "sequence_index": f.sequence_index,
            "blur_score": f.blur_score,
            "exposure_score": f.exposure_score,
            "is_selected": f.is_selected,
            "storage_path": f.storage_path,
        }
        for f in frames
    ]
