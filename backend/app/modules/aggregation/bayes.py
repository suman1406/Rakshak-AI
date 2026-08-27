"""
bayes.py — Bayesian Temporal Aggregation

Combines multi-frame detection and classification probabilities into a single
posterior probability distribution over the locked launch disease taxonomy.

Formula:
  w_i = (blur_score / 100.0) * detector_confidence
  log_odds(c) = sum(w_i * log(p_{i,c} / (1 - p_{i,c})))
  posterior(c) = softmax(log_odds(c))
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence
import numpy as np

from ..inference.classifier import TAXONOMY_CLASSES, NUM_CLASSES
from ..inference.service import FrameInferenceResult

AGGREGATION_MODEL_VERSION = "bayes-v1.0"

@dataclass
class AggregatedDiagnosisResult:
    top_class: str
    top_confidence: float
    probability_distribution: dict[str, float]
    is_unknown: bool
    supporting_frames: int
    total_frames: int
    aggregation_model_version: str = AGGREGATION_MODEL_VERSION


class BayesianAggregator:
    def __init__(self, model_version: str = AGGREGATION_MODEL_VERSION):
        self.model_version = model_version

    def aggregate(self, frame_results: Sequence[FrameInferenceResult]) -> AggregatedDiagnosisResult:
        if not frame_results:
            n = len(TAXONOMY_CLASSES)
            uniform = {cls: round(1.0 / n, 6) for cls in TAXONOMY_CLASSES}
            return AggregatedDiagnosisResult(
                top_class="unknown_other",
                top_confidence=0.0,
                probability_distribution=uniform,
                is_unknown=True,
                supporting_frames=0,
                total_frames=0,
                aggregation_model_version=self.model_version,
            )

        # Filter out unknown/unusable frames
        valid_frames = [fr for fr in frame_results if not fr.is_unknown]
        total_frames = len(frame_results)
        supporting_frames = len(valid_frames)

        if not valid_frames:
            n = len(TAXONOMY_CLASSES)
            uniform = {cls: round(1.0 / n, 6) for cls in TAXONOMY_CLASSES}
            return AggregatedDiagnosisResult(
                top_class="unknown_other",
                top_confidence=0.0,
                probability_distribution=uniform,
                is_unknown=True,
                supporting_frames=0,
                total_frames=total_frames,
                aggregation_model_version=self.model_version,
            )

        # Compute log-odds sum per class
        log_odds_acc = {cls: 0.0 for cls in TAXONOMY_CLASSES}
        total_weight = 0.0

        for fr in valid_frames:
            # Quality-weighted frame confidence
            quality_factor = min(max(fr.quality_score / 100.0, 0.1), 1.0)
            weight = quality_factor * max(fr.top_confidence, 0.1)
            total_weight += weight

            for cls in TAXONOMY_CLASSES:
                prob = max(min(fr.avg_probability_distribution.get(cls, 0.01), 0.99), 0.01)
                log_odds_acc[cls] += weight * math.log(prob / (1.0 - prob))

        # Apply softmax to log-odds to obtain normalized posterior probabilities
        logits = np.array([log_odds_acc[cls] for cls in TAXONOMY_CLASSES], dtype=np.float64)
        exp_logits = np.exp(logits - np.max(logits))
        posteriors = exp_logits / np.sum(exp_logits)

        prob_dist = {
            cls: float(round(posteriors[i], 6))
            for i, cls in enumerate(TAXONOMY_CLASSES)
        }

        top_class = max(prob_dist, key=lambda k: prob_dist[k])
        top_conf = prob_dist[top_class]

        # OOD thresholding
        is_unknown = (
            top_class == "unknown_other"
            or top_conf < 0.30
            or prob_dist.get("unknown_other", 0.0) >= 0.45
        )

        return AggregatedDiagnosisResult(
            top_class=top_class if not is_unknown else "unknown_other",
            top_confidence=top_conf,
            probability_distribution=prob_dist,
            is_unknown=is_unknown,
            supporting_frames=supporting_frames,
            total_frames=total_frames,
            aggregation_model_version=self.model_version,
        )
