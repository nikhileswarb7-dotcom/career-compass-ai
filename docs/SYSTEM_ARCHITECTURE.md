# System Architecture — CareerCompass AI

This document details the software architecture, modular boundaries, database-backed templates, and AI integration pipelines of the CareerCompass AI career planner.

---

## 1. Dual-Engine Hybrid Pipeline

CareerCompass AI uses a **hybrid design** to ensure absolute recommendation reliability and submission safety:

```
        +-------------------------------------------------------+
        |                  Student input profile                |
        +-------------------------------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      ProfessionalFeatureBuilder   |
                  +-----------------------------------+
                                    |
                                    +-----------------------+
                                    |                       |
                                    v                       v
                      +---------------------------+   +-----------+
                      | Deterministic Knowledge   |   |   ML      |
                      |          Engine           |   | Affinity  |
                      |   (Template & Schema)     |   |  Engine   |
                      +---------------------------+   +-----------+
                                    |                       |
                                    v                       v
                      +-------------------------------------------+
                      |   Hybrid Decision Trace & UI Exporter     |
                      +-------------------------------------------+
```

1.  **Deterministic Knowledge Engine**: Governs roadmap durations, stage sequences, skill-gap detection, content prerequisites, and coding challenges. This is backed by a transactional relational database schema ensuring that roadmaps never leak future skills or bypass prerequisites.
2.  **ML Specialization Affinity Engine**: Learns professional profiles from real-world datasets, outputting supporting evidence regarding General SE foundation, Backend, and Frontend affinities.

---

## 2. Year-Aware Roadmap Planner
The planner adjusts roadmap parameters based on academic year and CGPA:
*   **1st-Year Students**: Assigned a duration of **18 Months** with a lightweight **15 weekly study hours** target to build core foundations.
*   **2nd-Year Students**: Assigned **12 Months** with **20 weekly study hours**.
*   **3rd-Year Students**: Typically placement candidates, assigned a compressed **6 Months** with **25 weekly study hours** to lock down core readiness.
*   **4th-Year Students / Graduates**: Assigned an urgent **3 Months** with **30 weekly study hours** to ensure immediate readiness.
*   **CGPA Thresholds**: If a student's CGPA is below 8.00, the system flags eligibility alerts for companies with high-CGPA cut-offs (e.g. Swiggy/Blinkit) without modifying study stages.

---

## 3. Database Isolation and Content Correctness
To prevent resource, question, or challenge leakage:
*   **Strict Prerequisite Mapping**: High-concurrency or backend topics (e.g. Docker, Redis) require foundation prerequisites (e.g. DSA, DBMS) to be solved first.
*   **Positive Stage-Skill Filtering**: Stage content is queried through database mapping rules (`roadmap_stage_skill_mapping` and `stage_skills`), preventing future-stage material from appearing in current stages.

---

## 4. API Resilience & Gemini Failbacks
*   The backend service uses a fallback structure for the AI coach's explanation.
*   If the Gemini API encounters a quota limit, timeout, or network failure, the application catches the exception and returns a **structured fallback coach explanation** generated from the local profile analysis.
*   The entire onboarding, roadmap generation, skill mapping, assessments, and interview prep features operate **100% independently of LLM availability**.
