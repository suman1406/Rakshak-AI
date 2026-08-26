# Fasal Rakshak: Plan Loopholes & Evaluation Framework

A plan that doesn't survive its own critique isn't finished. Below is an honest look at where the original backend/ML plan breaks, followed by the evaluation framework best suited to this project.

## Part 1: Loopholes and Weak Points

### A. Data & flywheel loopholes

**1. Pilot data won't represent production reality.** University trial plots and 5–10 partner farms are cleaner, better-maintained, and more cooperative than the median smallholder farmer with a cracked-screen phone. Your golden test set built from pilot data will make the model look better than it actually performs in the wild — this is a form of selection bias baked into the "cold start fix" itself.
*Fix:* Deliberately recruit at least a few "worst-case" pilot sites (poor lighting, older phones, dense weedy fields) rather than optimizing pilot partner selection for convenience.

**2. VLM-assisted pre-labeling creates anchoring bias.** If agronomists see a VLM's suggested label before labeling, they tend to rubber-stamp it rather than independently verify — a well-documented failure mode in AI-assisted annotation. Your "verified" labels quietly inherit the VLM's blind spots.
*Fix:* Run periodic **blind re-labeling** — a sample labeled with the AI suggestion hidden — and measure agreement rate against the anchored labels. If agreement is suspiciously high, your agronomists are anchoring, not verifying.

**3. "Agronomist verification from video" isn't independent ground truth.** Both the model and the reviewing agronomist are looking at the *same evidence* (the same video). If the video itself is missing information a physical inspection would catch (e.g., root symptoms, pest presence, soil condition), verification just confirms internal consistency, not real-world correctness.
*Fix:* Budget for occasional **physical field visits or lab pathogen confirmation** on a small random sample (quarterly is reasonable) as a true ground-truth check independent of the video pipeline.

**4. Enterprise/B2B incentives can bias the flywheel.** Crop insurers and agri-input companies are named customers. An insurer has incentive to under-report disease (fewer payouts); an input company has incentive to over-report (more pesticide sales) if either is involved in generating or influencing labels.
*Fix:* Tag every verified label with its source channel, and never merge commercially-linked verifications into the core training set without separately auditing them for systematic skew vs. neutral agronomist labels.

**5. Regional inequity compounds itself.** If pilot farms concentrate in one or two states, the model launches strong there and weak elsewhere. Farmers in weak regions get bad early results, use the app less, generate less data — the flywheel ("more data → better models → more farmers") actively entrenches the gap instead of closing it.
*Fix:* Track per-region performance as a first-class metric before launch, not just post-launch drift monitoring, and deliberately over-invest pilot effort in underrepresented regions rather than letting geography be incidental.

### B. Pipeline design loopholes

**6. Component metrics hide end-to-end failure.** A detector with 90% mAP and a classifier with 90% F1 evaluated independently can still produce a pipeline that's wrong 30%+ of the time video-level, because errors compound across stages (missed lesion → classifier never sees it → aggregation has no signal). Independently evaluated models never explicitly measure the *cascade*.
*Fix:* covered in the evaluation section below (end-to-end + error attribution).

**7. Frame-level train/test splitting causes leakage.** If frames extracted from the same video land on both sides of a train/val split, near-duplicate frames inflate apparent accuracy — a classic and easy-to-miss mistake in exactly this kind of frame-extraction pipeline.
*Fix:* Split at the **video level** (or even farm/field level), never frame level.

**8. Severity heuristic is validated against its own inputs.** The MVP severity proxy is derived from detector output (lesion density, affected-region count) — and if you then "validate" severity using the same detector's outputs, you're checking self-consistency, not accuracy. There's no independent measurement of actual affected-area percentage.
*Fix:* During pilot, have agronomists provide an independent visual percentage-affected estimate (or literally count in a sample quadrat) so severity has a ground truth that isn't derived from the same model.

**9. The "Other/Unknown" class becomes a silent dumping ground.** Anything that doesn't fit — weeds, unrelated crop stress, rare diseases, bad frames that leaked through — gets bucketed into "Other," which never gets systematically mined, so genuinely emerging problems (new disease, new region-specific issue) hide inside it indefinitely.
*Fix:* Treat "Other" volume and composition as a monitored metric; periodically sample and manually review it, not just as an eval category but as an active data-mining source.

### C. Threshold & trust loopholes

**10. Blind false-negative minimization causes alarm fatigue.** Prioritizing false-negative rate above all else is correct in principle, but pushing thresholds purely toward catching everything floods farmers and agronomists with "possible disease" alerts on marginal cases. Once users learn most alerts are noise, they stop trusting or acting on any of them — which defeats the purpose more thoroughly than a missed case would. This tension needs an explicit resolution.
*Fix:* Threshold selection should be a **cost-weighted decision**, not a one-directional minimization — explicitly balance false-negative cost against alert-fatigue cost using real usage data (do farmers stop opening reports after N false alarms?), not just classifier metrics.

**11. Shadow mode is expensive and slow at low volume.** Shadow-mode evaluation assumes enough traffic to get statistically meaningful comparisons in reasonable time, and it also doubles GPU inference spend per prediction (old model + new model, both running). At early-pilot volume, this could take a long time to accumulate meaningful signal, or silently drain a tight compute budget.
*Fix:* Define a minimum sample size for shadow-mode conclusions up front, and use it selectively (major model changes only) rather than for every retrain — smaller updates can gate on the golden test set alone.

**12. Frozen golden test sets go stale.** A permanently frozen eval set doesn't capture new disease presentations, new regions, or new device types over time — but an eval set that keeps changing makes release-to-release comparisons meaningless.
*Fix:* Maintain a **versioned** golden set — a frozen regression subset that must never regress, plus a periodically refreshed subset (quarterly, governed, with a changelog) for measuring genuine progress.

### D. Governance / liability loophole

**13. Disclaimers alone don't cover the liability surface.** If a bank, insurer, or FPO makes a real financial decision partly informed by a false negative, "AI indication ≠ confirmed diagnosis" language in the UI doesn't fully protect against downstream liability once the system's output enters someone else's decision process.
*Fix:* For any B2B/financial-decision-linked customer, contractually and technically require human agronomist sign-off as the actual decision trigger, with the AI output logged as advisory input only — this needs to be enforced in the backend (a `decision_authority` flag on any case tied to a financial action), not just written in terms of service.

## Part 2: Evaluation Framework

### 1. Data integrity checks (before any model eval matters)
- **Video-level (not frame-level) train/val/test splits** — enforced in the dataset pipeline, checked automatically before every training run.
- **Stratified sampling** across crop, disease, severity, region, phone model, and lighting condition in every split.
- **Golden set governance**: frozen regression subset (must never regress) + periodically refreshed subset (tracks real progress), both versioned.

### 2. Component-level metrics

| Component | Primary metrics | Why these specifically |
|---|---|---|
| Plant/leaf/lesion detector | mAP@0.5, mAP@0.5:0.95, **per-class recall (especially lesion class)** | Recall on lesions matters more than overall mAP — a missed lesion silently kills everything downstream |
| Crop classifier | Accuracy, confusion matrix vs. visually-similar crops, calibration curve | Confusability with similar crops matters more than raw accuracy |
| Disease classifier | Precision/recall/F1 per class, **AUPRC per class** (not just AUROC — class imbalance makes AUPRC more informative), confusion matrix | AUPRC is far more sensitive to minority-class performance than AUROC under imbalance |
| Confidence calibration | **Expected Calibration Error (ECE)** + reliability diagrams, per confidence band | Directly tests whether "High confidence" actually means ~90%+ empirical accuracy, which the whole confidence-band system depends on |
| Severity model | **Quadratic Weighted Kappa** (ordinal-aware) + Macro F1 + MAE vs. independently-collected % affected | QWK penalizes "off by 2 levels" worse than "off by 1," which plain F1 doesn't capture — appropriate since severity is ordinal, not categorical |

### 3. End-to-end / pipeline metrics
- **Video-level diagnosis accuracy against agronomist-verified label** — the real product metric, computed on the full pipeline output, not any single stage.
- **Error attribution analysis**: when end-to-end is wrong, trace which stage caused it. Concretely — re-run the classifier+aggregation with *oracle* (ground-truth) detections substituted in, and compare to the full pipeline's error rate. The gap tells you how much error is attributable to detection vs. classification vs. aggregation, so you know where to invest next.
- **Aggregation ablation**: compare naive majority vote vs. confidence-weighted Bayesian aggregation vs. any later learned meta-model, all evaluated against the same video-level ground truth, before adopting a more complex aggregation method.
- **Repeat-scan / test-retest reliability**: scan the same healthy field twice in quick succession (no real change expected) and measure output agreement — catches a model that's noisy/unstable rather than genuinely sensitive, and matters directly for the disease-progression feature, which is meaningless if the underlying signal is jittery.

### 4. Threshold & operating-point selection
- **Cost-weighted confusion matrix** rather than blind recall maximization — assign explicit relative costs to false negatives vs. false positives and pick the operating point on the ROC/PR curve accordingly, rather than a single arbitrary threshold.
- Track **alert-dismissal rate / override-to-Healthy rate** as a live signal of alarm fatigue, and treat a rising trend as a threshold-tuning signal, not just a UX issue.

### 5. Open-set / novel-condition handling
- **OOD detection AUROC**: hold out a class entirely from training (or use a genuinely unseen disease/crop) as a proxy "unknown" test set, and measure how well the model's entropy/energy-based OOD score separates it from in-distribution predictions.
- **"Other" bucket precision/recall**, tracked explicitly, plus periodic manual mining of what's actually landing in that bucket.

### 6. Guardrail / explanation-layer eval
- **Red-team test set**: a curated set of adversarial or edge-case structured inputs (contradictory confidence/severity combinations, boundary confidence values, disallowed-language triggers) run against the LLM explanation layer, checking that the guardrail filter / schema validation / template fallback catches every case. Track this as a **guardrail pass rate**, targeted at ~100%, and treat any failure as release-blocking, not a soft warning.
- Periodic small-panel human review of generated farmer reports for clarity and (critically) for accidental overstated certainty that the automated regex/classifier guardrail might miss.

### 7. Fairness / robustness slices
- Report every metric above **sliced by region, phone model/OS, lighting condition, and video length**, not just in aggregate — this is what catches the regional-inequity loophole before it reaches farmers, rather than after.
- Stress tests: deliberately blurry/dark/very-short/wrong-crop/non-crop videos, and screen-replay videos as a proxy for the fraud-detection concern.

### 8. Bias-in-labeling checks
- **Blind vs. anchored labeling agreement rate**, run periodically, to detect and quantify VLM-pre-labeling anchoring bias.
- **Source-channel comparison**: compare disease-rate and severity distributions between commercially-linked (insurer/input-company) verified data and neutral agronomist-verified data, watching for systematic skew.

### 9. Product & business-level metrics
- False-negative rate — but always paired with false-positive/alert-dismissal rate so one can't be silently optimized at the other's expense.
- Agronomist override rate, split by whether the override matches the model's top-1 vs. top-2 prediction (partial-credit view of "close misses" vs. genuinely wrong).
- Cost per correctly-verified diagnosis (ties model quality directly to unit economics).

### 10. Release gate (tying it all together)
Before any model goes to shadow mode, and again before full promotion, it must: beat the current production model on the frozen regression set, show no slice-level regression beyond a defined threshold, pass calibration/ECE checks, pass the guardrail red-team suite at ~100%, and show acceptable repeat-scan consistency. This turns "evaluation" from a one-time training-report exercise into an actual release gate.
