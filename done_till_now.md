1. Current Repository State
text
[Video Upload] ──> [Frame Extractor] ──> [Quality Filter] ──> [Detector & Classifier] ──> [Aggregation] ──> [LLM + Guardrails] ──> [Diagnosis API]
    ✅ DONE              ✅ DONE                ✅ DONE                  ✅ READY                  ⚠️ PARTIAL             ❌ MISSING               ⚠️ NEEDS LINK
Trained Model & Classifier (

DiseaseClassifier
): Fine-tuned EfficientNet-B0 on ASDID loaded with 5 classes (soybean_bacterial_blight, soybean_frogeye_leaf_spot, soybean_healthy, soybean_rust, unknown_other) + temperature scaling calibration.
Plant Detector (

PlantDetector
): Faster R-CNN plant/leaf region detector with bounding-box extraction.
Inference Orchestration (

InferenceService
): Persists Detection and FrameDiagnosis rows in Postgres/SQLite with model versions.
Aggregation (

BayesianAggregator
): Implemented but not yet invoked in the ingestion pipeline.
Safety Guardrail (

CertaintyGuardrailFilter
): Implemented regex filters against overconfident medical/cure claims.
Reporting Templates (

templates.py
): Deterministic canned reports ready as fallback.
2. Next Steps to Complete the MVP
Step 1: Implement LLM Advisory Generation Service
Create 

backend/app/modules/reporting/llm_advisor.py
 to generate contextual, safe agricultural advisory reports:

Integrate with Gemini 1.5 Flash (via google-genai / google-generativeai using settings.LLM_API_KEY) or standard OpenAI/LiteLLM client.
Structured Prompting: Pass crop type (soybean), diagnosed disease, Bayesian confidence score & band (high/medium/low), severity level (0–3), affected plant percentage, and evidence frame count.
Output Contract: Return structured JSON with headline, explanation, and action_items (cultural practices, scouting tips, extension officer guidance).
Mandatory Safety Rule: Never provide lethal chemical recipes/dosages; always include "AI estimate, not a confirmed diagnosis. Consult an agronomist."
Step 2: Connect LLM Output to Certainty Guardrails & Canned Fallback
In the reporting service:

Run LLM response through 

CertaintyGuardrailFilter.evaluate()
.
If the LLM call fails, times out, or fails guardrails after 1 retry, immediately fall back to 

get_canned_report()
.
Step 3: Wire Bayesian Aggregator & Disease Table in Ingestion Pipeline
Update 

VideoIngestionService._process_pipeline_internal
:

Replace inline weighted averaging with 

BayesianAggregator.aggregate(frame_results)
 and 

estimate_field_severity()
.
Query the Disease table by slug to set VideoDiagnosis.disease_id.
Call the LLM advisory generator and store explanation and structured advice in VideoDiagnosis.
Step 4: Update API & Database Schemas
Verify 

GET /api/v1/diagnosis/{video_diagnosis_id}
 serves the generated explanation, action items, severity meters, and frame evidence.
Ensure action_items or structured recommendations are stored or serialized into the response schema.
Step 5: End-to-End Verification Test
Write an automated integration test in backend/tests/integration/test_full_pipeline.py:

Upload a mock soybean video or frame sequence.
Run Celery/in-process pipeline: Frame extraction ➔ Detection ➔ Classification (with real weights) ➔ Bayesian aggregation ➔ LLM explanation generation ➔ Guardrail validation.
Assert that a VideoDiagnosis record is created with non-null confidence, severity, and guarded explanation.
Suggested Execution Order
Phase	Tasks	Estimated Scope
Phase 1	Build llm_advisor.py + Gemini/LLM provider integration + prompt template	~1-2 hours
Phase 2	Connect Bayesian aggregator, severity estimator & LLM advisor into ingestion/service.py	~1 hour
Phase 3	Wire guardrails (certainty_filter.py) & template fallbacks	~30 mins
Phase 4	End-to-end integration test (backend/tests/) & API response verification	~1 hour
Would you like to proceed with implementing the LLM Advisory Service and wiring it into the ingestion pipeline?

