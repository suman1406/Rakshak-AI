"""
severity.py — Severity Estimation Heuristic

Calculates severity level (0=None, 1=Mild, 2=Moderate, 3=Severe) and affected
plant coverage estimate based on diseased frame ratio and detection density.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
from ..inference.service import FrameInferenceResult

@dataclass
class SeverityAssessment:
    severity_level: int              # 0 to 3
    severity_name: str               # "None", "Mild", "Moderate", "Severe"
    affected_plant_estimate: float   # 0.0 to 1.0


class SeverityEstimator:
    def estimate(
        self,
        frame_results: Sequence[FrameInferenceResult],
        is_unknown: bool,
    ) -> SeverityAssessment:
        if is_unknown or not frame_results:
            return SeverityAssessment(
                severity_level=0,
                severity_name="None",
                affected_plant_estimate=0.0,
            )

        total_frames = len(frame_results)
        diseased_frames = [
            fr for fr in frame_results
            if not fr.is_unknown and fr.top_class not in ("healthy", "unknown_other")
        ]
        ratio = len(diseased_frames) / total_frames if total_frames > 0 else 0.0

        if ratio >= 0.70:
            level = 3
            name = "Severe"
            estimate = round(min(ratio * 0.95, 0.95), 2)
        elif ratio >= 0.40:
            level = 2
            name = "Moderate"
            estimate = round(ratio * 0.75, 2)
        elif ratio >= 0.15:
            level = 1
            name = "Mild"
            estimate = round(ratio * 0.50, 2)
        else:
            level = 0
            name = "None"
            estimate = 0.0

        return SeverityAssessment(
            severity_level=level,
            severity_name=name,
            affected_plant_estimate=estimate,
        )
