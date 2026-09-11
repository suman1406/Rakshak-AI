import pytest

from app.modules.aggregation.bayes import BayesianAggregator
from app.modules.inference.classifier import TAXONOMY_CLASSES
from app.modules.inference.service import FrameInferenceResult


def frame(disease="soybean_rust", probability=.65):
    distribution = {name: (1 - probability) / 4 for name in TAXONOMY_CLASSES}
    distribution[disease] = probability
    return FrameInferenceResult("frame", "path", 100, 1, disease, probability, False, distribution)


def test_repeated_weak_predictions_cannot_become_high_confidence():
    result = BayesianAggregator().aggregate([frame() for _ in range(20)])
    assert result.top_confidence == pytest.approx(.65)
    assert result.is_unknown


def test_supporting_frames_only_count_winning_disease():
    result = BayesianAggregator().aggregate([frame(probability=.95)] * 5 + [frame("soybean_healthy", .95)])
    assert result.supporting_frames == 5
    assert result.total_frames == 6
    assert result.top_confidence < .95


def test_unknown_observations_are_not_discarded_to_inflate_certainty():
    unknown = frame("unknown_other", .99)
    unknown.is_unknown = True
    result = BayesianAggregator().aggregate([frame(probability=.95)] + [unknown] * 5)
    assert result.is_unknown


def test_background_objects_are_not_leaf_evidence():
    import torch
    from unittest.mock import MagicMock
    from app.modules.inference.detector import PlantDetector
    result = MagicMock()
    result.boxes.xywhn = torch.tensor([[.5, .5, .8, .8]])
    result.boxes.conf = torch.tensor([.99])
    result.boxes.cls = torch.tensor([0])
    result.names = {0: "person"}
    detector = PlantDetector()
    detector._model = MagicMock(return_value=[result])
    assert detector.detect("person.jpg") == []
