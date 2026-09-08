import pytest
from app.guardrails.certainty_filter import CertaintyGuardrailFilter


def test_guardrails_passes_clean_explanation_with_disclaimer():
    filter = CertaintyGuardrailFilter()
    explanation = "Visual inspection indicates possible symptoms of soybean rust on lower leaf canopy."
    disclaimer = "This is an AI estimate, not a confirmed diagnosis. Consult an agronomist before applying chemical treatments."
    combined = f"{explanation} {disclaimer}"
    
    res = filter.evaluate(combined)
    assert res.passed is True
    assert len(res.violations) == 0
    assert res.sanitized_text == combined


def test_guardrails_rejects_missing_disclaimer():
    filter = CertaintyGuardrailFilter()
    text = "Visual inspection indicates potential symptoms of frogeye leaf spot on leaves."
    res = filter.evaluate(text)
    assert res.passed is False
    assert any("safety disclaimer" in v.lower() for v in res.violations)


def test_guardrails_rejects_prohibited_certainty_claims():
    filter = CertaintyGuardrailFilter()
    disclaimer = "AI estimate, not a confirmed diagnosis. Consult an agronomist."
    
    prohibited_texts = [
        f"This fungicide offers a 100% cure for leaf spot. {disclaimer}",
        f"You definitely have soybean rust in your field. {disclaimer}",
        f"This treatment is guaranteed to eliminate the fungus. {disclaimer}",
        f"There is no doubt this is bacterial blight. {disclaimer}",
        f"Confirmed rust symptoms observed across all plants. {disclaimer}",
    ]
    
    for text in prohibited_texts:
        res = filter.evaluate(text)
        assert res.passed is False, f"Expected violation for: '{text}'"
        assert any("prohibited" in v.lower() for v in res.violations)


def test_guardrails_rejects_empty_text():
    filter = CertaintyGuardrailFilter()
    assert filter.evaluate("").passed is False
    assert filter.evaluate("   ").passed is False
