import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.config import settings
from ...core.logging import logger
from ...db.session import async_session_factory
from ...models.farm import Field
from ...models.prediction import ConfidenceBand, DecisionAuthorityStatus, VideoDiagnosis
from ...models.video import Frame, Video, VideoStatus
from ..processing.extractor import VideoFrameExtractor
from ..processing.quality import QualityFilterService
from ..inference.service import InferenceService
from ..inference.classifier import TAXONOMY_CLASSES

class VideoIngestionService:
    def __init__(self):
        self.extractor = VideoFrameExtractor(target_fps=1.0, max_frames=30)
        self.quality_filter = QualityFilterService(
            min_blur_threshold=settings.QUALITY_BLUR_THRESHOLD,
            min_exposure_score=40.0,
            near_dup_diff_threshold=8.0,
            max_selected_frames=15,
        )
        self._inference = InferenceService()

    async def init_upload(
        self,
        file: UploadFile,
        field_id: str,
        user_id: str,
        consent: bool,
        db: AsyncSession,
    ) -> Video:
        if not consent:
            raise HTTPException(status_code=400, detail="User consent is required to process field video")

        extension = Path(file.filename or "video.mp4").suffix.lower()
        allowed = {item.strip().lower() for item in settings.ALLOWED_VIDEO_EXTENSIONS.split(",") if item.strip()}
        if extension not in allowed:
            raise HTTPException(status_code=415, detail="Unsupported video format")

        # Validate field exists
        stmt = select(Field).where(Field.id == field_id)
        result = await db.execute(stmt)
        field = result.scalar_one_or_none()
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")

        video_id = str(uuid4())
        upload_dir = Path(settings.LOCAL_STORAGE_DIR) / "videos" / video_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
        video_file_path = upload_dir / f"video{file_suffix}"

        # Write uploaded chunks to disk
        with open(video_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if video_file_path.stat().st_size > settings.MAX_UPLOAD_BYTES:
            video_file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=413, detail="Video exceeds the maximum upload size")

        video = Video(
            id=video_id,
            field_id=field_id,
            uploaded_by=user_id,
            status=VideoStatus.uploaded,
            storage_path=str(video_file_path),
            usable_frames_count=0,
            total_frames_extracted=0,
        )
        db.add(video)
        await db.commit()
        await db.refresh(video)
        logger.info(f"Video {video_id} uploaded successfully, storage_path={video_file_path}")
        return video

    async def _process_pipeline_internal(self, video_id: str, db: AsyncSession):
        stmt = select(Video).where(Video.id == video_id)
        result = await db.execute(stmt)
        video = result.scalar_one_or_none()
        if not video:
            logger.error(f"Video {video_id} not found for background processing")
            return

        # 1. State: Validating
        video.status = VideoStatus.validating
        await db.commit()
        logger.info(f"Video {video_id} -> validating")

        # 2. Extract frames
        frames_dir = Path(settings.LOCAL_STORAGE_DIR) / "frames" / video_id
        frames_dir.mkdir(parents=True, exist_ok=True)

        extracted_frames = self.extractor.extract_frames(
            video_path=video.storage_path,
            output_dir=str(frames_dir),
        )
        video.total_frames_extracted = len(extracted_frames)

        # 3. State: Processing Quality
        video.status = VideoStatus.processing
        await db.commit()
        logger.info(f"Video {video_id} -> processing (extracted {len(extracted_frames)} frames)")

        quality_results, usable_count, avg_quality = self.quality_filter.evaluate_and_filter_frames(
            extracted_frames
        )

        # Store Frame rows in DB
        for q in quality_results:
            frame_row = Frame(
                video_id=video_id,
                storage_path=q.file_path,
                blur_score=q.blur_score,
                exposure_score=q.exposure_score,
                is_selected=q.is_selected,
                sequence_index=q.sequence_index,
            )
            db.add(frame_row)

        video.quality_score = avg_quality
        video.usable_frames_count = usable_count

        # 4. Check Minimum Usable Frame Threshold (Default: 5)
        if usable_count < settings.MIN_USABLE_FRAMES_THRESHOLD:
            video.status = VideoStatus.insufficient_evidence
            video.error_detail = (
                f"Insufficient usable frames extracted ({usable_count} usable < "
                f"{settings.MIN_USABLE_FRAMES_THRESHOLD} threshold). "
                "Footage may be too blurry, dark, or shaky to produce an evidence-backed analysis."
            )
            await db.commit()
            logger.warning(
                f"Video {video_id} -> insufficient_evidence: {video.error_detail}"
            )
            return

        # 5. Inference: Analyzing
        video.status = VideoStatus.analyzing
        await db.commit()
        logger.info(f"Video {video_id} -> analyzing ({usable_count} usable frames)")

        # Run detection + classification on all selected frames (Grade 3)
        frame_results = await self._inference.run_frame_inference(video_id, db)

        # 6. Aggregation: simple confidence-weighted vote across frames
        video.status = VideoStatus.aggregating
        await db.commit()
        logger.info(f"Video {video_id} -> aggregating ({len(frame_results)} frame results)")

        # Aggregate probability distributions weighted by per-frame quality score
        agg_dist: dict[str, float] = {cls: 0.0 for cls in TAXONOMY_CLASSES}
        weight_sum = 0.0
        known_frame_count = 0

        for fr in frame_results:
            if fr.is_unknown:
                continue
            weight = max(fr.quality_score, 1.0)
            for cls, prob in fr.avg_probability_distribution.items():
                agg_dist[cls] = agg_dist.get(cls, 0.0) + prob * weight
            weight_sum += weight
            known_frame_count += 1

        if weight_sum > 0:
            agg_dist = {cls: round(v / weight_sum, 6) for cls, v in agg_dist.items()}
        else:
            # All frames unknown: uniform distribution
            n = len(TAXONOMY_CLASSES)
            agg_dist = {cls: round(1.0 / n, 6) for cls in TAXONOMY_CLASSES}

        # Top-1 from aggregated distribution
        top_class = max(agg_dist, key=lambda k: agg_dist[k])
        top_conf  = agg_dist[top_class]

        # OOD routing: if unknown_other wins or top confidence too low
        all_unknown = all(fr.is_unknown for fr in frame_results)
        is_unknown  = all_unknown or top_class == "unknown_other" or top_conf < 0.30

        # Confidence band mapping
        if top_conf >= 0.90:
            band = ConfidenceBand.high
        elif top_conf >= 0.70:
            band = ConfidenceBand.medium
        else:
            band = ConfidenceBand.low

        # Severity heuristic: fraction of non-unknown frames × avg detection density
        if len(frame_results) > 0:
            diseased_fraction = known_frame_count / len(frame_results)
        else:
            diseased_fraction = 0.0

        if is_unknown:
            severity_level = 0
            affected_estimate = 0.0
        elif diseased_fraction >= 0.70:
            severity_level = 3    # Severe
            affected_estimate = round(min(diseased_fraction, 0.95), 2)
        elif diseased_fraction >= 0.40:
            severity_level = 2    # Moderate
            affected_estimate = round(diseased_fraction * 0.8, 2)
        elif diseased_fraction >= 0.15:
            severity_level = 1    # Mild
            affected_estimate = round(diseased_fraction * 0.5, 2)
        else:
            severity_level = 0
            affected_estimate = 0.0

        # Build explanation (will be replaced by LLM in Grade 5)
        disease_display = top_class.replace("_", " ").title()
        if is_unknown:
            explanation = (
                "Visual evidence is insufficient to confidently classify a disease. "
                "Please consult an agronomist for a manual inspection."
            )
        elif band == ConfidenceBand.high:
            explanation = (
                f"Strong visual indicators of {disease_display} detected across "
                f"{known_frame_count} frame(s). "
                "This is an AI estimate, not a confirmed diagnosis. Verify with an agronomist."
            )
        elif band == ConfidenceBand.medium:
            explanation = (
                f"Possible signs of {disease_display} observed in {known_frame_count} frame(s). "
                "Confidence is moderate. This is an AI estimate, not a confirmed diagnosis."
            )
        else:
            explanation = (
                f"Weak visual indicators suggest possible {disease_display}. "
                "Low confidence — inspect field manually. "
                "This is an AI estimate, not a confirmed diagnosis."
            )

        diagnosis = VideoDiagnosis(
            video_id=video_id,
            disease_id=None,
            is_unknown=is_unknown,
            confidence=top_conf,
            confidence_band=band,
            severity_level=severity_level,
            affected_plant_estimate=affected_estimate,
            supporting_frames=known_frame_count,
            total_frames=len(extracted_frames),
            aggregation_model_version="bayes-v1.0",
            decision_authority=DecisionAuthorityStatus.advisory_only,
            explanation=explanation,
        )
        db.add(diagnosis)

        video.status = VideoStatus.ready
        await db.commit()
        logger.info(
            f"Video {video_id} -> ready | top={top_class} conf={top_conf:.3f} "
            f"band={band.value} severity={severity_level} unk={is_unknown}"
        )

    async def execute_processing_pipeline(self, video_id: str, db_session: AsyncSession | None = None):
        """
        Executes frame extraction, quality scoring, and threshold validation.
        Uses supplied db_session or opens a new session.
        """
        if db_session is not None:
            try:
                await self._process_pipeline_internal(video_id, db_session)
            except Exception as e:
                logger.exception(f"Error in video processing pipeline for {video_id}: {e}")
                stmt = select(Video).where(Video.id == video_id)
                result = await db_session.execute(stmt)
                video = result.scalar_one_or_none()
                if video:
                    video.status = VideoStatus.failed
                    video.error_detail = str(e)
                    video.last_failure_at = datetime.now(timezone.utc)
                    await db_session.commit()
                raise
        else:
            async with async_session_factory() as db:
                try:
                    await self._process_pipeline_internal(video_id, db)
                except Exception as e:
                    logger.exception(f"Error in video processing pipeline for {video_id}: {e}")
                    stmt = select(Video).where(Video.id == video_id)
                    result = await db.execute(stmt)
                    video = result.scalar_one_or_none()
                    if video:
                        video.status = VideoStatus.failed
                        video.error_detail = str(e)
                        video.last_failure_at = datetime.now(timezone.utc)
                        await db.commit()
                    raise

ingestion_service = VideoIngestionService()
