# CareerCompass AI 🧭
### NLP-Based Career Navigation & Preparation System for Industry-Specific Roles

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## 📖 Project Overview

**CareerCompass AI** is a personalized career navigation and preparation platform designed to guide students from their current qualification level to industry readiness for specific software development roles (e.g., SDE at target companies like Blinkit). 

Instead of general career advice, CareerCompass AI runs qualification-aware gap analyses and builds tailored, time-sensitive roadmaps. Whether a student is in their 1st year of college or a final-year graduate, the system adjusts milestones, projects, interview questions, and prep tasks to match their specific timeline.

---

## 🚀 Key Features

*   **Dynamic Profile Parsing**: Ingests and processes resume text, LinkedIn profile text, and GitHub handles to build a comprehensive map of a candidate's background.
*   **NLP Entity Extraction**: Uses Google Gemini LLM API (with rule-based heuristics as a fail-safe) to parse candidate profiles and target roles from natural language query submissions.
*   **Time-Sensitive Roadmaps**: Dynamically partitions SDE prep tracks into sequential stages (e.g., Foundations, Advanced backend/frontend development, Systems Design) tailored to candidate qualification.
*   **Readiness Scoring Engine**: Computes a detailed readiness score mapping the student's skills against target role requirements.
*   **Curated Learning Tracks & Assessments**: Matches each roadmap stage with specific video playlist training content, cheat sheets, MCQs, and coding challenges.
*   **Interactive AI Mentor**: Provides real-time guidance on resumes, portfolio projects, LinkedIn setup, and GitHub presence.
*   **Premium Glassmorphic UI**: Single-Page Application (SPA) dashboard containing interactive metrics, gap analysis visualizations, chat drawers, and step-by-step roadmaps.

---

## 🏗️ System Architecture

CareerCompass AI is structured with a decoupled client-server architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                      │
│     (Glassmorphic dashboard, roadmap views, chat)       │
└────────────────────────────┬────────────────────────────┘
                             │ REST HTTP
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Web Server                   │
│          (Endpoints, routes, and controllers)           │
└──────┬─────────────────────┬─────────────────────┬──────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  AI Engine   │      │  ML Pipeline │      │  PostgreSQL  │
│  (Gemini +   │      │  (Affinity   │      │   Database   │
│  Heuristics) │      │  Clustering) │      │  (Core SOT)  │
└──────────────┘      └──────────────┘      └──────────────┘
```

The system uses **PostgreSQL** as the single source of truth (SOT) for storing companies, roles, roadmaps, checkpoints, and candidates' session histories.

---

## 🤖 AI Architecture (NLP Processor)

The system features an **NLP Classification Pipeline** (`ai_engine/nlp/nlp_processor.py`) that parses natural language queries:
1. **Model**: Google Gemini SDK model (`gemini-2.5` or `gemini-1.5-flash`).
2. **Intent Parsing**: Extracts candidate parameters: `qualification`, `skills`, `target_company`, and `target_role`.
3. **Robust Fallback**: If LLM API limits are reached, the system falls back to a deterministic regex-based entity keyword classifier.

---

## 📈 ML Architecture (Affinities & Classifiers)

Candidate skills are analyzed through a series of local **ML pipelines** (`ai_engine/similarity/`):
*   **Profile Vectorization**: Transforms candidate skills into numerical feature representations using a TF-IDF bag-of-words schema.
*   **Affinity Pipelines**: Scikit-learn pipelines load pre-trained `.joblib` affinity models to calculate role alignment across different engineering paths (Frontend, Backend, General SDE).
*   **Skill Assessor**: Maps candidate competencies against target requirements to calculate priority-ordered gaps.

---

## 🗄️ Knowledge Layer

The database schema (`database/schema.sql`) represents a multi-tiered knowledge base:
*   **Career Layer**: Holds role skill requirements and skill frequency distributions.
*   **Hiring Layer**: Stores target company parameters, job descriptions, and user interview experiences.
*   **Learning Layer**: Defines stages, learning goals, milestones, mcqs, coding templates, and curated resources.

---

## 🛠️ Technology Stack

*   **Frontend**: React (JS/JSX), Vite, Chart.js / Canvas, Vanilla CSS (Premium responsive custom style sheet).
*   **Backend**: Python 3.10+, FastAPI, Uvicorn.
*   **Database**: PostgreSQL 14+, Psycopg2.
*   **AI/ML**: Google Generative AI SDK, Scikit-learn, Joblib.

---

## 📦 Installation & Setup

### 1. Database Creation & Seeding
Ensure you have a local PostgreSQL instance running. Initialize the schema and seed data:
```sql
CREATE DATABASE career_compass_ai;
\c career_compass_ai
\i database/schema.sql
\i database/seed_data.sql
```

### 2. Setup Environment Variables
Copy `.env.example` to `.env` in the root of the project:
```bash
cp .env.example .env
```
Open the `.env` file and fill in your details:
*   `GEMINI_API_KEY`: Your Google Gemini API key.
*   `DB_PASSWORD`: Your local PostgreSQL password.
*   `QUIZ_API_KEY`: Your QuizAPI key (optional).

### 3. Setup Backend Environment & Dependencies
Create a virtual environment and install backend requirements:
```bash
# From project root
python -m venv .venv
.venv\Scripts\activate      # For Windows Powershell/CMD
source .venv/bin/activate    # For macOS/Linux

pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv
```

### 4. Run Backend FastAPI Server
Start the backend web server:
```bash
python api/app.py
```
The backend server will run at `http://127.0.0.1:8000`.

### 5. Setup React Frontend
Navigate to the frontend folder, install dependencies, and run Vite:
```bash
cd frontend-react
npm install
npm run dev
```
The web application will open at `http://localhost:5173`.

---

## 🧪 Testing & Verification

Run the integration and regression test suites to verify system modules:
```bash
# Run NLP classifier & gap validation tests
python testing/run_tests.py

# Run API session state transition tests
python testing/verify_session_flow.py

# Run database schema sandbox isolation checks
python testing/verify_session_isolation.py
```

---

## 🗺️ Future Roadmap

*   **Expanded Role Indexing**: Add support for DevOps, Site Reliability, and Product Management tracks.
*   **Semantic Matching**: Integrate `pgvector` in PostgreSQL for vector similarity searches over projects and resume profiles.
*   **Real-time Coding Playgrounds**: Introduce interactive in-browser compiler endpoints for SDE checkpoint challenges.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
