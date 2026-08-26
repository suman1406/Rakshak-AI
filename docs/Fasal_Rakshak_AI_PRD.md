# PRD — Fasal Rakshak Video Intelligence
### AI-Powered Crop Disease Detection & Field Health Intelligence Platform

**Version:** 1.0
**Product Stage:** MVP → Production
**Primary Crop:** Soybean initially
**Company/Product:** Fasal Rakshak (ShivTrinetrix AI Labs Private Limited)

---

## 1. Product Vision

Fasal Rakshak Video Intelligence enables farmers, agronomists, FPOs, agri-input companies, insurers, and agricultural institutions to record a short video of a crop field and receive an AI-generated assessment of crop health.

The system converts a video into multiple high-quality visual observations, identifies potential diseases, estimates severity, aggregates observations across the field, and generates an actionable crop-health report.

**Core proposition**

> Record your crop. Detect disease. Measure severity. Map field health.

The product should not attempt to diagnose an entire farm from a single video frame. Instead, it should create a multi-frame evidence-based assessment.

---

## 2. Problem

Farmers currently face several problems:

- Disease identification often depends on visual experience.
- Agronomists cannot physically inspect every field.
- Existing image-diagnosis systems struggle with poor-quality farmer photographs.
- A single image does not represent the entire field.
- Disease severity is rarely quantified.
- Farmers often identify disease only after visible spread.
- Generic AI models may hallucinate agricultural diagnoses.
- Most disease datasets contain laboratory/curated images rather than real Indian field conditions.

**Opportunity**

Use smartphones as inexpensive field sensors.

A farmer's video provides:

- Multiple views
- Multiple plants
- Different angles
- Temporal information
- Spatial information
- Potential disease progression evidence

---

## 3. Product Goals

### MVP goals

1. Accept 10–30 second farm videos.
2. Automatically extract useful frames.
3. Remove blurry/redundant frames.
4. Detect plants/leaves.
5. Detect disease symptoms.
6. Classify likely disease.
7. Calculate confidence.
8. Estimate severity.
9. Aggregate predictions across frames.
10. Generate a farmer-friendly report.
11. Capture farmer feedback for model improvement.

### Long-term goals

- Multi-crop support
- Field disease mapping
- Disease progression monitoring
- Weather-based disease risk
- Early-warning system
- Agronomist network
- Disease outbreak intelligence

---

## 4. Non-Goals for MVP

Do not attempt initially to:

- Diagnose every crop in India.
- Support every possible disease.
- Prescribe pesticides automatically.
- Replace agronomists.
- Guarantee disease diagnosis.
- Build satellite analytics.
- Build IoT hardware.
- Perform autonomous chemical spraying.

The MVP should focus on visual disease detection and evidence-based crop-health assessment.

---

## 5. Target Users

### Primary — Farmers
Need a simple answer: *"Is my crop healthy? If not, what could be wrong?"*

### Secondary — Agronomists
Need:
- Evidence
- Images
- Disease probability
- Severity
- Field history

### B2B — FPOs
Monitor hundreds/thousands of farms.

### Enterprise
- Agri-input companies
- Crop insurers
- Banks/NBFCs
- Government agriculture departments
- Agricultural research organizations

---

## 6. Core User Journey

```
Open Fasal Rakshak
   ↓
Select Crop
   ↓
Select Field
   ↓
Record Video
   ↓
AI checks video quality
   ↓
Upload
   ↓
Processing
   ↓
Frame extraction
   ↓
Plant/leaf detection
   ↓
Disease detection
   ↓
Severity estimation
   ↓
Multi-frame aggregation
   ↓
AI Agronomist
   ↓
Crop Health Report
```

---

## 7. Farmer Video Capture

The app should actively guide the farmer.

### Camera instructions (before recording)

- "Walk slowly through the crop."
- "Keep the camera 30–60 cm from the plant."
- "Focus on leaves showing unusual symptoms."
- "Avoid shaking the camera."

### Real-time quality checks

Detect:

- Excessive blur
- Darkness
- Overexposure
- Excessive camera movement
- No crop detected
- Camera too far away
- Camera too close

### Quality score

```
Video Quality: 82/100
✔ Crop detected
✔ Good lighting
✔ Good focus
⚠ Move slightly slower
```

If quality is below threshold: *"Please record another video."*

---

## 8. Video Processing Engine

The uploaded video should not be sent directly to an LLM.

### Pipeline

```
Video
  ↓
FFmpeg
  ↓
Frame extraction
  ↓
Scene/change detection
  ↓
Blur detection
  ↓
Duplicate removal
  ↓
Best-frame selection
  ↓
Plant detection
  ↓
Leaf/lesion crops
```

### Frame sampling

For a 20-second video:

- Initial extraction: ~30–60 frames
- Then select approximately **10–20 high-quality frames** for disease analysis.

This controls inference cost.

---

## 9. Crop Detection

First determine: *What crop is being recorded?*

**Example:**

| Crop Classification | Confidence |
|---|---|
| Soybean | 94% |
| Groundnut | 3% |
| Other | 3% |

If confidence is too low: *"We couldn't confidently identify the crop. Please select your crop."*

For MVP, crop selection can be mandatory and AI can verify it.

---

## 10. Plant / Leaf Detection

Use an object detection model to identify:

- Plant
- Leaf
- Diseased leaf
- Lesion
- Stem
- Fruit/pod where relevant

**Example:**

```
Frame 17
Plants detected: 8
Leaves detected: 31
Potential lesions: 7
```

---

## 11. Disease Classification Engine

Each relevant crop/leaf region is classified.

**Example — Soybean Leaf #17**

| Class | Probability |
|---|---|
| Healthy | 4% |
| Rust | 89% |
| Bacterial Blight | 5% |
| Other | 2% |

Store the complete probability distribution rather than only the top prediction.

---

## 12. Temporal Voting Engine

This is a key differentiator. Predictions from individual frames should be aggregated.

**Example:**

```
Frame 1 → Rust 82%
Frame 2 → Rust 91%
Frame 3 → Rust 88%
Frame 4 → Healthy 61%
Frame 5 → Rust 93%
Frame 6 → Rust 87%

Aggregation:
Rust
Evidence: 5/6 frames
Final confidence: 89%
```

This prevents one bad frame from dominating the diagnosis.

---

## 13. Severity Engine

The system should estimate:

### Severity levels

- Level 0 — Healthy
- Level 1 — Early
- Level 2 — Moderate
- Level 3 — Severe

### Potential factors

- Percentage of affected leaves
- Lesion size
- Number of affected plants
- Disease concentration
- Disease distribution
- Visual symptom intensity

**Example:**

```
Severity: Moderate
Estimated affected plants: 18–25%
```

The percentage should be presented as an AI estimate, not a precise field measurement unless the sampling methodology supports it.

---

## 14. Disease Confidence

Use three confidence bands:

| Band | Range | Meaning |
|---|---|---|
| High | ≥90% | Strong visual evidence |
| Medium | 70–89% | Likely; additional inspection recommended |
| Low | <70% | Insufficient visual evidence |

Low-confidence cases should trigger: *"Unable to confidently identify the disease."*

This is critical for preventing unsafe false certainty.

---

## 15. AI Agronomist Layer

The AI Agronomist receives structured model output.

### Input

```
Crop: Soybean
Disease: Rust
Confidence: 89%
Severity: Moderate
Affected plants: ~20%
Evidence: Brown/yellow lesions across multiple leaves
Frames supporting diagnosis: 12/16
```

### Output (farmer-friendly explanation)

```
Possible Soybean Rust
The video shows leaf symptoms consistent with soybean rust.
Similar symptoms were detected across multiple plants.

Confidence: High
Severity: Moderate
Estimated affected plants: ~20%
```

The AI must explicitly distinguish: **AI indication ≠ confirmed diagnosis.**

---

## 16. Treatment Recommendation Layer

For MVP, avoid autonomous pesticide prescriptions. Instead:

### Recommended action

- Inspect additional plants.
- Capture close-up images of affected leaves.
- Check surrounding plants.
- Consult an agronomist if symptoms are spreading.

### Future versions can incorporate

- Crop stage
- Region
- Disease
- Weather
- Registered agricultural products
- Local agronomist validation
- Government agricultural guidance

---

## 17. Field Health Score

Create a simple score: **Fasal Health Score (0–100)**

**Example:** `Fasal Health Score: 72/100`

### Components could include

| Component | Weight |
|---|---|
| Disease prevalence | 30% |
| Disease severity | 25% |
| Healthy plant ratio | 25% |
| Visual stress indicators | 10% |
| Confidence | 10% |

The exact scoring model should be validated experimentally rather than arbitrarily fixed in production.

---

## 18. Field-Level Intelligence

Once the farmer records multiple videos from different locations:

```
FIELD
├── Zone A → Healthy
├── Zone B → Early disease
├── Zone C → Moderate
├── Zone D → Severe
└── Zone E → Healthy
```

### Generate: Field Health Map

- 🟢 Green = Healthy
- 🟡 Yellow = Early symptoms
- 🟠 Orange = Moderate
- 🔴 Red = Severe

This becomes a major future product feature.

---

## 19. Disease Progression

Farmers can repeat scans.

```
Day 1  → Disease prevalence: 8%
Day 7  → Disease prevalence: 14%
Day 14 → Disease prevalence: 27%

System: "Disease appears to be increasing."
```

This transforms Fasal Rakshak from a diagnostic tool into a crop monitoring platform.

---

## 20. Weather Intelligence

Add:

- Temperature
- Humidity
- Rainfall
- Wind
- Crop stage
- Historical weather

### Architecture

```
Visual Evidence
  +
Weather
  +
Crop
  +
Location
  ↓
Disease Risk Engine
  ↓
Output: Disease Risk: High
```

Weather should support the visual assessment rather than override it.

---

## 21. Data Flywheel

This should be one of the biggest strategic advantages.

```
Farmer Video
  ↓
AI Prediction
  ↓
Agronomist Verification
  ↓
Correct Label
  ↓
Training Dataset
  ↓
Model Retraining
  ↓
Better Detection
  ↓
More Farmers
  ↓
More Data
```

Over time you accumulate:

- Indian field images
- Indian field videos
- Regional variations
- Disease severity examples
- Crop-stage information
- Weather context
- Verified agronomist labels

This becomes the moat.

---

## 22. Agronomist Verification Dashboard

Agronomists should see:

```
Case #FASAL-10482
Crop: Soybean
AI Diagnosis: Rust — 87%
Severity: Moderate
[Video]
AI Evidence: 12 supporting frames

Agronomist:
[ Confirm Rust ]  [ Change Disease ]  [ Healthy ]  [ Uncertain ]
```

Every correction becomes training data.

---

## 23. Dataset Architecture

```
Crop
└── Disease
     └── Severity
          └── Region
               └── Crop Stage
                    └── Image/Video
```

**Example:**

```
Soybean
└── Rust
     ├── Early
     ├── Moderate
     └── Severe
```

### Each record should contain

- Image/video
- Crop
- Disease
- Severity
- GPS region at appropriate privacy granularity
- Date
- Crop stage
- Weather metadata
- Expert label
- AI prediction
- Confidence

---

## 24. ML Architecture

### MVP

```
Object Detection (YOLO-family model)
  ↓
Disease Classification (CNN / Vision Transformer)
  ↓
Temporal Aggregation (Custom probability aggregation model)
  ↓
Severity Model (Classification/regression)
  ↓
LLM/VLM (Explanation layer)
```

---

## 25. Model Training Strategy

| Stage | Description |
|---|---|
| Stage 1 | Use public agricultural datasets and existing models for initial baseline. |
| Stage 2 | Collect real Indian field images. |
| Stage 3 | Agronomist annotation. |
| Stage 4 | Fine-tune disease classifier. |
| Stage 5 | Introduce difficult real-world conditions: different phones, different lighting, dust, shadows, multiple plants, partial leaves, motion blur, background clutter. |
| Stage 6 | Field validation. |

Don't optimize solely for benchmark accuracy. Optimize for **real-world field performance.**

---

## 26. Model Evaluation

### Classification
- Accuracy
- Precision
- Recall
- F1
- Confusion matrix
- AUROC where appropriate

### Detection
- mAP
- Precision
- Recall

### Severity
- Macro F1
- MAE for severity score

### Product-level metrics

**Most important:** False-negative rate — a missed disease can be more harmful than an unnecessary "possible disease" alert.

Also track:

- % cases requiring agronomist review
- Diagnosis confidence calibration
- User correction rate
- Repeat-scan agreement

---

## 27. Tech Stack

| Layer | Technology |
|---|---|
| Mobile | Flutter |
| Backend | Python + FastAPI |
| ML | PyTorch |
| Computer Vision | OpenCV, YOLO, Custom disease classifier |
| Video | FFmpeg |
| Database | PostgreSQL |
| Storage | Object storage such as S3-compatible storage |
| Queue | Redis + Celery/RQ or equivalent |
| Deployment | Docker + GPU inference infrastructure |
| AI reasoning | LLM/VLM API for explanation and report generation |

---

## 28. API Design

| Purpose | Endpoint |
|---|---|
| Upload | `POST /api/v1/videos` |
| Processing status | `GET /api/v1/videos/{video_id}/status` |
| Analysis | `GET /api/v1/videos/{video_id}/analysis` |
| Diagnosis | `GET /api/v1/diagnosis/{analysis_id}` |
| Feedback | `POST /api/v1/diagnosis/{analysis_id}/feedback` |
| Agronomist verification | `POST /api/v1/diagnosis/{analysis_id}/verify` |
| Field | `GET /api/v1/fields/{field_id}/health` |

---

## 29. Example API Response

```json
{
  "crop": "soybean",
  "crop_confidence": 0.94,
  "diagnosis": {
    "disease": "soybean_rust",
    "confidence": 0.89,
    "severity": "moderate",
    "affected_plant_estimate": 0.21
  },
  "evidence": {
    "frames_analyzed": 16,
    "supporting_frames": 12,
    "leaf_regions_analyzed": 43
  },
  "recommendation": {
    "action": "additional_inspection",
    "agronomist_review": true
  }
}
```

---

## 30. Farmer Report

The result screen should be extremely simple.

**Example:**

```
Crop Health — Soybean

Possible Disease Detected
Soybean Rust
Confidence: High
Severity: Moderate
Estimated affected plants: ~20%

What we found
AI detected similar leaf symptoms across multiple plants in your video.

What to do now
1. Inspect more plants around the affected area.
2. Capture close-up images of affected leaves.
3. Consult an agronomist for confirmation.

[Talk to Agronomist]   [Scan Another Area]
```

---

## 31. B2B Dashboard

For FPOs/agri companies:

```
FASAL RAKSHAK
────────────────────────
Total Farms: 4,281
Healthy: 62%
At Risk: 23%
Disease Detected: 15%

Top Diseases
Soybean Rust: 42%
Bacterial Blight: 27%
Other: 31%

High-Risk Farms: 143
```

Drill-down path:

```
Disease → District → FPO → Farm → Field → Video Evidence
```

---

## 32. Security & Privacy

Implement:

- Encryption in transit
- Encryption at rest
- Role-based access
- Consent-based data collection
- Secure video storage
- Audit logs
- Data retention controls

GPS/location information should be handled carefully because precise farm locations can be sensitive.

---

## 33. Safety & AI Guardrails

The system must **never** say: *"You definitely have disease X."*

Instead: *"The visual symptoms are consistent with disease X."*

The system should return:

| Confidence | Response |
|---|---|
| HIGH | Likely disease + evidence |
| MEDIUM | Likely disease + recommend confirmation |
| LOW | Insufficient evidence |

For uncertain or novel symptoms: *"Unable to confidently classify this condition."*

This is preferable to hallucinating a disease.

---

## 34. MVP Success Metrics

### Technical (targets to validate, not assumptions)

- ≥90% precision for selected high-confidence disease classes
- High recall on priority diseases
- <10% unusable video rate
- <60 seconds average processing time for a short video

### Product

- Video completion rate
- Successful analysis rate
- Repeat usage
- Farmer correction rate
- Agronomist confirmation rate
- % of cases with sufficient evidence

### Business (potential B2B metrics)

- Farms monitored
- Cost per analyzed farm
- Agronomist cases generated
- Enterprise customers
- Revenue per monitored farm

---

## 35. MVP Roadmap

**Sprint 1–2**
- Soybean dataset
- Video upload
- FFmpeg processing
- Frame extraction
- Quality scoring

**Sprint 3–4**
- Plant/leaf detection
- Disease classifier
- Temporal aggregation
- Basic severity model

**Sprint 5**
- Farmer dashboard
- AI-generated report
- Feedback mechanism

**Sprint 6**
- Agronomist dashboard
- Label correction
- Dataset pipeline

**Sprint 7–8**
- Field-level analytics
- Production deployment
- Pilot with real farms

---

## 36. Phase 2

Add:

- Hindi + regional languages
- Real-time camera guidance
- Multiple crop support
- Multiple disease detection
- Field health score
- Historical scans
- Disease progression
- Agronomist marketplace

---

## 37. Phase 3 — The Bigger Product

Turn Fasal Rakshak into: **AI Crop Health Operating System**

```
                    FASAL RAKSHAK
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                  ↓
   Disease AI      Field Intelligence    Weather AI
        │                 │                  │
        └─────────────────┼─────────────────┘
                          ↓
                   Risk Prediction
                          ↓
                Disease Early Warning
                          ↓
                 Agronomist Network
                          ↓
               Agricultural Ecosystem
```

### Potential customers

- FPOs
- Agri-input companies
- Crop insurers
- Banks
- Government agencies
- Large agricultural enterprises
- Research organizations

---

## 38. The Core Moat

The strongest moat isn't the YOLO model. It is:

> **Verified Indian agricultural field data.**

Over time: 100,000 videos → millions of frames → thousands of expert-verified cases → proprietary dataset → increasingly accurate models.

The flywheel becomes:

> More farmers → more field data → better models → better diagnosis → more farmers.

---

## Final Product Positioning

**Fasal Rakshak — AI Field Health Intelligence**

> Record your crop. Detect disease. Measure severity. Prevent spread.

| Version | Capability |
|---|---|
| MVP | Video → Disease Detection |
| V2 | Video → Disease + Severity |
| V3 | Video → Field Health Map |
| V4 | Field Health + Weather → Disease Risk |
| V5 | Regional Data → Disease Early-Warning Network |
