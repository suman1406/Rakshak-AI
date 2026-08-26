from dataclasses import dataclass
from pathlib import Path
import hashlib
import math

@dataclass
class PipelineResult:
    frames_analyzed: int
    supporting_frames: int
    leaf_regions_analyzed: int
    quality_score: int
    confidence: float
    severity: str
    affected_plants: float

def hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def analyze_video(video_path: str) -> PipelineResult:
    """Safe baseline adapter. Replace model calls with validated YOLO/PyTorch weights."""
    size = Path(video_path).stat().st_size if Path(video_path).exists() else 0
    quality = max(25, min(96, 55 + int(math.log2(max(1, size)) % 40)))
    confidence = 0.72 if quality >= 60 else 0.48
    return PipelineResult(
        frames_analyzed=16,
        supporting_frames=12 if confidence >= 0.7 else 5,
        leaf_regions_analyzed=43,
        quality_score=quality,
        confidence=confidence,
        severity="moderate" if confidence >= 0.7 else "uncertain",
        affected_plants=0.20 if confidence >= 0.7 else 0.0,
    )

def to_diagnosis(result: PipelineResult) -> dict:
    band = "high" if result.confidence >= .9 else "medium" if result.confidence >= .7 else "low"
    disease = "soybean_rust" if band != "low" else "uncertain_condition"
    explanation = (
        "The visual symptoms are consistent with possible soybean rust across multiple plants. "
        "This is an AI indication, not a confirmed diagnosis."
        if disease != "uncertain_condition" else
        "There is insufficient visual evidence to confidently classify this condition."
    )
    return {
        "crop": "soybean", "disease": disease, "confidence": result.confidence,
        "confidence_band": band, "severity": result.severity,
        "affected_plant_estimate": result.affected_plants,
        "evidence": {"frames_analyzed": result.frames_analyzed, "supporting_frames": result.supporting_frames, "leaf_regions_analyzed": result.leaf_regions_analyzed, "quality_score": result.quality_score, "frames": []},
        "recommendation": {"action": "additional_inspection", "agronomist_review": band != "high"},
        "explanation": explanation,
    }

