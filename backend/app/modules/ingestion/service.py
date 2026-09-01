import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile
import cv2
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.config import settings
from ...core.logging import logger
from ...db.session import async_session_factory
from ...models.farm import Disease, Field
from ...models.prediction import ConfidenceBand, DecisionAuthorityStatus, Detection, VideoDiagnosis
from ...models.video import Frame, Video, VideoStatus
from ..processing.extractor import VideoFrameExtractor
from ..processing.quality import QualityFilterService
from ..inference.service import InferenceService
from ..inference.classifier import TAXONOMY_CLASSES
from ..aggregation.bayes import BayesianAggregator
from ..aggregation.severity import SeverityEstimator
from ..reporting.llm_advisor import generate_advisory_report
from ..reporting.templates import get_canned_report
from ...guardrails.certainty_filter import CertaintyGuardrailFilter

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

    def _validate_video_file(self, path: Path) -> float:
        """Reject mislabeled, undecodable, or out-of-contract captures early."""
        capture = cv2.VideoCapture(str(path))
        try:
            if not capture.isOpened():
                raise HTTPException(status_code=422, detail="Uploaded file is not a decodable video")
            fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
            frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            if fps <= 0 or frames <= 0 or width <= 0 or height <= 0:
                raise HTTPException(status_code=422, detail="Video metadata could not be read")
            duration = frames / fps
            if not settings.MIN_VIDEO_DURATION_SECONDS <= duration <= settings.MAX_VIDEO_DURATION_SECONDS:
                raise HTTPException(status_code=422, detail=f"Video duration must be {settings.MIN_VIDEO_DURATION_SECONDS:g}–{settings.MAX_VIDEO_DURATION_SECONDS:g} seconds")
            if width > settings.MAX_VIDEO_WIDTH or height > settings.MAX_VIDEO_HEIGHT:
                raise HTTPException(status_code=422, detail="Video resolution exceeds the capture limit")
            return duration
        finally:
            capture.release()

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

        # Bound the write itself: checking only after copy permits an oversized
        # request to exhaust local storage before rejection.
        bytes_written = 0
        try:
            with open(video_file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    bytes_written += len(chunk)
                    if bytes_written > settings.MAX_UPLOAD_BYTES:
                        raise HTTPException(status_code=413, detail="Video exceeds the maximum upload size")
                    buffer.write(chunk)
        except Exception:
            shutil.rmtree(upload_dir, ignore_errors=True)
            try:
                upload_dir.parent.rmdir()
            except OSError:
                pass
            raise

        try:
            duration_seconds = self._validate_video_file(video_file_path)
        except Exception:
            shutil.rmtree(upload_dir, ignore_errors=True)
            raise

        video = Video(
            id=video_id,
            field_id=field_id,
            uploaded_by=user_id,
            status=VideoStatus.uploaded,
            storage_path=str(video_file_path),
            duration_seconds=duration_seconds,
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
        if video.status in (VideoStatus.ready, VideoStatus.insufficient_evidence):
            logger.info(f"Video {video_id} is already terminal ({video.status.value}); skipping duplicate delivery")
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

        # A retry may follow a crash after frames were committed but before the
        # diagnosis was persisted. Replace that attempt's derived rows so frame
        # records remain idempotent for a video.
        await db.execute(delete(Frame).where(Frame.video_id == video_id))
        # Also clean up any detection/diagnosis records from previous attempts
        await db.execute(delete(Detection).where(Detection.frame_id.in_(
            select(Frame.id).where(Frame.video_id == video_id)
        )))
        await db.flush()

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

        # 6. Aggregation: Bayesian temporal aggregation
        video.status = VideoStatus.aggregating
        await db.commit()
        logger.info(f"Video {video_id} -> aggregating ({len(frame_results)} frame results)")

        # Use BayesianAggregator for intelligent frame combination
        aggregator = BayesianAggregator()
        agg_result = aggregator.aggregate(frame_results)

        top_class = agg_result.top_class
        top_conf = agg_result.top_confidence
        agg_dist = agg_result.probability_distribution
        is_unknown = agg_result.is_unknown
        known_frame_count = agg_result.supporting_frames

        # Confidence band mapping
        if top_conf >= 0.90:
            band = ConfidenceBand.high
        elif top_conf >= 0.70:
            band = ConfidenceBand.medium
        else:
            band = ConfidenceBand.low

        # Severity estimation using dedicated module
        severity_estimator = SeverityEstimator()
        severity = severity_estimator.estimate(frame_results, is_unknown)
        severity_level = severity.severity_level
        affected_estimate = severity.affected_plant_estimate

        # 7. LLM Advisory Generation with Guardrails
        action_items: list[str] = []
        guardrail_filter = CertaintyGuardrailFilter()
        disease_slug = top_class  # Use the classifier output as the slug
        disease_display = top_class.replace("_", " ").title()  # Define before LLM call

        try:
            llm_result = await generate_advisory_report(
                crop="soybean",
                disease=disease_display,
                confidence=top_conf,
                confidence_band=band.value,
                severity_level=severity_level,
                affected_plant_estimate=affected_estimate,
                supporting_frames=known_frame_count,
            )
            
            if llm_result:
                # Run LLM explanation through guardrail filter
                llm_explanation = llm_result.get("explanation", "")
                guardrail_result = guardrail_filter.evaluate(llm_explanation)
                if guardrail_result.passed:
                    explanation = llm_explanation
                    action_items = llm_result.get("action_items", [])
                    logger.info(f"Video {video_id} -> LLM advisory generated and passed guardrails")
                else:
                    logger.warning(f"Video {video_id} -> LLM output failed guardrails: {guardrail_result.violations}, using template fallback")
                    template = get_canned_report(disease_slug)
                    explanation = template.get("explanation", "")
                    action_items_str = template.get("action_items", "")
                    action_items = action_items_str.split("\n") if isinstance(action_items_str, str) else []
            else:
                # LLM returned None (API key missing or call failed), use template
                template = get_canned_report(disease_slug)
                explanation = template.get("explanation", "")
                action_items_str = template.get("action_items", "")
                action_items = action_items_str.split("\n") if isinstance(action_items_str, str) else []
                
        except Exception as e:
            logger.warning(f"Video {video_id} -> LLM advisory generation failed: {e}, using template fallback")
            template = get_canned_report(disease_slug)
            explanation = template.get("explanation", "")
            action_items_str = template.get("action_items", "")
            action_items = action_items_str.split("\n") if isinstance(action_items_str, str) else []

        # Build explanation - use LLM result if available, otherwise fallback to default template
        disease_display = top_class.replace("_", " ").title()
        
        # Only use default explanation as fallback if LLM didn't produce one
        if not explanation or explanation.strip() == "":
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

        # Persist a database disease identity only when the classifier's launch
        # taxonomy can be matched to the active, versioned catalogue. An
        # unmatched class is safer as "unknown" than as an invented diagnosis.
        disease_id = None
        if not is_unknown:
            # Map classifier output class names (from classes.json) to Disease names in DB
            taxonomy_names = {
                "soybean_rust": "Soybean Rust",
                "soybean_frogeye_leaf_spot": "Frogeye Leaf Spot",
                "soybean_healthy": "Healthy",
                "soybean_bacterial_blight": "Sudden Death Syndrome",
            }
            disease_name = taxonomy_names.get(top_class)
            if disease_name:
                disease = (
                    await db.execute(
                        select(Disease).where(Disease.name == disease_name, Disease.active.is_(True))
                    )
                ).scalar_one_or_none()
                if disease:
                    disease_id = disease.id
                else:
                    is_unknown = True
            else:
                is_unknown = True

        if is_unknown:
            severity_level = 0
            affected_estimate = 0.0

        diagnosis = VideoDiagnosis(
            video_id=video_id,
            disease_id=disease_id,
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
