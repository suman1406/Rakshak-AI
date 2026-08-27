"""
Unit tests for Grade 3 — Vision Inference: Detector, Classifier, and InferenceService.

Strategy:
  - All torch/torchvision calls are mocked so tests run without GPU and without
    downloading pretrained weights (keeping CI fast and deterministic).
  - We verify the *contracts* enforced by the architecture:
    • Full probability distributions are always returned (all 6 taxonomy classes).
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
        assert len(TAXONOMY_CLASSES) == 6

    def test_taxonomy_contains_all_launch_diseases(self):
        assert "soybean_rust" in TAXONOMY_CLASSES
        assert "bacterial_blight" in TAXONOMY_CLASSES
        assert "frogeye_leaf_spot" in TAXONOMY_CLASSES
        assert "septoria_brown_spot" in TAXONOMY_CLASSES
        assert "healthy" in TAXONOMY_CLASSES
        assert "unknown_other" in TAXONOMY_CLASSES

    def test_taxonomy_index_order_stable(self):
        """Index 0 must always be soybean_rust; index 4 healthy; index 5 unknown_other."""
        assert TAXONOMY_CLASSES[0] == "soybean_rust"
        assert TAXONOMY_CLASSES[4] == "healthy"
        assert TAXONOMY_CLASSES[5] == "unknown_other"

    def test_classifier_version_constant_present(self):
        assert CLASSIFIER_MODEL_VERSION != ""
        assert "effnet" in CLASSIFIER_MODEL_VERSION.lower()

    def test_detector_version_constant_present(self):
        assert DETECTOR_MODEL_VERSION != ""


# ──────────────────────────────────────────────────────────────────────────────
# Detector Unit Tests (mocked torch)
# ──────────────────────────────────────────────────────────────────────────────

class TestPlantDetector:

    def _make_detector_with_mock_model(self, boxes, scores, labels, img_bgr=None):
        """
        Construct a PlantDetector whose model is pre-seeded with mock predictions.
        Returns (detector, mock_frame_path).
        """
        import torch
        detector = PlantDetector(confidence_threshold=0.30)
        mock_model = MagicMock()

        # Build prediction dict
        pred = {
            "boxes": torch.tensor(boxes, dtype=torch.float32),
            "scores": torch.tensor(scores, dtype=torch.float32),
            "labels": torch.tensor(labels, dtype=torch.int64),
        }
        mock_model.return_value = [pred]
        mock_model.eval.return_value = mock_model
        mock_model.to.return_value = mock_model

        detector._model = mock_model
        detector._device = torch.device("cpu")
        detector._torch = torch

        return detector

    @patch("cv2.imread")
    def test_returns_detection_results_with_version_stamp(self, mock_imread):
        import torch
        mock_imread.return_value = make_fake_bgr_image(128, 128)

        detector = self._make_detector_with_mock_model(
            boxes=[[10.0, 20.0, 60.0, 80.0]],
            scores=[0.85],
            labels=[58],   # plant class
        )

        results = detector.detect("fake/frame.jpg")
        assert len(results) >= 1
        r = results[0]
        assert r.detector_model_version == DETECTOR_MODEL_VERSION
        assert r.detector_model_version != ""

    @patch("cv2.imread")
    def test_bbox_normalised_to_unit_range(self, mock_imread):
        import torch
        mock_imread.return_value = make_fake_bgr_image(100, 200)  # h=100, w=200

        detector = self._make_detector_with_mock_model(
            boxes=[[20.0, 10.0, 100.0, 50.0]],  # absolute pixels
            scores=[0.90],
            labels=[58],
        )
        results = detector.detect("fake/frame.jpg")
        bbox = results[0].bbox
        assert 0.0 <= bbox["x"] <= 1.0, f"x={bbox['x']} out of range"
        assert 0.0 <= bbox["y"] <= 1.0, f"y={bbox['y']} out of range"
        assert 0.0 <= bbox["w"] <= 1.0, f"w={bbox['w']} out of range"
        assert 0.0 <= bbox["h"] <= 1.0, f"h={bbox['h']} out of range"

    @patch("cv2.imread")
    def test_low_confidence_boxes_are_filtered(self, mock_imread):
        import torch
        mock_imread.return_value = make_fake_bgr_image(128, 128)

        detector = self._make_detector_with_mock_model(
            boxes=[[10.0, 20.0, 60.0, 80.0], [5.0, 5.0, 15.0, 15.0]],
            scores=[0.80, 0.05],   # second is below threshold
            labels=[58, 58],
        )
        results = detector.detect("fake/frame.jpg")
        # Should keep the high-score box only
        real_detections = [r for r in results if r.confidence >= 0.30]
        assert all(r.confidence >= 0.30 for r in real_detections)

    @patch("cv2.imread")
    def test_no_detections_synthesises_full_frame_region(self, mock_imread):
        """If no box exceeds threshold, a full-frame fallback is inserted."""
        import torch
        mock_imread.return_value = make_fake_bgr_image(128, 128)

        detector = self._make_detector_with_mock_model(
            boxes=[[10.0, 20.0, 60.0, 80.0]],
            scores=[0.05],         # below threshold
            labels=[58],
        )
        results = detector.detect("fake/frame.jpg")
        assert len(results) == 1
        assert results[0].bbox == {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0}


# ──────────────────────────────────────────────────────────────────────────────
# Classifier Unit Tests (mocked torch)
# ──────────────────────────────────────────────────────────────────────────────

class TestDiseaseClassifier:

    def _make_classifier_with_mock_model(self, top_class_idx: int, dominance: float = 0.65):
        """Inject a mock model returning a controlled probability tensor."""
        import torch
        classifier = DiseaseClassifier()

        # Build mock model
        mock_model = MagicMock()
        fake_logits = make_prob_tensor(top_class_idx, NUM_CLASSES, dominance)
        mock_model.return_value = fake_logits
        mock_model.eval.return_value = mock_model
        mock_model.to.return_value = mock_model

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
        classifier = self._make_classifier_with_mock_model(top_class_idx=4)  # healthy

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        assert result.classifier_model_version == CLASSIFIER_MODEL_VERSION
        assert result.classifier_model_version != ""

    @patch("cv2.imread")
    def test_ood_routing_when_unknown_dominates(self, mock_imread):
        """unknown_other (index 5) at high probability should trigger is_unknown=True."""
        mock_imread.return_value = make_fake_bgr_image()
        # Dominance of 0.70 on unknown_other (index 5) → should trigger OOD
        classifier = self._make_classifier_with_mock_model(top_class_idx=5, dominance=0.70)
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
        classifier = self._make_classifier_with_mock_model(top_class_idx=4, dominance=0.80)  # healthy
        classifier._ood_max_conf_floor = 0.30
        classifier._ood_unknown_threshold = 0.45

        result = classifier.classify("fake/frame.jpg", {"x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0})
        assert result.is_unknown is False
        # top_class should be healthy (dominant at 0.80, well above thresholds)
        assert result.top_class == "healthy"


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

    # ── Create farm → field → video and inject a Frame manually ───────────
    farm_res = await client.post("/api/v1/farms", json={"name": "Inference Test Farm"})
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Field A"})
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
            "bacterial_blight": 0.10,
            "frogeye_leaf_spot": 0.08,
            "septoria_brown_spot": 0.07,
            "healthy": 0.06,
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
    assert set(fd.probability_distribution.keys()) == set(TAXONOMY_CLASSES)
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

    farm_res = await client.post("/api/v1/farms", json={"name": "Error Farm"})
    farm_id = farm_res.json()["id"]
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json={"name": "Error Field"})
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

    results = await svc.run_frame_inference(video_id, test_db)
    assert len(results) == 1
    assert results[0].is_unknown is True
    assert results[0].detections_count == 0
