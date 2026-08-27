"""
classifier.py — Soybean Disease Classifier

Design goals:
  - Launch-locked disease taxonomy (6 classes). New classes require a taxonomy
    version bump and a new `classifier_model_version` — never silent expansion.
  - Always outputs the *full probability distribution* over all classes, not
    just top-1. This is stored in `frame_diagnoses.probability_distribution`.
  - CPU-safe on Mac M2 dev (uses EfficientNet-B0 pretrained on ImageNet as
    feature backbone; fine-tuning on soybean data is a later production step).
  - Lazy-loaded model to keep test collection fast.

Taxonomy (locked, v1.0):
  0 → soybean_rust
  1 → bacterial_blight
  2 → frogeye_leaf_spot
  3 → septoria_brown_spot
  4 → healthy
  5 → unknown_other

The class-index ordering is stable and referenced in TAXONOMY_CLASSES below.
Any model retrain that changes this ordering MUST bump CLASSIFIER_MODEL_VERSION.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger("rakshak")

# ──────────────────────────────────────────────────────────────────────────────
# Locked taxonomy (Grade 3 — v1.0)
# ──────────────────────────────────────────────────────────────────────────────
CLASSIFIER_MODEL_VERSION = "effnet-b0-soybean-v1.0"

TAXONOMY_VERSION = "v1.0"

# Class index → canonical slug mapping (never reorder without bumping version)
TAXONOMY_CLASSES: list[str] = [
    "soybean_rust",
    "bacterial_blight",
    "frogeye_leaf_spot",
    "septoria_brown_spot",
    "healthy",
    "unknown_other",
]

NUM_CLASSES = len(TAXONOMY_CLASSES)

# OOD routing: if `unknown_other` probability exceeds this OR max non-unknown
# class probability falls below this, route to `is_unknown=True`.
OOD_UNKNOWN_THRESHOLD = 0.45
OOD_MAX_CONFIDENCE_FLOOR = 0.30

# ImageNet normalisation (standard for pretrained torchvision models)
_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD  = [0.229, 0.224, 0.225]
_INPUT_SIZE = 224


@dataclass
class ClassificationResult:
    """Per-detection disease classification output."""
    frame_path: str
    detection_bbox: dict
    probability_distribution: dict[str, float]   # class_slug → probability
    top_class: str
    top_confidence: float
    is_unknown: bool
    classifier_model_version: str = CLASSIFIER_MODEL_VERSION


class DiseaseClassifier:
    """
    Wraps an EfficientNet-B0 ImageNet backbone fine-tuned for soybean disease
    classification over the locked 6-class taxonomy.

    At MVP launch the head is randomly initialised (simulating the shape of a
    fine-tuned model) because we have no labelled soybean dataset yet.  The
    softmax outputs are therefore not calibrated, but the architecture, DB
    schema, version stamping, and OOD routing are fully production-ready so
    that swapping in real weights requires only replacing the state_dict.
    """

    def __init__(
        self,
        model_version: str = CLASSIFIER_MODEL_VERSION,
        ood_unknown_threshold: float = OOD_UNKNOWN_THRESHOLD,
        ood_max_confidence_floor: float = OOD_MAX_CONFIDENCE_FLOOR,
    ) -> None:
        self._model_version = model_version
        self._ood_unknown_threshold = ood_unknown_threshold
        self._ood_max_conf_floor = ood_max_confidence_floor
        self._model = None          # lazy-loaded
        self._preprocess = None

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _load_model(self):
        """Lazy-load EfficientNet-B0 with a custom classification head."""
        if self._model is not None:
            return

        try:
            import torch
            import torch.nn as nn
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            from torchvision import transforms

            weights = EfficientNet_B0_Weights.DEFAULT
            backbone = efficientnet_b0(weights=weights)

            # Replace the head with a soybean-disease head (NUM_CLASSES outputs)
            in_features = backbone.classifier[1].in_features
            backbone.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(in_features, NUM_CLASSES),
            )
            backbone.eval()

            # Device selection (MPS → CUDA → CPU)
            if torch.backends.mps.is_available():
                self._device = torch.device("mps")
            elif torch.cuda.is_available():
                self._device = torch.device("cuda")
            else:
                self._device = torch.device("cpu")

            self._model = backbone.to(self._device)
            self._torch = torch

            # Standard ImageNet preprocessing pipeline
            self._preprocess = transforms.Compose([
                transforms.Resize((_INPUT_SIZE, _INPUT_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
            ])

            logger.info(f"Classifier loaded on device={self._device}: {self._model_version}")

        except ImportError as exc:
            raise RuntimeError(
                "torch/torchvision required. Install with: "
                "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
            ) from exc

    def _crop_region(self, image_bgr, bbox: dict):
        """Crop the bounding-box region from a full frame (normalised coords)."""
        h, w = image_bgr.shape[:2]
        x_c, y_c = bbox["x"] * w, bbox["y"] * h
        bw, bh   = bbox["w"] * w, bbox["h"] * h
        x1 = max(0, int(x_c - bw / 2))
        y1 = max(0, int(y_c - bh / 2))
        x2 = min(w, int(x_c + bw / 2))
        y2 = min(h, int(y_c + bh / 2))
        crop = image_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            crop = image_bgr  # fallback to full frame
        return crop

    def _bgr_crop_to_tensor(self, crop_bgr):
        """Convert OpenCV BGR crop to a preprocessed tensor ready for the model."""
        import cv2
        from PIL import Image as PILImage
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil_img = PILImage.fromarray(rgb)
        return self._preprocess(pil_img).unsqueeze(0).to(self._device)

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def classify(self, image_path: str, bbox: dict) -> ClassificationResult:
        """
        Classify the disease within a single bounding-box region.

        Args:
            image_path: Absolute path to the frame JPEG.
            bbox: Normalised bounding box {"x", "y", "w", "h"} in [0, 1].

        Returns:
            ClassificationResult with full probability_distribution dict and
            mandatory classifier_model_version stamp.
        """
        self._load_model()

        import cv2
        bgr = cv2.imread(image_path)
        if bgr is None:
            raise FileNotFoundError(f"Cannot read image for classification: {image_path}")

        crop = self._crop_region(bgr, bbox)
        tensor = self._bgr_crop_to_tensor(crop)

        with self._torch.no_grad():
            logits = self._model(tensor)            # [1, NUM_CLASSES]
            probs  = self._torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

        # Build full probability distribution dict (always all classes)
        prob_dist: dict[str, float] = {
            cls: float(round(float(probs[i]), 6))
            for i, cls in enumerate(TAXONOMY_CLASSES)
        }

        top_idx = int(np.argmax(probs))
        top_class = TAXONOMY_CLASSES[top_idx]
        top_conf  = float(probs[top_idx])

        # OOD routing: unknown_other dominates OR max non-unknown conf too low
        unknown_prob = prob_dist.get("unknown_other", 0.0)
        max_known_conf = max(
            v for k, v in prob_dist.items() if k != "unknown_other"
        )
        is_unknown = (
            unknown_prob >= self._ood_unknown_threshold
            or max_known_conf < self._ood_max_conf_floor
        )

        return ClassificationResult(
            frame_path=image_path,
            detection_bbox=bbox,
            probability_distribution=prob_dist,
            top_class=top_class if not is_unknown else "unknown_other",
            top_confidence=top_conf,
            is_unknown=is_unknown,
            classifier_model_version=self._model_version,
        )

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def taxonomy_classes(self) -> list[str]:
        return list(TAXONOMY_CLASSES)

    @property
    def taxonomy_version(self) -> str:
        return TAXONOMY_VERSION
