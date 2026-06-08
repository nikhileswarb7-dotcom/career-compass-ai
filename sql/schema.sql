-- ============================================================
-- CareerCompass AI — 5-Layer PostgreSQL Schema
-- Version: 2.0 | Complete Project Layout Schema
-- ============================================================

-- CREATE DATABASE career_compass_ai;
-- \c career_compass_ai

CREATE SCHEMA IF NOT EXISTS career_compass_ai;
SET search_path TO career_compass_ai, public;

-- ============================================================
-- 1. INDUSTRY LAYER (Real-world employee profiles & transitions)
-- ============================================================

CREATE TABLE companies (
    company_id          INT PRIMARY KEY,
    company_name        VARCHAR(100) UNIQUE NOT NULL,
    industry            VARCHAR(100),
    company_type        VARCHAR(50) -- e.g. Product, Startup, MNC, Academic, Internal
);

CREATE TABLE roles (
    role_id             INT PRIMARY KEY,
    role_name           VARCHAR(100) UNIQUE NOT NULL,
    career_level        VARCHAR(50)
);

CREATE TABLE employee_profiles (
    profile_id          INT PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    role_id             INT REFERENCES roles(role_id) ON DELETE SET NULL,
    current_company     VARCHAR(100),
    experience_years    FLOAT,
    college             VARCHAR(200),
    degree              VARCHAR(200),
    previous_company    VARCHAR(100),
    career_path         TEXT,
    linkedin_url        VARCHAR(500),
    github_url          VARCHAR(500),
    career_stage        VARCHAR(100),
    company_tier        INT
);

CREATE TABLE education_profiles (
    education_id        INT PRIMARY KEY,
    profile_id          INT REFERENCES employee_profiles(profile_id) ON DELETE CASCADE,
    college             VARCHAR(200),
    degree              VARCHAR(200),
    field               VARCHAR(255)
);

CREATE TABLE career_transitions (
    transition_id       INT PRIMARY KEY,
    profile_id          INT REFERENCES employee_profiles(profile_id) ON DELETE CASCADE,
    source_company_id   INT REFERENCES companies(company_id) ON DELETE CASCADE,
    target_company_id   INT REFERENCES companies(company_id) ON DELETE CASCADE
);

-- ============================================================
-- 2. CAREER LAYER (Master skills and statistics)
-- ============================================================

CREATE TABLE skills_master (
    skill_id            INT PRIMARY KEY,
    skill_name          VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE employee_skills (
    profile_id          INT REFERENCES employee_profiles(profile_id) ON DELETE CASCADE,
    skill_id            INT REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (profile_id, skill_id)
);

CREATE TABLE role_skill_requirements (
    role_skill_id       INT PRIMARY KEY,
    company_role_id     INT, -- Maps to roles in system
    skill_id            INT REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    priority            VARCHAR(20) CHECK (priority IN ('High', 'Medium', 'Low'))
);

CREATE TABLE career_patterns (
    pattern_id          INT PRIMARY KEY,
    pattern_name        VARCHAR(200),
    frequency           INT,
    description         TEXT
);

CREATE TABLE skills_frequency (
    skill_id            INT PRIMARY KEY REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    skill_name          VARCHAR(100),
    frequency           INT,
    importance_score    INT
);

CREATE TABLE hiring_signals (
    signal_id           INT PRIMARY KEY,
    signal_name         VARCHAR(200),
    signal_type         VARCHAR(50), -- e.g. Skill, Education, Career
    weight              INT,
    description         TEXT
);

-- ============================================================
-- 3. HIRING LAYER (Company interview structures & criteria)
-- ============================================================

CREATE TABLE interview_rounds (
    round_id            INT PRIMARY KEY,
    company_role_id     INT,
    round_number        INT,
    round_name          VARCHAR(200),
    focus               VARCHAR(200),
    duration_minutes    INT,
    platform            VARCHAR(100),
    description         TEXT
);

CREATE TABLE interview_questions (
    question_id         INT PRIMARY KEY,
    company_role_id     INT,
    category            VARCHAR(100), -- DSA, DBMS, OS, HLD, LLD
    difficulty          VARCHAR(50) CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    question            TEXT NOT NULL,
    answer              TEXT,
    explanation         TEXT,
    tags                JSONB,
    frequency           VARCHAR(50)
);

CREATE TABLE company_interview_patterns (
    pattern_id          INT PRIMARY KEY,
    company_id          INT REFERENCES employee_companies(company_id) ON DELETE CASCADE,
    role_id             INT,
    typical_rounds_count INT,
    difficulty_rating   INT,
    notes               TEXT
);

CREATE TABLE hiring_criteria (
    criteria_id         INT PRIMARY KEY,
    company_role_id     INT,
    min_experience_years FLOAT,
    cgpa_cutoff         FLOAT,
    backlogs_allowed    BOOLEAN,
    notes               TEXT
);

-- ============================================================
-- 4. LEARNING LAYER (Curated learning assets & templates)
-- ============================================================

CREATE TABLE learning_resources (
    resource_id         INT PRIMARY KEY,
    title               VARCHAR(255) NOT NULL,
    resource_type       VARCHAR(50),
    topic               VARCHAR(100),
    skill_id            INT REFERENCES skills_master(skill_id) ON DELETE SET NULL,
    url                 TEXT,
    platform            VARCHAR(100),
    difficulty          VARCHAR(50),
    duration_hours      FLOAT,
    is_free             BOOLEAN DEFAULT TRUE,
    rating              FLOAT,
    notes               TEXT
);

CREATE TABLE roadmap_templates (
    template_id         INT PRIMARY KEY,
    qualification_id    INT,
    total_duration_months INT,
    overview            TEXT
);

CREATE TABLE projects_master (
    project_id          INT PRIMARY KEY,
    project_name        VARCHAR(200) NOT NULL,
    description         TEXT,
    difficulty          VARCHAR(50),
    estimated_days      INT,
    outcome             TEXT
);

CREATE TABLE project_skill_mapping (
    id                  INT PRIMARY KEY,
    project_id          INT REFERENCES projects_master(project_id) ON DELETE CASCADE,
    skill_id            INT REFERENCES skills_master(skill_id) ON DELETE CASCADE
);

-- ============================================================
-- 5. STUDENT LAYER (User profiles & personalized outputs)
-- ============================================================

CREATE TABLE student_profiles (
    student_id          INT PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    email               VARCHAR(200) UNIQUE,
    qualification_id    INT,
    branch              VARCHAR(100),
    cgpa                FLOAT,
    college             VARCHAR(200)
);

CREATE TABLE student_skills (
    id                  INT PRIMARY KEY,
    student_id          INT REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    skill_id            INT REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    proficiency         VARCHAR(50) CHECK (proficiency IN ('Beginner', 'Intermediate', 'Advanced'))
);

CREATE TABLE student_targets (
    id                  INT PRIMARY KEY,
    student_id          INT REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    company_role_id     INT
);

CREATE TABLE student_projects (
    id                  INT PRIMARY KEY,
    student_id          INT REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    project_id          INT REFERENCES projects_master(project_id) ON DELETE CASCADE,
    status              VARCHAR(50) CHECK (status IN ('Not Started', 'In Progress', 'Completed'))
);

CREATE TABLE skill_gaps (
    id                  INT PRIMARY KEY,
    student_id          INT REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    skill_id            INT REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    priority            VARCHAR(20)
);

CREATE TABLE generated_roadmaps (
    id                  INT PRIMARY KEY,
    student_id          INT REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    roadmap_json        JSONB
);

-- ============================================================
-- 6. INTERACTIVE SDE TRAINING & PROFILE OPTIMIZATION LAYER
-- ============================================================

CREATE TABLE stage_training_content (
    stage_id            INT PRIMARY KEY,
    video_playlist      JSONB NOT NULL,
    cheat_sheets        JSONB NOT NULL
);

CREATE TABLE stage_assessments (
    stage_id            INT PRIMARY KEY,
    mcqs                JSONB NOT NULL,
    coding_challenge    JSONB NOT NULL
);

CREATE TABLE profile_builder_templates (
    role_name           VARCHAR(100) PRIMARY KEY,
    resume_bullets      JSONB NOT NULL,
    linkedin_summary    TEXT NOT NULL,
    github_readme       TEXT NOT NULL
);

-- ============================================================
-- 7. SDE INTELLIGENCE DATASETS (Relational Expansion)
-- ============================================================

CREATE TABLE job_descriptions (
    jd_id                       INT PRIMARY KEY,
    company_id                  INT REFERENCES companies(company_id) ON DELETE CASCADE,
    role_id                     INT REFERENCES roles(role_id) ON DELETE CASCADE,
    experience_required_years   VARCHAR(50),
    salary_range                VARCHAR(50),
    description                 TEXT,
    responsibilities            JSONB,
    requirements                JSONB,
    created_at                  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interview_experiences (
    experience_id               INT PRIMARY KEY,
    company_id                  INT REFERENCES companies(company_id) ON DELETE CASCADE,
    role_id                     INT REFERENCES roles(role_id) ON DELETE CASCADE,
    candidate_name              VARCHAR(200),
    verdict                     VARCHAR(50),
    difficulty_rating           INT,
    experience_story            TEXT,
    tips                        TEXT,
    created_at                  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE skill_roadmaps (
    roadmap_id                  INT PRIMARY KEY,
    skill_id                    INT REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    level                       VARCHAR(50), -- Beginner, Intermediate, Advanced
    duration_weeks              INT,
    learning_goals              JSONB,
    recommended_resources       TEXT,
    milestone                   TEXT,
    created_at                  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE company_metadata (
    company_id          INT PRIMARY KEY REFERENCES companies(company_id) ON DELETE CASCADE,
    tier                INT,            -- e.g. 1, 2, 3
    hiring_bar_score    FLOAT,          -- selectivity rating
    target_cgpa         FLOAT,
    allow_backlogs      BOOLEAN,
    annual_hiring_count INT,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recommendation_audit_log (
    audit_id            SERIAL PRIMARY KEY,
    student_id          INT REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    session_id          UUID, -- references analysis_sessions/similar or null
    score_readiness     INT,
    score_skills        INT,
    score_projects      INT,
    score_interview     INT,
    score_profile       INT,
    score_company_fit   INT,
    missing_skills_count INT,
    recommended_projects_count INT,
    generated_at        TIMESTAMP DEFAULT NOW(),
    debug_message       TEXT
);
