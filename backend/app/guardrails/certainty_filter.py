"""
certainty_filter.py — Guardrail Filter for LLM Explanations

Enforces standing invariant #3:
  - Rejects overconfident claims ("100% cure", "definitely", "guaranteed").
  - Rejects specific chemical dosage advice without advisory disclaimer.
  - Returns pass/fail status and violation list.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Prohibited overconfident phrases (patterns that should FAIL)
# Diseases/conditions that should trigger "confirmed {disease}" pattern
DISEASE_TERMS = r"(rust|blight|mildew|spot|rot|wilts?|(?:leaf|stem)(?:\s+)?spot|cancer|lesion)"

PROHIBITED_CERTAINTY_PATTERNS = [
    r"\b100%\b",
    r"\bdefinitely\b",
    r"\bguaranteed?\b",
    r"\bcured?\b",
    r"\bproven to eliminate\b",
    r"\bcomplete eradication\b",
    r"\balways works\b",
    r"\bno doubt\b",
    r"\bexact diagnosis\b",
    # Task required patterns
    r"definitely have\s+\w+",          # "definitely have {disease}"
    rf"confirmed\s+(?:that\s+)?{DISEASE_TERMS}",  # "confirmed {disease}"
    r"you definitely have",              # "you definitely have"
    r"prescribe.*pesticide",             # "prescribe.*pesticide"
    r"apply.*fertilizer.*dose",          # "apply.*fertilizer.*dose"
    r"use.*chemical.*amount",           # "use.*chemical.*amount"
    r"cure.*disease",                    # "cure.*disease"
    r"guaranteed.*treatment",            # "guaranteed.*treatment"
]

# Mandatory safety phrases (at least one must be present if a diagnosis is stated)
MANDATORY_DISCLAIMER_PATTERNS = [
    r"ai (estimate|indication|assessment)",
    r"not a confirmed diagnosis",
    r"consult (an|your) agronomist",
    r"inspect (the|your) field",
    r"advisory only",
]


@dataclass
class GuardrailResult:
    passed: bool
    violations: list[str] = field(default_factory=list)
    sanitized_text: str | None = None


class CertaintyGuardrailFilter:
    def evaluate(self, text: str) -> GuardrailResult:
        if not text:
            return GuardrailResult(passed=False, violations=["Empty text"])

        violations = []
        lower_text = text.lower()

        # Check prohibited overconfident words/phrases
        for pattern in PROHIBITED_CERTAINTY_PATTERNS:
            if re.search(pattern, lower_text):
                violations.append(f"Prohibited overconfident phrase match: '{pattern}'")

        # Check for presence of mandatory safety disclaimer
        has_disclaimer = any(
            re.search(pat, lower_text) for pat in MANDATORY_DISCLAIMER_PATTERNS
        )
        if not has_disclaimer:
            violations.append("Missing mandatory safety disclaimer copy")

        passed = len(violations) == 0
        return GuardrailResult(
            passed=passed,
            violations=violations,
            sanitized_text=text if passed else None,
        )
