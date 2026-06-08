-- ============================================================
--  CareerCompass AI — PostgreSQL Schema
--  Target: Blinkit SDE Career Navigation System
--  Version: 1.0 | Designed for scalability across roles/companies
-- ============================================================

-- Run this first in psql or pgAdmin Query Tool:
-- CREATE DATABASE career_compass_ai;
-- \c career_compass_ai

CREATE SCHEMA IF NOT EXISTS career_compass_ai;
SET search_path TO career_compass_ai, public;

-- ============================================================
-- LAYER 1: COMPANY KNOWLEDGE
-- ============================================================

CREATE TABLE companies (
    company_id          SERIAL PRIMARY KEY,
    company_name        VARCHAR(100) UNIQUE NOT NULL,
    industry            VARCHAR(100),
    founded_year        INT,
    description         TEXT,
    mission             TEXT,
    work_culture        TEXT,
    tech_stack          JSONB,         -- e.g. ["Java","Kafka","MySQL","Redis","AWS"]
    hiring_process      JSONB,         -- e.g. ["OA","DSA Round","LLD","HLD","HR"]
    salary_range        JSONB,         -- e.g. {"intern":"20k-50k/mo","sde1":"10-18 LPA"}
    career_growth       TEXT,          -- Trainee → SDE-1 → SDE-2 → Senior → TL
    engineering_blog_url TEXT,
    company_type        VARCHAR(50),   -- Merged from employee_companies
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- LAYER 2: ROLE KNOWLEDGE
-- ============================================================

CREATE TABLE roles (
    role_id             SERIAL PRIMARY KEY,
    role_name           VARCHAR(100) UNIQUE NOT NULL,
    description         TEXT,
    responsibilities    JSONB,         -- ["Backend Dev","API Design","Scalability"]
    experience_levels   JSONB,         -- ["Intern","SDE-1","SDE-2","Senior SDE","Tech Lead"]
    career_level        VARCHAR(50),   -- Merged from role_specializations
    created_at          TIMESTAMP DEFAULT NOW()
);

-- Maps a company to a specific role (e.g. Blinkit → SDE)
CREATE TABLE company_roles (
    company_role_id     SERIAL PRIMARY KEY,
    company_id          INT REFERENCES companies(company_id) ON DELETE CASCADE,
    role_id             INT REFERENCES roles(role_id) ON DELETE CASCADE,
    cgpa_cutoff         FLOAT DEFAULT 0.0,
    backlogs_allowed    BOOLEAN DEFAULT TRUE,
    notes               TEXT,
    UNIQUE(company_id, role_id)
);

-- ============================================================
-- LAYER 3: QUALIFICATION LEVELS
-- ============================================================

CREATE TABLE qualifications (
    qualification_id        SERIAL PRIMARY KEY,
    qualification_name      VARCHAR(100) UNIQUE NOT NULL,
    level_order             INT,    -- 1=1st Year, 2=2nd, ..., 7=Junior Engineer
    available_time          VARCHAR(50),    -- "High" / "Medium" / "Low"
    learning_speed          VARCHAR(50),    -- "Slow" / "Medium" / "Fast" / "Very Fast"
    urgency                 VARCHAR(50),    -- "Low" / "Medium" / "High" / "Critical"
    typical_duration_months INT,            -- months until placement-ready
    description             TEXT
);

-- ============================================================
-- LAYER 4: SKILLS
-- ============================================================

CREATE TABLE skills (
    skill_id        SERIAL PRIMARY KEY,
    skill_name      VARCHAR(100) UNIQUE NOT NULL,
    category        VARCHAR(100),   -- "Programming" / "Core CS" / "Backend" / "Cloud" / "DevOps"
    description     TEXT,
    difficulty      VARCHAR(50)     -- "Beginner" / "Intermediate" / "Advanced"
);

-- Skills required for a specific company_role
CREATE TABLE role_skills (
    role_skill_id   SERIAL PRIMARY KEY,
    company_role_id INT REFERENCES company_roles(company_role_id) ON DELETE CASCADE,
    skill_id        INT REFERENCES skills(skill_id) ON DELETE CASCADE,
    priority        VARCHAR(20) CHECK (priority IN ('High','Medium','Low')),
    notes           TEXT,
    UNIQUE(company_role_id, skill_id)
);

-- ============================================================
-- LAYER 5: CAREER ROADMAP
-- ============================================================

-- One roadmap per (qualification × company_role) combination
CREATE TABLE roadmaps (
    roadmap_id              SERIAL PRIMARY KEY,
    qualification_id        INT REFERENCES qualifications(qualification_id) ON DELETE CASCADE,
    company_role_id         INT REFERENCES company_roles(company_role_id) ON DELETE CASCADE,
    total_duration_months   INT,
    overview                TEXT,
    created_at              TIMESTAMP DEFAULT NOW(),
    UNIQUE(qualification_id, company_role_id)
);

-- Stages within a roadmap (sequential steps)
CREATE TABLE roadmap_stages (
    stage_id        SERIAL PRIMARY KEY,
    roadmap_id      INT REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE,
    stage_number    INT,
    stage_title     VARCHAR(200),
    duration_weeks  INT,
    focus_area      TEXT,
    learning_goals  JSONB,          -- ["Understand DBMS basics","Write complex SQL queries"]
    weekly_hours    INT,
    milestone       TEXT,           -- what student achieves at the end of this stage
    UNIQUE(roadmap_id, stage_number)
);

-- Skills covered in each roadmap stage
CREATE TABLE stage_skills (
    id          SERIAL PRIMARY KEY,
    stage_id    INT REFERENCES roadmap_stages(stage_id) ON DELETE CASCADE,
    skill_id    INT REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- ============================================================
-- LAYER 6: PROJECTS
-- ============================================================

CREATE TABLE projects (
    project_id          SERIAL PRIMARY KEY,
    project_name        VARCHAR(200) NOT NULL,
    description         TEXT,
    difficulty          VARCHAR(50),
    estimated_days      INT,
    skills_covered      JSONB,          -- ["Java","Spring Boot","MySQL"]
    github_template_url TEXT,
    outcome             TEXT            -- what the student demonstrates by completing this
);

-- Link projects to specific roadmap stages
CREATE TABLE stage_projects (
    id          SERIAL PRIMARY KEY,
    stage_id    INT REFERENCES roadmap_stages(stage_id) ON DELETE CASCADE,
    project_id  INT REFERENCES projects(project_id) ON DELETE CASCADE
);

-- ============================================================
-- LAYER 7: LEARNING RESOURCES
-- ============================================================

CREATE TABLE resources (
    resource_id     SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    resource_type   VARCHAR(50) CHECK (resource_type IN ('Video','Playlist','Course','Article','Documentation','Practice Platform')),
    topic           VARCHAR(100),
    skill_id        INT REFERENCES skills(skill_id) ON DELETE SET NULL,
    url             TEXT,
    platform        VARCHAR(100),   -- "YouTube","Udemy","LeetCode","GeeksForGeeks"
    difficulty      VARCHAR(50),
    duration_hours  FLOAT,
    is_free         BOOLEAN DEFAULT TRUE,
    rating          FLOAT,          -- community rating 1-5
    notes           TEXT
);

-- Resources recommended at specific roadmap stages
CREATE TABLE stage_resources (
    id          SERIAL PRIMARY KEY,
    stage_id    INT REFERENCES roadmap_stages(stage_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources(resource_id) ON DELETE CASCADE
);

-- ============================================================
-- LAYER 8: CAREER GUIDANCE (Resume / LinkedIn / GitHub)
-- ============================================================

CREATE TABLE resume_guidance (
    resume_id           SERIAL PRIMARY KEY,
    qualification_id    INT REFERENCES qualifications(qualification_id) ON DELETE CASCADE,
    required_sections   JSONB,  -- ["Education","Skills","Projects","Internships"]
    optional_sections   JSONB,  -- ["Achievements","Certifications","Publications"]
    ats_tips            JSONB,
    common_mistakes     JSONB,
    word_limit          VARCHAR(50),
    example_summary     TEXT,
    template_url        TEXT
);

CREATE TABLE linkedin_guidance (
    linkedin_id         SERIAL PRIMARY KEY,
    qualification_id    INT REFERENCES qualifications(qualification_id) ON DELETE CASCADE,
    headline_examples   JSONB,
    about_examples      JSONB,
    featured_section    TEXT,
    skills_to_list      JSONB,
    networking_tips     JSONB,
    connection_targets  TEXT,
    profile_checklist   JSONB
);

CREATE TABLE github_guidance (
    github_id               SERIAL PRIMARY KEY,
    qualification_id        INT REFERENCES qualifications(qualification_id) ON DELETE CASCADE,
    profile_readme_tips     TEXT,
    required_repos          JSONB,  -- ["food-delivery-backend","url-shortener"]
    repo_naming_standards   TEXT,
    commit_standards        TEXT,
    readme_template         TEXT,
    contribution_strategy   TEXT,
    profile_checklist       JSONB
);

-- ============================================================
-- LAYER 9: INTERVIEW QUESTIONS
-- ============================================================

CREATE TABLE interview_questions (
    question_id     SERIAL PRIMARY KEY,
    company_role_id INT REFERENCES company_roles(company_role_id) ON DELETE SET NULL,
    category        VARCHAR(100) CHECK (category IN ('DSA','DBMS','OS','CN','System Design','Behavioral','Java','Spring Boot')),
    difficulty      VARCHAR(50)  CHECK (difficulty IN ('Easy','Medium','Hard')),
    question        TEXT NOT NULL,
    answer          TEXT,
    explanation     TEXT,
    tags            JSONB,
    frequency       VARCHAR(50)  -- "Very Common","Common","Rare"
);

-- ============================================================
-- LAYER 10: USER PROFILE
-- ============================================================

CREATE TABLE students (
    student_id              SERIAL PRIMARY KEY,
    name                    VARCHAR(200),
    email                   VARCHAR(200) UNIQUE,
    qualification_id        INT REFERENCES qualifications(qualification_id),
    branch                  VARCHAR(100),
    cgpa                    FLOAT,
    college                 VARCHAR(200),
    target_company_role_id  INT REFERENCES company_roles(company_role_id),
    linkedin_url            VARCHAR(500),
    github_username         VARCHAR(100),
    resume_text             TEXT,
    created_at              TIMESTAMP DEFAULT NOW()
);

CREATE TABLE student_skills (
    id          SERIAL PRIMARY KEY,
    student_id  INT REFERENCES students(student_id) ON DELETE CASCADE,
    skill_id    INT REFERENCES skills(skill_id) ON DELETE CASCADE,
    proficiency VARCHAR(50) CHECK (proficiency IN ('Beginner','Intermediate','Advanced')),
    UNIQUE(student_id, skill_id)
);

CREATE TABLE student_progress (
    progress_id     SERIAL PRIMARY KEY,
    student_id      INT REFERENCES students(student_id) ON DELETE CASCADE,
    stage_id        INT REFERENCES roadmap_stages(stage_id) ON DELETE CASCADE,
    status          VARCHAR(50) CHECK (status IN ('Not Started','In Progress','Completed')),
    completion_pct  INT DEFAULT 0,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    UNIQUE(student_id, stage_id)
);

-- ============================================================
-- LAYER 11: CAREER ASSESSMENT CACHE & ANALYSIS SESSIONS
-- ============================================================

CREATE TABLE career_assessments (
    assessment_id               SERIAL PRIMARY KEY,
    student_id                  INT REFERENCES students(student_id) ON DELETE CASCADE,
    readiness_score             INT,    -- 0–100 overall
    skill_score                 INT,
    project_score               INT,
    resume_score                INT,
    linkedin_score              INT,
    github_score                INT,
    interview_score             INT,
    missing_skills              JSONB,
    recommended_projects        JSONB,
    next_30_day_plan            JSONB,
    estimated_months_to_ready   INT,
    generated_at                TIMESTAMP DEFAULT NOW()
);

CREATE TABLE analysis_sessions (
    session_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      INT REFERENCES students(student_id) ON DELETE CASCADE,
    target_company  VARCHAR(100) NOT NULL,
    target_role     VARCHAR(100) NOT NULL,
    status          VARCHAR(50) DEFAULT 'uploaded',
    created_at      TIMESTAMP DEFAULT NOW()
);


-- ============================================================
-- LAYER 12: NEW INTELLIGENCE DATASETS (Relational Expansion)
-- ============================================================

CREATE TABLE job_descriptions (
    jd_id                       SERIAL PRIMARY KEY,
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
    experience_id               SERIAL PRIMARY KEY,
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
    roadmap_id                  SERIAL PRIMARY KEY,
    skill_id                    INT REFERENCES skills(skill_id) ON DELETE CASCADE,
    level                       VARCHAR(50), -- Beginner, Intermediate, Advanced
    duration_weeks              INT,
    learning_goals              JSONB,
    recommended_resources       TEXT,
    milestone                   TEXT,
    created_at                  TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- LAYER 13: COMPANY METADATA & RECOMMENDATION AUDIT LOG
-- ============================================================

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
    student_id          INT REFERENCES students(student_id) ON DELETE CASCADE,
    session_id          UUID REFERENCES analysis_sessions(session_id) ON DELETE CASCADE,
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

-- ============================================================
-- LAYER 14: INTERACTIVE TRAINING & PROFILE OPTIMIZATION
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

