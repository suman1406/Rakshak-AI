"""
detector.py — Plant/Leaf Region Detector

Design goals (Architecture §4, rule 8 — CPU-safe on Mac M2 dev):
  - Zero network I/O at inference time; models are loaded from disk on first use.
  - Lazy loading: model weights are only instantiated when the first frame is
    submitted, not at import time (keeps tests fast when ultralytics is mocked).
  - Returns normalized bounding boxes (x_center, y_center, w, h all in [0,1])
    consistent with the DB schema in models/prediction.py.

MVP uses YOLOv8n (nano, 6.2 MB) as the detection backbone.  It provides fast,
CPU-safe leaf/plant localisation without any fine-tuning on the COCO general
object classes; the full-frame synthetic fallback guarantees the downstream
classifier always has at least one region to score.

The model version constant drives the non-nullable `detector_model_version`
column in every `detections` row.  Hot-swapping to a domain-fine-tuned YOLOv8
checkpoint is a drop-in change: update DETECTOR_MODEL_VERSION and swap the
weights file — no other code changes required.
"""

from __future__ import annotations

import logging
import pathlib
from dataclasses import dataclass

logger = logging.getLogger("rakshak")

# ──────────────────────────────────────────────────────────────────────────────
# Taxonomy & version constants
# ──────────────────────────────────────────────────────────────────────────────
DETECTOR_MODEL_VERSION = "yolov8n-leaf-v1.0"

WEIGHTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "weights"
YOLO_WEIGHTS_PATH = WEIGHTS_DIR / "yolov8n.pt"

# Confidence threshold for keeping a detection bounding box.
DETECTOR_CONFIDENCE_THRESHOLD = 0.30


@dataclass
class DetectionResult:
    """Single bounding-box detection on one frame."""
    frame_path: str
    bbox: dict          # {"x": float, "y": float, "w": float, "h": float} — normalised [0,1]
    detection_class: str  # matches DetectionClass enum values in models/prediction.py
    confidence: float
    detector_model_version: str = DETECTOR_MODEL_VERSION


class PlantDetector:
    """
    Wraps a YOLOv8n object detection model for plant/leaf localisation.

    Thread-safety: the model is loaded once and reused across calls.  YOLOv8
    selects the fastest available device (MPS > CUDA > CPU) automatically.

    The detect() method always returns at least one DetectionResult per frame:
    when no boxes exceed the confidence threshold, a synthetic full-frame region
    {x:0.5, y:0.5, w:1.0, h:1.0} is inserted so the downstream classifier
    always has a region to score.
    """

    def __init__(
        self,
        confidence_threshold: float = DETECTOR_CONFIDENCE_THRESHOLD,
        model_version: str = DETECTOR_MODEL_VERSION,
    ) -> None:
        self._confidence_threshold = confidence_threshold
        self._model_version = model_version
        self._model = None          # lazy-loaded

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _load_model(self):
        """Lazy-load YOLOv8n on first inference call."""
        if self._model is not None:
            return

        try:
            from ultralytics import YOLO

            if not YOLO_WEIGHTS_PATH.exists():
                raise FileNotFoundError(
                    f"YOLOv8 weights not found at {YOLO_WEIGHTS_PATH}. "
                    "Download yolov8n.pt from https://github.com/ultralytics/assets/releases "
                    "and place it in backend/app/weights/."
                )

            self._model = YOLO(str(YOLO_WEIGHTS_PATH))
            logger.info(
                f"PlantDetector loaded: {self._model_version} | "
                f"weights={YOLO_WEIGHTS_PATH.name}"
            )

        except ImportError as exc:
            raise RuntimeError(
                "ultralytics is required for inference. "
                "Install with: pip install 'ultralytics>=8.0.0'"
            ) from exc

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def detect(self, image_path: str) -> list[DetectionResult]:
        """
        Run YOLOv8 detection on a single frame image.

        Args:
            image_path: Absolute path to a JPEG/PNG frame file.

        Returns:
            List of DetectionResult objects.  Always non-empty — a synthetic
            full-frame bbox is appended if no real detections exceed the
            confidence threshold.
        """
        self._load_model()

        # Run inference — verbose=False suppresses YOLOv8 console spam
        results = self._model(image_path, verbose=False)

        # YOLOv8 Results: results[0].boxes.xywhn  → Tensor[N, 4] normalized
        #                  results[0].boxes.conf   → Tensor[N]
        #                  results[0].boxes.cls    → Tensor[N]
        boxes_xywhn = results[0].boxes.xywhn.cpu().numpy()  # shape [N, 4]
        confidences = results[0].boxes.conf.cpu().numpy()    # shape [N]

        detection_results: list[DetectionResult] = []

        for (x_c, y_c, w, h), conf in zip(boxes_xywhn, confidences):
            if float(conf) < self._confidence_threshold:
                continue

            # Clamp to [0, 1] — defensive guard against floating-point edge cases
            bbox = {
                "x": round(float(min(max(x_c, 0.0), 1.0)), 4),
                "y": round(float(min(max(y_c, 0.0), 1.0)), 4),
                "w": round(float(min(max(w,   0.0), 1.0)), 4),
                "h": round(float(min(max(h,   0.0), 1.0)), 4),
            }

            detection_results.append(DetectionResult(
                frame_path=image_path,
                bbox=bbox,
                detection_class="leaf",
                confidence=float(conf),
                detector_model_version=self._model_version,
            ))

        # If no objects detected (or all below threshold), synthesise a
        # full-frame "leaf" region so the classifier always has ≥1 region.
        if not detection_results:
            detection_results.append(DetectionResult(
                frame_path=image_path,
                bbox={"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0},
                detection_class="leaf",
                confidence=0.40,
                detector_model_version=self._model_version,
            ))

        return detection_results

    @property
    def model_version(self) -> str:
        return self._model_version
