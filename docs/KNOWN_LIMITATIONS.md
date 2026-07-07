# Known Limitations — CareerCompass AI

This document outlines the design tradeoffs, dataset size limits, and system constraints of the current CareerCompass AI prototype.

---

## 1. Machine Learning & Dataset Limitations
*   **Sample Size Constraints**: The ML models are trained on **473 profiles**. This is sufficient for learning stable baseline distributions of core technologies but does not capture niche specializations or cloud-native setups.
*   **Class Imbalance**: The SDE class represents **88.8%** of the dataset. While the models use Sigmoid probability calibration (`CalibratedClassifierCV`) and balanced class weighting, absolute PR-AUC metrics for Backend (0.1521) and Frontend (0.2735) are modest compared to the General SE Foundation.
*   **Equivalence of SDE and Software Engineer**: Profile analysis proved that SDE and Software Engineer are non-separable targets. They share a **0.6667 Jaccard overlap** and a low **0.1845 Jensen-Shannon Divergence**, necessitating their merger into a single "General SE Foundation" cohort.

---

## 2. Evidence-Only Integration Trait
*   The models are integrated in **Evidence-Only / Trace-Only mode**.
*   They do not dynamically alter or dynamically rearrange study stages.
*   This approach guarantees 100% roadmap stability and prevents class-imbalance bias from shifting critical study stages.

---

## 3. Database Content-Skill Schema Limitations
*   **Lack of Priority Sub-Tags**: The current `roadmap_stage_skill_mapping` and `stage_skills` tables do not distinguish between `essential_taught_skill`, `recommended_exposure_skill`, and `prerequisite_validation_skill`.
*   **Strict Mode Semantics**: Because of this schema limitation, the system enforces a strict prerequisite validator. Any content mapped to a skill must satisfy all prerequisite mappings of that skill, which may occasionally trigger false positives for optional multi-topic resources.
