"""
classifier.py — Soybean Disease Classifier

Design goals:
  - Launch-locked disease taxonomy, loaded from classes.json bundled with the
    model weights — never hardcoded and trusted blind. Startup asserts the
    manifest matches the model's output dimension (fail loud, not lazy).
  - Always outputs the *full probability distribution* over all classes, not
    just top-1. This is stored in `frame_diagnoses.probability_distribution`.
  - Real fine-tuned weights (EfficientNet-B0 via timm), trained on ASDID
    (Auburn Soybean Disease Image Dataset), single-source MVP.
  - Post-hoc temperature scaling applied at inference (see calibration.json).
  - Lazy-loaded model to keep test collection fast.

Taxonomy (locked, v1.1-mvp5):
  MVP taxonomy excludes soybean_septoria_brown_spot — no volume source was
  available at MVP scope (ASDID doesn't include it). Adding it back is a
  Rule 5 append-only change: new class appended at the next index, model
  retrained with an expanded output layer (warm-start old class weights,
  random-init the new row), and BOTH CLASSIFIER_MODEL_VERSION and
  TAXONOMY_VERSION bumped together. Never insert mid-list, never silently
  re-add without a version bump.

  Actual class order is NOT hardcoded here — it's loaded from classes.json
  at model-load time and asserted to match the model's output dimension.
  The list below is documentation of what's *expected*, not the source of
  truth:
    0 → soybean_bacterial_blight
    1 → soybean_frogeye_leaf_spot
    2 → soybean_healthy
    3 → soybean_rust
    4 → unknown_other
"""

from __future__ import annotations

import json
import logging
import pathlib
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger("rakshak")

# ──────────────────────────────────────────────────────────────────────────────
# Locked taxonomy (v1.1-mvp5 — Septoria deferred, see module docstring)
# ──────────────────────────────────────────────────────────────────────────────
CLASSIFIER_MODEL_VERSION = "effnet-b0-soybean-asdid-v1.1-mvp5"
TAXONOMY_VERSION = "v1.1-mvp5"

# Documentation only — actual order comes from classes.json at load time.
EXPECTED_TAXONOMY_CLASSES: list[str] = [
    "soybean_bacterial_blight",
    "soybean_frogeye_leaf_spot",
    "soybean_healthy",
    "soybean_rust",
    "unknown_other",
]

# Module-level taxonomy classes for use before model is loaded.
# This is the fallback when classes.json can't be read (e.g., in tests).
# The actual classes are loaded at runtime from classes.json when the model loads.
TAXONOMY_CLASSES = EXPECTED_TAXONOMY_CLASSES

# Number of classes in the taxonomy
NUM_CLASSES = len(EXPECTED_TAXONOMY_CLASSES)

WEIGHTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "weights"  # backend/app/weights
WEIGHTS_PATH = WEIGHTS_DIR / "soybean_classifier_effnet_b0.pt"
CLASSES_PATH = WEIGHTS_DIR / "classes.json"
CALIBRATION_PATH = WEIGHTS_DIR / "calibration.json"

# OOD routing thresholds — inherited from the original scaffold, NOT yet
# re-validated or tuned against this real model. Revisit as a follow-up pass
# before relying on these for production certainty guardrails.
OOD_UNKNOWN_THRESHOLD = 0.45
OOD_MAX_CONFIDENCE_FLOOR = 0.30

# ImageNet normalisation (standard for pretrained torchvision/timm models)
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
    taxonomy_version: str = TAXONOMY_VERSION


class DiseaseClassifier:
    """
    Wraps a timm EfficientNet-B0 backbone fine-tuned on ASDID for soybean
    disease classification over the locked 5-class MVP taxonomy.

    Class order and count are loaded from classes.json bundled next to the
    weights, not hardcoded — startup fails loud if the manifest doesn't match
    the model's actual output dimension (Rule 6 of the taxonomy governance
    doc), rather than silently misreading indices at inference time.
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
        self._classes: list[str] = []
        self._temperature: float = 1.0

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _load_model(self):
        """Lazy-load the fine-tuned EfficientNet-B0 + bundled manifest."""
        if self._model is not None:
            return

        try:
            import torch
            import timm
            from torchvision import transforms

            if not WEIGHTS_PATH.exists():
                raise FileNotFoundError(
                    f"Trained weights not found at {WEIGHTS_PATH}. "
                    "Copy soybean_classifier_effnet_b0.pt into backend/app/weights/."
                )
            if not CLASSES_PATH.exists():
                raise FileNotFoundError(
                    f"classes.json not found at {CLASSES_PATH}. "
                    "Copy it alongside the weights file."
                )

            classes = json.load(open(CLASSES_PATH))

            # Device selection (MPS → CUDA → CPU)
            if torch.backends.mps.is_available():
                device = torch.device("mps")
            elif torch.cuda.is_available():
                device = torch.device("cuda")
            else:
                device = torch.device("cpu")

            model = timm.create_model(
                "efficientnet_b0", pretrained=False, num_classes=len(classes)
            )
            state_dict = torch.load(WEIGHTS_PATH, map_location=device)
            model.load_state_dict(state_dict)
            model.eval()
            model = model.to(device)

            # Rule 6 — fail loud at load time, not lazily on the first weird prediction.
            expected_dim = model.get_classifier().out_features
            assert len(classes) == expected_dim, (
                f"classes.json has {len(classes)} entries but the loaded model "
                f"outputs {expected_dim} classes — taxonomy/model mismatch. Refusing to serve."
            )
            assert "unknown_other" in classes, (
                "classes.json is missing the 'unknown_other' sentinel class."
            )

            # Calibration (optional — defaults to no-op if file is missing)
            temperature = 1.0
            if CALIBRATION_PATH.exists():
                calib = json.load(open(CALIBRATION_PATH))
                temperature = float(calib.get("temperature", 1.0))
            self._temperature = temperature

            self._device = device
            self._model = model
            self._torch = torch
            self._classes = classes

            self._preprocess = transforms.Compose([
                transforms.Resize((_INPUT_SIZE, _INPUT_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
            ])

            logger.info(
                f"Classifier loaded on device={self._device}: {self._model_version} "
                f"| taxonomy_version={TAXONOMY_VERSION} | classes={self._classes} "
                f"| temperature={self._temperature}"
            )

        except ImportError as exc:
            raise RuntimeError(
                "torch/torchvision/timm required. Install with: "
                "pip install torch torchvision timm --index-url https://download.pytorch.org/whl/cpu"
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
            mandatory classifier_model_version / taxonomy_version stamps.
        """
        self._load_model()

        import cv2
        bgr = cv2.imread(image_path)
        if bgr is None:
            raise FileNotFoundError(f"Cannot read image for classification: {image_path}")

        crop = self._crop_region(bgr, bbox)
        tensor = self._bgr_crop_to_tensor(crop)

        with self._torch.no_grad():
            logits = self._model(tensor)                          # [1, NUM_CLASSES]
            scaled_logits = logits / self._temperature             # calibration (no-op if T=1.0)
            probs = self._torch.softmax(scaled_logits, dim=1).squeeze(0).cpu().numpy()

        # Build full probability distribution dict (always all classes, in
        # the exact order loaded from classes.json — never re-derived).
        prob_dist: dict[str, float] = {
            cls: float(round(float(probs[i]), 6))
            for i, cls in enumerate(self._classes)
        }

        top_idx = int(np.argmax(probs))
        top_class = self._classes[top_idx]
        top_conf  = float(probs[top_idx])

        # OOD routing — thresholds inherited as-is, not yet re-tuned (see
        # module-level note above this is a deferred follow-up pass).
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
            taxonomy_version=TAXONOMY_VERSION,
        )

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def taxonomy_classes(self) -> list[str]:
        self._load_model()
        return list(self._classes)

    @property
    def taxonomy_version(self) -> str:
        return TAXONOMY_VERSION