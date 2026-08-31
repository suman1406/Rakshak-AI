"""Canonical, conservative serialization helpers for persisted scan results."""

from __future__ import annotations

import re

from app.models.prediction import VideoDiagnosis


def disease_slug(diagnosis: VideoDiagnosis) -> str:
    """Return a user-facing taxonomy slug without ever exposing a database ID."""
    if diagnosis.is_unknown or diagnosis.disease is None:
        return "unknown_other"
    return re.sub(r"[^a-z0-9]+", "_", diagnosis.disease.name.lower()).strip("_") or "unknown_other"


def result_state(diagnosis: VideoDiagnosis) -> str:
    if diagnosis.is_unknown or diagnosis.disease is None:
        return "unknown"
    if disease_slug(diagnosis) == "healthy":
        return "healthy"
    return "ready"


def severity_name(level: int | None) -> str:
    return {0: "None", 1: "Mild", 2: "Moderate", 3: "Severe"}.get(level or 0, "None")
