"""
inference/service.py — Frame-Level Inference Orchestration

Responsibilities:
  1. Iterate selected frames from a video.
  2. Run PlantDetector to get bounding boxes per frame.
  3. Run DiseaseClassifier to get full probability distributions per detection.
  4. Persist Detection + FrameDiagnosis rows with mandatory *_model_version stamps.
  5. Return a per-frame summary for the aggregation layer (Grade 4).

Invariants enforced here:
  - Every Detection row carries a non-nullable detector_model_version.
  - Every FrameDiagnosis row carries a non-nullable classifier_model_version.
  - No inference result is silently discarded; failures route to is_unknown=True.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.prediction import (
    ConfidenceBand,
    Detection,
    DetectionClass,
    FrameDiagnosis,
    VideoDiagnosis,
    DecisionAuthorityStatus,
)
from ...models.video import Frame, Video, VideoStatus
from .detector import PlantDetector, DETECTOR_MODEL_VERSION
from .classifier import DiseaseClassifier, CLASSIFIER_MODEL_VERSION, TAXONOMY_CLASSES

logger = logging.getLogger("rakshak")

# ──────────────────────────────────────────────────────────────────────────────
# Data structures exchanged with the aggregation layer (Grade 4)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FrameInferenceResult:
    """Aggregated inference result for a single frame (one or more detections)."""
    frame_id: str
    frame_path: str
    quality_score: float
    detections_count: int
    # Dominant class across detections in this frame (weighted by detector conf)
    top_class: str
    top_confidence: float
    is_unknown: bool
    # Full probability distribution averaged across detections in this frame
    avg_probability_distribution: dict[str, float]


class InferenceService:
    """
    Orchestrates per-frame plant detection and disease classification.
    Uses lazy-loaded detector/classifier singletons to avoid repeated model I/O.
    """

    def __init__(self) -> None:
        self._detector = PlantDetector()
        self._classifier = DiseaseClassifier()

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _detection_class_to_enum(self, cls_str: str) -> DetectionClass:
        """Map detector output string to DetectionClass enum safely."""
        try:
            return DetectionClass(cls_str)
        except ValueError:
            return DetectionClass.leaf

    def _average_distributions(
        self, dists: list[dict[str, float]]
    ) -> dict[str, float]:
        """Average multiple probability distributions element-wise."""
        if not dists:
            return {cls: 1.0 / len(TAXONOMY_CLASSES) for cls in TAXONOMY_CLASSES}
        avg: dict[str, float] = {}
        for cls in TAXONOMY_CLASSES:
            avg[cls] = round(sum(d.get(cls, 0.0) for d in dists) / len(dists), 6)
        return avg

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    async def run_frame_inference(
        self,
        video_id: str,
        db: AsyncSession,
    ) -> list[FrameInferenceResult]:
        """
        Run detection + classification on all *selected* frames of a video.

        Persists Detection and FrameDiagnosis rows to the DB with mandatory
        model version stamps.  Returns a list of FrameInferenceResult for
        consumption by the aggregation layer.
        """
        # Load all selected frames for this video
        stmt = (
            select(Frame)
            .where(Frame.video_id == video_id, Frame.is_selected == True)
            .order_by(Frame.sequence_index)
        )
        result = await db.execute(stmt)
        frames: list[Frame] = list(result.scalars().all())

        if not frames:
            logger.warning(f"No selected frames found for video {video_id}")
            return []

        logger.info(f"Running inference on {len(frames)} selected frames for video {video_id}")

        frame_results: list[FrameInferenceResult] = []

        for frame in frames:
            try:
                frame_result = await self._process_single_frame(frame, db)
                frame_results.append(frame_result)
            except Exception as exc:
                logger.error(
                    f"Inference failed for frame {frame.id} (path={frame.storage_path}): {exc}"
                )
                # On per-frame failure: emit an unknown result but do NOT halt
                # the pipeline — other frames may still be usable.
                frame_results.append(FrameInferenceResult(
                    frame_id=frame.id,
                    frame_path=frame.storage_path,
                    quality_score=frame.blur_score or 0.0,
                    detections_count=0,
                    top_class="unknown_other",
                    top_confidence=0.0,
                    is_unknown=True,
                    avg_probability_distribution={
                        cls: round(1.0 / len(TAXONOMY_CLASSES), 6) for cls in TAXONOMY_CLASSES
                    },
                ))

        await db.commit()
        logger.info(
            f"Frame inference complete for video {video_id}: "
            f"{len(frame_results)} frames processed"
        )
        return frame_results

    async def _process_single_frame(
        self, frame: Frame, db: AsyncSession
    ) -> FrameInferenceResult:
        """Detect objects, classify each detection, persist rows, return summary."""
        # ── 1. Detection ────────────────────────────────────────────────────
        detections = self._detector.detect(frame.storage_path)
        logger.debug(
            f"Frame {frame.id}: {len(detections)} detection(s) "
            f"[detector={DETECTOR_MODEL_VERSION}]"
        )

        per_detection_dists: list[dict[str, float]] = []
        dominant_class = "unknown_other"
        dominant_conf  = 0.0
        any_unknown    = False

        for det in detections:
            # ── 2. Persist Detection row ────────────────────────────────────
            det_row = Detection(
                frame_id=frame.id,
                bbox=det.bbox,
                detection_class=self._detection_class_to_enum(det.detection_class),
                detector_confidence=det.confidence,
                detector_model_version=det.detector_model_version,
            )
            db.add(det_row)
            # Flush to generate det_row.id before creating FrameDiagnosis FK
            await db.flush()

            # ── 3. Classification ───────────────────────────────────────────
            cls_result = self._classifier.classify(frame.storage_path, det.bbox)
            logger.debug(
                f"  Detection {det_row.id}: top={cls_result.top_class} "
                f"conf={cls_result.top_confidence:.3f} "
                f"unk={cls_result.is_unknown} "
                f"[classifier={CLASSIFIER_MODEL_VERSION}]"
            )

            # ── 4. Persist FrameDiagnosis row ───────────────────────────────
            fd_row = FrameDiagnosis(
                detection_id=det_row.id,
                probability_distribution=cls_result.probability_distribution,
                classifier_model_version=cls_result.classifier_model_version,
            )
            db.add(fd_row)

            per_detection_dists.append(cls_result.probability_distribution)
            if cls_result.is_unknown:
                any_unknown = True

            # Track dominant class by detection confidence × top probability
            weight = det.confidence * cls_result.top_confidence
            if weight > dominant_conf:
                dominant_conf  = weight
                dominant_class = cls_result.top_class

        avg_dist = self._average_distributions(per_detection_dists)
        composite_quality = float(frame.blur_score or 50.0)

        return FrameInferenceResult(
            frame_id=frame.id,
            frame_path=frame.storage_path,
            quality_score=composite_quality,
            detections_count=len(detections),
            top_class=dominant_class if not any_unknown else "unknown_other",
            top_confidence=dominant_conf,
            is_unknown=any_unknown,
            avg_probability_distribution=avg_dist,
        )

    @property
    def detector_model_version(self) -> str:
        return self._detector.model_version

    @property
    def classifier_model_version(self) -> str:
        return self._classifier.model_version


# Module-level singleton
inference_service = InferenceService()
