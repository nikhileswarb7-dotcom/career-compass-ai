# Model Card — CareerCompass AI Specialization Affinity

This model card details the development, validation, calibration, and constraints of the specialization affinity pipelines used to evaluate student alignment with professional career tracks.

---

## 1. Model Details
*   **Model Type**: Sigmoid-calibrated Logistic Regression classifiers with balanced class weighting.
*   **Version**: `1.0.0`
*   **Developer**: Antigravity AI Assistant & CareerCompass Team.
*   **Release Date**: July 6, 2026.
*   **Intended Use**: Estimating how closely a student's technical stack (skills, experience, education) resembles industry patterns for General Software Engineering, Backend, and Frontend roles.
*   **Status**: **Experimental evidence-only signal**. The scores must not override selected targets, select resources, or make success guarantees.

---

## 2. Training Data & Leakage Controls
*   **Dataset Source**: PostgreSQL professional profiles dataset (MD5 Hash: `85285b02695f8301a6d567bc1b7f97c8`).
*   **Sample Size**: **473 independent profiles** (Train: 378, Test: 95).
*   **Class Imbalance**: General Foundation (`420`), Backend Specialization (`30`), Frontend Specialization (`23`).
*   **Leakage Controls**:
    *   No target labels or role names are used as input.
    *   Company histories are excluded from features to prevent the model from learning collection-specific shortcuts.
    *   Prerequisites and roadmaps are kept strictly independent of model outputs.

---

## 3. Evaluation Metrics
Models were trained using stratified 5-fold cross-validation (3 repeats) and evaluated on an untouched 20% holdout test set (95 samples).

### Holdout Performance:
*   **General Foundation Model**:
    *   *PR-AUC*: **0.9217** (Baseline chance: 0.8842)
    *   *ROC-AUC*: **0.7100**
    *   *Brier Calibration Score*: **0.0987**
*   **Backend Specialization Model**:
    *   *PR-AUC*: **0.1521** (Baseline chance: 0.0632 - 2.4x baseline)
    *   *ROC-AUC*: **0.6536**
    *   *Brier Calibration Score*: **0.0581**
*   **Frontend Specialization Model**:
    *   *PR-AUC*: **0.2735** (Baseline chance: 0.0526 - 5.2x baseline)
    *   *ROC-AUC*: **0.8667** (Excellent ranking performance)
    *   *Brier Calibration Score*: **0.0444**

---

## 4. Calibration & Score Interpretations
*   **Brier Scores**: Extremely low Brier scores (under 0.10) confirm high-quality probability calibration.
*   > [!IMPORTANT]
    > **PROHIBITED INTERPRETATION**: These affinity scores **must not** be displayed to students as "career success probabilities", "placement guarantees", or "suitability scores". They represent resemblance statistics compared to a versioned data sample of working professionals.

---

## 5. Out-Of-Distribution (OOD) Behavior
The model pipeline implements the following deterministic OOD gates:
1.  **Zero-Skill Input**: Returns `supported = False` and `confidence_status = "low"`.
2.  **No Ontology Overlap**: If none of the student's skills overlap with the 53 canonical ontology skills, the request is flagged as OOD (`supported = False`) and bypassed.
3.  **Low-Signal Profile**: If a student enters less than 3 skills, `confidence_status = "low"` is returned to warn the user.
