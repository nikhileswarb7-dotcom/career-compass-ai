# Dataset Data Card — CareerCompass AI

This document outlines the data sources, provenance, counts, and limitations of the database and machine learning training datasets used in CareerCompass AI.

---

## 1. Overview & Provenance
*   **Data Scope**: The profiles used for benchmarking SDE readiness and training affinity models were collected from public professional profiles (LinkedIn and GitHub) representing engineers in top tier technical organizations.
*   **Intended Use**: Evaluating career preparation and estimating specialization affinities (General Software Engineering, Backend, Frontend) for engineering students.
*   **Prohibited Claims**: The profiles do not represent an exhaustive industry census or a guarantee of hiring criteria.

---

## 2. Master Ontology Versioning
*   **Ontology Version**: `1.1.0`
*   **Skill Expansion**: Expanded from 28 to **53 canonical skills** to capture modern frontend, backend, database, testing, mobile, DevOps, and ML/Data stacks.
*   **Alias Mapping**: Implemented a string normalizer (e.g. `Reactjs` -> `React`, `AWS` -> `AWS Basics`) to map raw resume/LinkedIn inputs to canonical ontology entries.

---

## 3. Database Statistics & Table Row Counts
The PostgreSQL database (schema: `career_compass_ai`) contains the following validated row counts (matching live production state):

| Table Name | Description | Row Count |
| :--- | :--- | :---: |
| `employee_profiles` | Professional profiles of industry engineers | **486** |
| `companies` | Corporate entities normalized in the system | **1045** |
| `education_profiles` | Academic background (degrees and universities) | **446** |
| `employee_skills` | Profile-to-skill foreign key mapping entries | **863** |
| `career_transitions` | Corporate transition sequence histories | **1111** |
| `roles` | Canonical target product roles (e.g. SDE, SRE, PM) | **30** |
| `skills` | Master canonical skills list (ontology) | **53** |
| `stage_skills` | Phase 2 SDE stage-skill qualification rules | **50** |
| `roadmap_stage_skill_mapping` | Active SDE content mapping indexes | **50** |

---

## 4. Reproducible ML Dataset Card
*   **Training Subset**: Profiles matching SDE (289), Software Engineer (131), Backend Developer (30), and Frontend Developer (23).
*   **Row Count**: **473 independent professionals**.
*   **Dataset Version**: `1.0.0`
*   **Dataset Hash (MD5)**: `85285b02695f8301a6d567bc1b7f97c8`
*   **Primary Features**: 53 binary skill columns, `experience_years`, one-hot encoded `college` (IIT/NIT/IIIT/BITS/Other), and `degree` (BTech/BE/MCA/MTech/Dual Degree/Other).
*   **Targets**: Binary classification vectors `target_general`, `target_backend`, `target_frontend` (One-vs-Rest formulation).

---

## 5. Data Quality Limitations
1.  **Imbalance**: SDE/Software Engineer dominates the sample (420 out of 473 profiles, 88.8%), reflecting the broad scope of SDE title labels. Specializations (Backend 30, Frontend 23) represent smaller, refined cohorts.
2.  **Missingness**: 15.8% of parsed database profiles do not contain explicitly listed skills, which are handled by fallback headline/experience scanners during ingestion.
3.  **Collection Bias**: Profile data is gathered predominantly from high-growth tech companies (Blinkit, Swiggy, Paytm). Consequently, company-history features were excluded from the primary model to prevent shortcut learning.
