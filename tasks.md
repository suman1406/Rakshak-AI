# Backend ML Pipeline Implementation Tasks

## Task 1: Fix Video Ingestion Pipeline Issues
Fix diagnosis mapping (severity, disease ID), fix insufficient_evidence handling (return proper response, not 404), add idempotency (prevent duplicate frames on retry), wire existing detector and classifier into processing.

## Task 2: Wire Bayesian Aggregator into Pipeline
Import BayesianAggregator from aggregation/bayes.py, replace simple weighted average in service.py with aggregate(), use AggregatedDiagnosisResult for final diagnosis.

## Task 3: Wire Severity Module into Pipeline
Import from aggregation/severity.py, use estimate_field_severity() instead of inline calculation.

## Task 4: Create LLM Advisor Service with Groq Integration
Create backend/app/modules/reporting/llm_advisor.py, integrate Groq client with llama-3.1-70b-versatile, structured prompt: crop, disease, confidence, severity, evidence. Output: {headline, explanation, action_items, safety_disclaimer}. Add GROQ_API_KEY to settings.

## Task 5: Implement Guardrails Module
Create backend/app/guardrails/certainty_filter.py, regex patterns to filter overconfident medical/cure claims. Function: CertaintyGuardrailFilter.evaluate(text) -> (passed, violations).

## Task 6: Wire LLM + Guardrails into Pipeline
After Bayesian aggregation, call LLM advisor, run LLM output through guardrail filter, fall back to template-based report on failure/filter, store explanation + action_items in VideoDiagnosis.

## Task 7: Fix API Response Schemas
Add action_items field to responses, ensure consistency across /videos/{id}/analysis and /diagnosis/{id}, fix result_state values (ready, healthy, unknown, insufficient_evidence, failed).

## Task 8: End-to-End Integration Test
Upload video → extract frames → detect → classify → aggregate → LLM report. Verify complete diagnosis with explanation and action_items.