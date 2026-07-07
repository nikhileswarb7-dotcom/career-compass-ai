# CareerCompass AI
### NLP-Based Career Navigation System for Industry-Specific Roles

---

### 🌟 Submission Documentation & Gate Artifacts
Please review the complete internship submission documents located in the agent environment workspace:
*   [Unified Submission Gate (FINAL_SUBMISSION_GATE.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/FINAL_SUBMISSION_GATE.md) — Verdict: **GO**
*   [Submission Report (SUBMISSION_REPORT.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/SUBMISSION_REPORT.md) — Accomplishments overview
*   [Model Card (MODEL_CARD.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/MODEL_CARD.md) — OvR classifiers, PR-AUC and calibration metrics
*   [Data Card (DATA_CARD.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/DATA_CARD.md) — Schema statistics and row counts
*   [System Architecture (SYSTEM_ARCHITECTURE.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/SYSTEM_ARCHITECTURE.md) — Hybrid pipeline and positive stage filters
*   [Demonstration Script (DEMO_SCRIPT.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/DEMO_SCRIPT.md) — 5–7 min live demo guide using 3 reproducible personas
*   [Known Limitations (KNOWN_LIMITATIONS.md)](file:///C:/Users/nikhi/.gemini/antigravity-ide/brain/dd0d8955-9343-4ea0-8812-3b8d612846f0/KNOWN_LIMITATIONS.md) — Class imbalances and schema boundaries

---

## Problem Statement

Students often know their dream company and role but lack a structured, personalized roadmap based on their current qualification level and skill set. Generic career advice doesn't account for time urgency — a 1st-year student needs a different strategy than a final-year student targeting the same role.

---

## Solution

CareerCompass AI is a **Career Navigation System** that takes a student's current qualification and known skills, and generates a **personalized, stage-by-stage career roadmap** to become a Software Development Engineer at Blinkit.

---

## Target (Phase 1)

| Field | Value |
|-------|-------|
| Company | Blinkit |
| Role | Software Development Engineer (SDE) |
| Qualifications Supported | 1st Year, 2nd Year, 3rd Year, 4th Year, Fresh Graduate, Trainee Engineer, Junior Software Engineer |

---

## System Architecture

```
User Query (Text / Form)
        │
        ▼
  NLP Processor
  (nlp_processor.py)
  Extracts: qualification, skills, company, role
        │
        ▼
  Recommendation Engine
  (recommendation_engine.py)
  Gap Analysis + Roadmap Generation
        │
        ▼
  PostgreSQL Database
  (career_compass)
  Fetches: roadmap stages, resources, projects, guidance
        │
        ▼
  Personalized Career Plan
  - Readiness Score
  - Missing Skills (priority-ordered)
  - Stage-by-Stage Roadmap
  - Projects to Build
  - Resources to Use
  - Resume / LinkedIn / GitHub Guidance
  - 30-Day Action Plan
  - Estimated Time to Ready
```

---

## Project Structure

```
career-compass-ai/
│
├── api/
│   ├── app.py                  ← FastAPI web server entry point
│   └── database_connector.py   ← Dual PostgreSQL & CSV fallback layer
│
├── database/
│   ├── schema.sql              ← All core PostgreSQL tables
│   ├── seed_data.sql           ← Seed scripts for companies, roles, and stages
│   └── learning_layer/         ← CSV fallback datasets (e.g. stage_training_content.csv)
│
├── datasets/                   ← Static JSON templates
│   ├── companies/
│   ├── roles/
│   ├── qualifications/
│   ├── roadmaps/
│   ├── projects/
│   ├── resources/
│   ├── interview_questions/
│   └── guidance/
│
├── frontend-react/             ← Premium React SPA (Vite + Tailwind/Vanilla CSS)
│   ├── src/
│   │   ├── components/         ← Reusable layout & drawer modules
│   │   ├── pages/              ← Dynamic page views (Dashboard, Roadmap, etc.)
│   │   ├── App.jsx             ← React routes & state providers
│   │   └── index.css           ← Global glassmorphic design tokens
│   ├── package.json
│   └── vite.config.js
│
├── model/                      ← NLP & Recommendation Core Engines
│   ├── nlp_classifier.py       ← Entity extractor for student form inputs
│   └── readiness_score.py      ← Readiness metric calculation engines
│
├── profile_analysis/           ← Resume and social extraction modules
├── services/                   ← Application services
├── testing/                    ← Integration & unit test suite
│   ├── run_tests.py            ← Run rule-based validation tests
│   ├── verify_session_flow.py  ← Verify API session workflow transitions
│   └── verify_session_isolation.py  ← Verify candidate session sandbox isolation
│
├── README.md
└── .gitignore                  ← Configured repository ignore file
```

---

## Setup & Running Instructions

### 1. Install PostgreSQL
Ensure a local PostgreSQL instance is running on your machine.

### 2. Database Creation & Seeding
Initialize the schema and seed data using PostgreSQL command line or a GUI tool:
```sql
CREATE DATABASE career_compass_ai;
\c career_compass_ai
\i database/schema.sql
\i database/seed_data.sql
```

### 3. Setup Environment Variables
Copy `.env.example` to `.env` in the root of the project:
```bash
cp .env.example .env
```
Open the `.env` file and fill in your Gemini API key, local database password, and Quiz API key:
- `GEMINI_API_KEY`: Obtain from Google AI Studio.
- `DB_PASSWORD`: Your local PostgreSQL postgres user password.
- `QUIZ_API_KEY`: Obtain from QuizAPI.io.

### 4. Setup Backend Environment & Dependencies
Create a virtual environment and install dependencies:
```bash
# In project root
python -m venv .venv
.venv\Scripts\activate      # For Windows
source .venv/bin/activate    # For macOS/Linux

pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv
```

### 5. Launch Backend Web Server
Run the FastAPI application:
```bash
python api/app.py
```
The server will start up at `http://127.0.0.1:8000`.

### 6. Setup React Frontend
Navigate to the React project folder, install packages, and launch the Vite development server:
```bash
cd frontend-react
npm install
npm run dev
```
The web application will open at `http://localhost:5173`.

### 7. Run Integration Test Suite
To verify the DB connector, classification accuracy, and session sandboxing:
```bash
# Run NLP classifier validations
python testing/run_tests.py

# Run API session state transition tests
python testing/verify_session_flow.py

# Run candidate sandbox isolation checks
python testing/verify_session_isolation.py
```

---

## Team Responsibilities

| Member | Ownership |
|--------|-----------|
| Member 1 (Database Lead) | schema.sql, seed_data.sql, all datasets in /datasets/, import_data.py |
| Member 2 (NLP + Recommendation Lead) | nlp_processor.py, recommendation_engine.py, test_cases.json, run_tests.py |

---

## Future Scope

- Add Google SDE, Amazon SDE, Flipkart SDE (same DB structure, new data)
- Add more roles: Data Scientist, DevOps Engineer, Embedded Engineer
- FastAPI backend with REST API endpoints
- React / Next.js frontend with dashboard
- pgvector integration for semantic search
- RAG-based AI assistant on top of this knowledge base

---

## Project Title Options

1. **CareerCompass AI** — NLP-Based Career Navigation System for Industry-Specific Roles *(recommended)*
2. **DreamPath** — Personalized Career Roadmap Generator
3. **RoleReady AI** — Qualification-Aware Career Preparation System
