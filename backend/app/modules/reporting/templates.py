"""
templates.py — Deterministic Canned Report Fallback Templates

Guarantees high-quality, honest farmer reports even when LLM generation fails
or is rejected by guardrails.
"""

from __future__ import annotations

CANNED_REPORTS: dict[str, dict[str, str]] = {
    "soybean_rust": {
        "headline": "Possible Soybean Rust Visual Symptoms Detected",
        "explanation": (
            "Visual evidence indicates symptoms consistent with soybean rust on inspected leaves. "
            "This is an AI estimate, not a confirmed diagnosis. Inspect your field manually or consult an agronomist."
        ),
        "action_items": (
            "1. Inspect undersides of lower canopy leaves for reddish-brown pustules.\n"
            "2. Avoid overhead irrigation to minimize leaf wetness duration.\n"
            "3. Consult a local agricultural extension officer for approved fungicide guidance."
        ),
    },
    "bacterial_blight": {
        "headline": "Possible Bacterial Blight Symptoms Observed",
        "explanation": (
            "Small angular water-soaked lesions observed on leaves. "
            "This is an AI estimate, not a confirmed diagnosis. Verify with an agronomist."
        ),
        "action_items": (
            "1. Avoid field cultivation while foliage is wet to prevent bacterial spread.\n"
            "2. Monitor upper canopy for yellow haloing around angular spots.\n"
            "3. Ensure crop rotation with non-host crops in subsequent seasons."
        ),
    },
    "frogeye_leaf_spot": {
        "headline": "Possible Frogeye Leaf Spot Detected",
        "explanation": (
            "Circular to angular spots with dark reddish-brown borders detected. "
            "This is an AI estimate, not a confirmed diagnosis. Consult an agronomist for field confirmation."
        ),
        "action_items": (
            "1. Inspect middle to upper leaf canopy for lesions with grey centers.\n"
            "2. Utilize certified disease-free soybean seed stock.\n"
            "3. Consider resistant varieties for future planting."
        ),
    },
    "septoria_brown_spot": {
        "headline": "Possible Septoria Brown Spot Observed",
        "explanation": (
            "Irregular brown spots detected on lower leaves. "
            "This is an AI estimate, not a confirmed diagnosis. Inspect lower canopy."
        ),
        "action_items": (
            "1. Check for early defoliation in the lower canopy.\n"
            "2. Manage crop residue post-harvest.\n"
            "3. Practice 1-2 year crop rotation with corn or grass crops."
        ),
    },
    "healthy": {
        "headline": "Soybean Foliage Appears Healthy",
        "explanation": (
            "No significant visual leaf disease symptoms detected in inspected frames. "
            "This is an AI estimate, not a confirmed diagnosis. Continue routine field scouting."
        ),
        "action_items": (
            "1. Maintain regular weekly field inspection schedule.\n"
            "2. Monitor for pests or soil nutrient deficiencies.\n"
            "3. Maintain proper field drainage."
        ),
    },
    "unknown_other": {
        "headline": "Unable to Confidently Classify Disease",
        "explanation": (
            "Visual evidence is insufficient or symptoms do not match known launch disease profiles. "
            "This is an AI indication, not a confirmed diagnosis. Please consult an agronomist for a manual inspection."
        ),
        "action_items": (
            "1. Retake video with clear lighting and steady camera movement.\n"
            "2. Ensure close-up footage of affected leaf surfaces.\n"
            "3. Invite a certified agronomist for physical field inspection."
        ),
    },
}

def get_canned_report(disease_slug: str) -> dict[str, str]:
    return CANNED_REPORTS.get(disease_slug, CANNED_REPORTS["unknown_other"])
