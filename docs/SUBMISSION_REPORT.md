# Submission Report — CareerCompass AI

This report provides the executive overview of the technical achievements, database improvements, machine learning pipeline, and reliability upgrades implemented for the CareerCompass AI submission.

---

## 1. Project Overview & Focus
CareerCompass AI is a hybrid intelligent career planning dashboard designed to help technical students prepare for software engineering hiring bars.

Our engineering work was structured around five critical reliability and feature milestones:
1.  **Phase 1: Database & Data Quality Audit**: Inspected raw CSV files and PostgreSQL tables. We logged, identified, and removed profile duplicates, missing labels, and class imbalances.
2.  **Phase 2: Correctness & positive stage filtering**: Resolved content-leakage bugs by introducing positive stage-skill filtering. Stage content is mapped dynamically to current-stage skills, validated against prerequisite rules.
3.  **Phase 3: Machine Learning Specialization Modeling**: Built a versioned profile dataset (473 records) with an alias normalizer expanding the master ontology to 53 skills. Trained and calibrated three OvR specialization classifiers.
4.  **Phase 4: Safe Integration & Trace Exporter**: Built an in-memory `MLSpecializationAffinityEngine` that caches model pipelines, performs OOD checks, and exposes outputs under the explainable decision trace. Added dashboard affinity panels in the React frontend.
5.  **Phase 5: Reliability & Demo Gate**: Conducted failure mode assessments, security audits, and regression tests. All 7 verification suites passed successfully.

---

## 2. Technical Accomplishments Summary

### Database Integrity Upgrade:
*   Unified database aliases and expanded the ontology table from 28 to **53 canonical skills**.
*   Wrote `repair_stage_skills.py` to map Blinkit SDE roadmap content cleanly without disrupting other role mappings.
*   Enforced strict database foreign keys and transaction commits.

### Machine Learning Performance:
*   Built the reproducible ML dataset (MD5: `85285b02695f8301a6d567bc1b7f97c8`).
*   Developed sigmoid-calibrated pipelines (`CalibratedClassifierCV`) achieving excellent General SDE Foundation classification (PR-AUC: 0.9217, Brier Score: 0.0987).
*   Handled Out-Of-Distribution (OOD) scenarios gracefully using skill overlap constraints.

---

## 3. Testing & Verification Summary

The unified submission test suite reports **100% success rate** across all core modules:

*   **Database Schema & Integrity**: `PASS`
*   **Roadmap Correctness & Prerequisites**: `PASS`
*   **ML Affinity Fallbacks & Constraints**: `PASS`
*   **Session Flow Integration**: `PASS`
*   **Session Isolation & Concurrency**: `PASS`
*   **API Endpoint Coverage**: `PASS`
*   **Legacy Regression Suites (TC001-TC014)**: `PASS`

---

## 4. Setup & Installation
Follow these commands to set up the prototype locally:

```bash
# 1. Install dependencies
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv joblib scikit-learn pandas

# 2. Configure .env file
# Create a .env file with DATABASE_URL, GEMINI_API_KEY, etc.

# 3. Start Backend server
python api/app.py

# 4. Navigate to frontend-react and run dev server
cd frontend-react
npm install
npm run dev
```
