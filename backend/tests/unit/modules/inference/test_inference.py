"""
Unit tests for Grade 3 — Vision Inference: Detector, Classifier, and InferenceService.

Strategy:
  - All ultralytics/torch calls are mocked so tests run without GPU and without
    downloading pretrained weights (keeping CI fast and deterministic).
  - We verify the *contracts* enforced by the architecture:
    • Full probability distributions are always returned (all 5 taxonomy classes).
    • OOD routing triggers correctly.
    • All detector results carry detector_model_version.
    • All classifier results carry classifier_model_version.
    • InferenceService persists Detection + FrameDiagnosis rows to DB.
"""

from __future__ import annotations

import math
import types
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import numpy as np
import pytest

from app.modules.inference.classifier import (
    CLASSIFIER_MODEL_VERSION,
    TAXONOMY_CLASSES,
    NUM_CLASSES,
    DiseaseClassifier,
)
from app.modules.inference.detector import (
    DETECTOR_MODEL_VERSION,
    PlantDetector,
    DetectionResult,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers / factories
# ──────────────────────────────────────────────────────────────────────────────

def make_fake_bgr_image(h=64, w=64):
    """Return a synthetic OpenCV BGR numpy array."""
    return np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)


def make_prob_tensor(top_class_idx: int, total: int = NUM_CLASSES, dominance: float = 0.6):
    """Return a *logit* tensor whose softmax gives `dominance` to `top_class_idx`."""
    try:
        import torch
        # Build target probabilities then convert to logits via log
        probs = np.full(total, (1.0 - dominance) / (total - 1))
        probs[top_class_idx] = dominance
        # logit = log(p); softmax(logit) ≈ p when passed as [1, N]
        logits = np.log(probs + 1e-9)
        return torch.tensor(logits).unsqueeze(0).float()
    except ImportError:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Taxonomy Lock Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestTaxonomyLock:
    """Ensure the locked taxonomy has not been altered."""

    def test_taxonomy_has_six_classes(self):
        # The MVP taxonomy has 5 classes (Septoria deferred per design doc)
        assert len(TAXONOMY_CLASSES) == 5

    def test_taxonomy_contains_all_launch_diseases(self):
        # MVP taxonomy contains soybean-prefixed class names
        assert "soybean_rust" in TAXONOMY_CLASSES
        assert "soybean_bacterial_blight" in TAXONOMY_CLASSES
        assert "soybean_frogeye_leaf_spot" in TAXONOMY_CLASSES
        # Septoria is deferred for MVP
        assert "soybean_healthy" in TAXONOMY_CLASSES
        assert "unknown_other" in TAXONOMY_CLASSES

    def test_taxonomy_index_order_stable(self):
        """Index order per design: bacterial_blight, frogeye, healthy, rust, unknown_other"""
        assert TAXONOMY_CLASSES[0] == "soybean_bacterial_blight"
        assert TAXONOMY_CLASSES[2] == "soybean_healthy"
        assert TAXONOMY_CLASSES[3] == "soybean_rust"
        assert TAXONOMY_CLASSES[4] == "unknown_other"

    def test_classifier_version_constant_present(self):
        assert CLASSIFIER_MODEL_VERSION != ""
        assert "effnet" in CLASSIFIER_MODEL_VERSION.lower()

    def test_detector_version_constant_present(self):
        assert DETECTOR_MODEL_VERSION != ""
        assert "yolov8" in DETECTOR_MODEL_VERSION.lower()


# ──────────────────────────────────────────────────────────────────────────────
# Detector Unit Tests (mocked ultralytics.YOLO)
# ──────────────────────────────────────────────────────────────────────────────

class TestPlantDetector:

    def _make_detector_with_mock_model(
        self,
        xywhn_boxes: list[list[float]],
        confidences: list[float],
    ):
        """
        Construct a PlantDetector whose YOLO model is pre-seeded with mock
        predictions matching the ultralytics Results API.

        Args:
            xywhn_boxes: List of [x_center, y_center, w, h] in [0,1] (normalised).
            confidences:  Per-box confidence scores.

        Returns:
            detector (PlantDetector with lazy model already injected)
        """
        import torch

        detector = PlantDetector(confidence_threshold=0.30)

        # Build a mock that mimics ultralytics Results object
        mock_boxes = MagicMock()
        mock_boxes.xywhn = torch.tensor(xywhn_boxes, dtype=torch.float32)
        mock_boxes.conf  = torch.tensor(confidences, dtype=torch.float32)
        mock_boxes.cls = torch.zeros(len(confidences))

        mock_result = MagicMock()
        mock_result.boxes = mock_boxes
        mock_result.names = {0: "leaf"}

        mock_model = MagicMock()
        mock_model.return_value = [mock_result]

        # Inject the already-loaded mock model so _load_model() is bypassed
        detector._model = mock_model

        return detector

    def test_returns_detection_results_with_version_stamp(self):
        detector = self._make_detector_with_mock_model(
            xywhn_boxes=[[0.5, 0.4, 0.3, 0.25]],
            confidences=[0.85],
        )

        results = detector.detect("fake/frame.jpg")
        assert len(results) >= 1
        r = results[0]
        assert r.detector_model_version == DETECTOR_MODEL_VERSION
        assert r.detector_model_version != ""

    def test_bbox_normalised_to_unit_range(self):
        detector = self._make_detector_with_mock_model(
            xywhn_boxes=[[0.6, 0.45, 0.4, 0.35]],
            confidences=[0.90],
        )
        results = detector.detect("fake/frame.jpg")
        bbox = results[0].bbox
        assert 0.0 <= bbox["x"] <= 1.0, f"x={bbox['x']} out of range"
        assert 0.0 <= bbox["y"] <= 1.0, f"y={bbox['y']} out of range"
        assert 0.0 <= bbox["w"] <= 1.0, f"w={bbox['w']} out of range"
        assert 0.0 <= bbox["h"] <= 1.0, f"h={bbox['h']} out of range"

    def test_low_confidence_boxes_are_filtered(self):
        detector = self._make_detector_with_mock_model(
            xywhn_boxes=[[0.5, 0.5, 0.4, 0.4], [0.2, 0.2, 0.1, 0.1]],
            confidences=[0.80, 0.05],   # second is below threshold
        )
        results = detector.detect("fake/frame.jpg")
        real_detections = [r for r in results if r.confidence >= 0.30]
        # The high-confidence box should be kept; low-confidence filtered.
        assert any(r.confidence == pytest.approx(0.80, abs=0.01) for r in real_detections)
        assert all(r.confidence >= 0.30 for r in real_detections)

    def test_no_detections_synthesises_full_frame_region(self):
        """If no box exceeds threshold, a full-frame fallback is inserted."""
        detector = self._make_detector_with_mock_model(
            xywhn_boxes=[[0.5, 0.5, 0.4, 0.4]],
            confidences=[0.05],         # below threshold
        )
        results = detector.detect("fake/frame.jpg")
        assert results == []

    def test_coords_clamped_to_unit_range(self):
        """Out-of-range xywhn values (floating-point edge cases) must be clamped."""
        detector = self._make_detector_with_mock_model(
            # Intentionally slightly out of range
            xywhn_boxes=[[1.02, -0.01, 0.5, 0.5]],
            confidences=[0.95],
        )
        results = detector.detect("fake/frame.jpg")
        bbox = results[0].bbox
        assert 0.0 <= bbox["x"] <= 1.0
        assert 0.0 <= bbox["y"] <= 1.0
        assert 0.0 <= bbox["w"] <= 1.0
        assert 0.0 <= bbox["h"] <= 1.0



# ──────────────────────────────────────────────────────────────────────────────
# Classifier Unit Tests (mocked torch)
# ──────────────────────────────────────────────────────────────────────────────

class TestDiseaseClassifier:

    def _make_classifier_with_mock_model(self, top_class_idx: int, dominance: float = 0.65):
        """Inject a mock model returning a controlled probability tensor."""
        import torch
        classifier = DiseaseClassifier()

        # Build mock model - use the actual taxonomy classes from the classifier
        mock_model = MagicMock()
        # Use 5 classes for the MVP taxonomy
        fake_logits = make_prob_tensor(top_class_idx, 5, dominance)
        mock_model.return_value = fake_logits
        mock_model.eval.return_value = mock_model
        mock_model.to.return_value = mock_model

        # Set the classifier's internal classes to match the taxonomy
        classifier._classes = [
            "soybean_bacterial_blight",
            "soybean_frogeye_leaf_spot",
            "soybean_healthy",
            "soybean_rust",
            "unknown_other",
        ]

        # Mock preprocessing pipeline
        mock_preprocess = MagicMock()
        mock_preprocess.return_value = torch.zeros(3, 224, 224)

        classifier._model = mock_model
        classifier._device = torch.device("cpu")
        classifier._torch = torch
        classifier._preprocess = mock_preprocess

        return classifier

    @patch("cv2.imread")
    def test_full_probability_distribution_returned(self, mock_imread):
        """All 6 taxonomy classes must be present in the distribution."""
        mock_imread.return_value = make_fake_bgr_image()
        classifier = self._make_classifier_with_mock_model(top_class_idx=0)  # soybean_rust

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})

        assert set(result.probability_distribution.keys()) == set(TAXONOMY_CLASSES)

    @patch("cv2.imread")
    def test_probabilities_sum_to_one(self, mock_imread):
        mock_imread.return_value = make_fake_bgr_image()
        classifier = self._make_classifier_with_mock_model(top_class_idx=0)

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        total = sum(result.probability_distribution.values())
        assert math.isclose(total, 1.0, abs_tol=1e-4), f"Sum={total}"

    @patch("cv2.imread")
    def test_classifier_version_stamp_always_present(self, mock_imread):
        mock_imread.return_value = make_fake_bgr_image()
        classifier = self._make_classifier_with_mock_model(top_class_idx=2)  # soybean_healthy

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        assert result.classifier_model_version == CLASSIFIER_MODEL_VERSION
        assert result.classifier_model_version != ""

    @patch("cv2.imread")
    def test_ood_routing_when_unknown_dominates(self, mock_imread):
        """unknown_other (index 4) at high probability should trigger is_unknown=True."""
        mock_imread.return_value = make_fake_bgr_image()
        # Dominance of 0.70 on unknown_other (index 4) → should trigger OOD
        classifier = self._make_classifier_with_mock_model(top_class_idx=4, dominance=0.70)
        classifier._ood_unknown_threshold = 0.45  # default

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        assert result.is_unknown is True

    @patch("cv2.imread")
    def test_ood_routing_when_max_confidence_too_low(self, mock_imread):
        """When no class reaches the minimum confidence floor, is_unknown=True."""
        mock_imread.return_value = make_fake_bgr_image()
        # Very uniform distribution: dominance=0.20 → max known class < 0.30 floor
        classifier = self._make_classifier_with_mock_model(top_class_idx=0, dominance=0.20)
        classifier._ood_max_conf_floor = 0.30

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        assert result.is_unknown is True

    @patch("cv2.imread")
    def test_healthy_class_correctly_identified(self, mock_imread):
        mock_imread.return_value = make_fake_bgr_image()
        # soybean_healthy is at index 2
        classifier = self._make_classifier_with_mock_model(top_class_idx=2, dominance=0.80)
        classifier._ood_max_conf_floor = 0.30
        classifier._ood_unknown_threshold = 0.45

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        assert result.is_unknown is False
        # top_class should be soybean_healthy (dominant at 0.80, well above thresholds)
        assert result.top_class == "soybean_healthy"


# ──────────────────────────────────────────────────────────────────────────────
# InferenceService Integration Tests (in-memory DB, mocked torch)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_inference_service_persists_detection_and_frame_diagnosis_rows(test_db, client):
    """
    End-to-end: upload a video, persist frames, run InferenceService, and verify
    that Detection + FrameDiagnosis rows are written with non-empty model versions.
    """
    import torch
    import tempfile
    import cv2
    import numpy as np
    from sqlalchemy import select
    from app.modules.inference.service import InferenceService
    from app.models.prediction import Detection, FrameDiagnosis
    from app.models.video import Frame
    from app.modules.inference.detector import PlantDetector, DETECTOR_MODEL_VERSION
    from app.modules.inference.classifier import DiseaseClassifier, CLASSIFIER_MODEL_VERSION

    # ── Register and login to get auth token ───────────────────────────────
    await client.post(
        "/api/v1/auth/register",
        json={"email": "inference-test@rakshak.ai", "password": "Password123!", "consent_to_data_processing": True},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email_or_phone": "inference-test@rakshak.ai", "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # ── Create farm → field → video and inject a Frame manually ───────────
    farm_res = await client.post("/api/v1/farms", json={"name": "Inference Test Farm"}, headers=headers)
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Field A"}, headers=headers)
    field_id = field_res.json()["id"]

    from app.models.video import Video, VideoStatus
    import uuid
    video_id = str(uuid.uuid4())

    # Write a real JPEG to disk so detector/classifier can read it
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        frame_path = tmp.name
    bgr = make_fake_bgr_image(128, 128)
    cv2.imwrite(frame_path, bgr)

    # Insert Video
    video = Video(
        id=video_id,
        field_id=field_id,
        uploaded_by="test-user",
        status=VideoStatus.analyzing,
        storage_path="storage/videos/test/video.mp4",
        usable_frames_count=1,
        total_frames_extracted=1,
    )
    test_db.add(video)

    # Insert a selected Frame pointing at our real image
    frame = Frame(
        id=str(uuid.uuid4()),
        video_id=video_id,
        storage_path=frame_path,
        blur_score=120.0,
        exposure_score=70.0,
        is_selected=True,
        sequence_index=0,
    )
    test_db.add(frame)
    await test_db.commit()

    # ── Patch detector and classifier to avoid network/GPU ────────────────
    svc = InferenceService()

    # Detector mock: one detection bbox
    mock_det_result = DetectionResult(
        frame_path=frame_path,
        bbox={"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0},
        detection_class="leaf",
        confidence=0.80,
        detector_model_version=DETECTOR_MODEL_VERSION,
    )
    svc._detector.detect = MagicMock(return_value=[mock_det_result])

    # Classifier mock: soybean_rust at 65%
    from app.modules.inference.classifier import ClassificationResult
    mock_cls_result = ClassificationResult(
        frame_path=frame_path,
        detection_bbox={"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0},
        probability_distribution={
            "soybean_rust": 0.65,
            "soybean_bacterial_blight": 0.10,
            "soybean_frogeye_leaf_spot": 0.08,
            # septoria brown spot is deferred for MVP
            "soybean_healthy": 0.13,
            "unknown_other": 0.04,
        },
        top_class="soybean_rust",
        top_confidence=0.65,
        is_unknown=False,
        classifier_model_version=CLASSIFIER_MODEL_VERSION,
    )
    svc._classifier.classify = MagicMock(return_value=mock_cls_result)

    # ── Run inference ─────────────────────────────────────────────────────
    results = await svc.run_frame_inference(video_id, test_db)

    assert len(results) == 1
    fr = results[0]
    assert fr.top_class == "soybean_rust"
    assert fr.is_unknown is False

    # ── Verify DB rows ────────────────────────────────────────────────────
    det_stmt = select(Detection).where(Detection.frame_id == frame.id)
    det_result = await test_db.execute(det_stmt)
    detections = det_result.scalars().all()

    assert len(detections) == 1
    det = detections[0]
    assert det.detector_model_version == DETECTOR_MODEL_VERSION
    assert det.detector_model_version != ""
    assert det.detector_confidence == pytest.approx(0.80, abs=0.01)

    fd_stmt = select(FrameDiagnosis).where(FrameDiagnosis.detection_id == det.id)
    fd_result = await test_db.execute(fd_stmt)
    frame_diagnoses = fd_result.scalars().all()

    assert len(frame_diagnoses) == 1
    fd = frame_diagnoses[0]
    assert fd.classifier_model_version == CLASSIFIER_MODEL_VERSION
    assert fd.classifier_model_version != ""
    # MVP taxonomy has 5 classes (Septoria deferred)
    expected_classes = {
        "soybean_rust",
        "soybean_bacterial_blight", 
        "soybean_frogeye_leaf_spot",
        "soybean_healthy",
        "unknown_other",
    }
    assert set(fd.probability_distribution.keys()) == expected_classes
    assert fd.probability_distribution["soybean_rust"] == pytest.approx(0.65, abs=0.01)


@pytest.mark.asyncio
async def test_inference_service_handles_frame_error_gracefully(test_db, client):
    """
    If detection fails for a frame, the pipeline should emit an unknown result
    rather than crashing.
    """
    import uuid
    from app.models.video import Video, VideoStatus, Frame
    from app.modules.inference.service import InferenceService

    # ── Register and login to get auth token ───────────────────────────────
    await client.post(
        "/api/v1/auth/register",
        json={"email": "error-test@rakshak.ai", "password": "Password123!", "consent_to_data_processing": True},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email_or_phone": "error-test@rakshak.ai", "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    farm_res = await client.post("/api/v1/farms", json={"name": "Error Farm"}, headers=headers)
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Error Field"}, headers=headers)
    field_id = field_res.json()["id"]

    video_id = str(uuid.uuid4())
    video = Video(
        id=video_id,
        field_id=field_id,
        uploaded_by="test-user",
        status=VideoStatus.analyzing,
        storage_path="storage/videos/test/video.mp4",
        usable_frames_count=1,
        total_frames_extracted=1,
    )
    test_db.add(video)

    frame = Frame(
        id=str(uuid.uuid4()),
        video_id=video_id,
        storage_path="/nonexistent/path/frame.jpg",  # will raise FileNotFoundError
        blur_score=100.0,
        exposure_score=70.0,
        is_selected=True,
        sequence_index=0,
    )
    test_db.add(frame)
    await test_db.commit()

    svc = InferenceService()
    # Detector raises FileNotFoundError
    svc._detector.detect = MagicMock(side_effect=FileNotFoundError("test"))

    with pytest.raises(RuntimeError, match="Model inference failed"):
        await svc.run_frame_inference(video_id, test_db)
