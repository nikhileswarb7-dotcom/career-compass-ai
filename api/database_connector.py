# Database & CSV Connector - CareerCompass AI

import os
import csv
import psycopg2
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

# Load local .env file if it exists at the root of the workspace
dotenv_path = os.path.abspath(os.path.join(BASE_DIR, ".env"))
if os.path.exists(dotenv_path):
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Database connection credentials (loaded dynamically from environment)
db_port_str = os.environ.get("DB_PORT", "5432")
try:
    db_port = int(db_port_str) if db_port_str else 5432
except ValueError:
    db_port = 5432

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     db_port,
    "dbname":   os.environ.get("DB_NAME", "career_compass_ai"),
    "user":     os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "")
}

def read_csv_layer(layer_name: str, filename: str):
    csv_path = os.path.join(DB_DIR, layer_name, filename)
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        return None

def query_stats():
    """
    Fetches stats for the dashboard.
    Enforces PostgreSQL only.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for query_stats.")
    try:
        cur = conn.cursor()
        # Top colleges
        cur.execute("""
            SELECT college, COUNT(*) as count 
            FROM employee_profiles 
            WHERE college IS NOT NULL AND college != ''
            GROUP BY college 
            ORDER BY count DESC 
            LIMIT 5
        """)
        colleges = [{"college": r[0], "count": r[1]} for r in cur.fetchall()]
        
        # Skills frequency
        cur.execute("""
            SELECT skill_name, frequency, importance_score 
            FROM skills_frequency 
            ORDER BY frequency DESC 
            LIMIT 8
        """)
        skills = [{"skill_name": r[0], "frequency": r[1], "importance_score": r[2]} for r in cur.fetchall()]
        
        # Total profiles count
        cur.execute("SELECT COUNT(*) FROM employee_profiles")
        total_profiles = cur.fetchone()[0]
        
        # Average experience
        cur.execute("SELECT ROUND(AVG(experience_years)::numeric, 1) FROM employee_profiles")
        avg_exp = float(cur.fetchone()[0] or 0.0)
        
        cur.close()
        conn.close()
        return {
            "source": "PostgreSQL",
            "colleges": colleges,
            "skills": skills,
            "total_profiles": total_profiles,
            "avg_exp": avg_exp
        }
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in query_stats: {str(e)}")

def get_hiring_signals():
    """
    Fetches the top hiring signals. Enforces PostgreSQL only.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for get_hiring_signals.")
    try:
        cur = conn.cursor()
        cur.execute("SELECT signal_name, signal_type, weight, description FROM hiring_signals ORDER BY weight DESC LIMIT 15")
        signals = [{"name": r[0], "type": r[1], "weight": r[2], "description": r[3]} for r in cur.fetchall()]
        cur.close()
        conn.close()
        return signals
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_hiring_signals: {str(e)}")

import json

def get_stage_training(stage_id: int):
    """
    Fetches SDE training lecture video playlists and cheat sheets for a stage.
    Enforces PostgreSQL only.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError(f"Database connection is unavailable for get_stage_training({stage_id}).")
    try:
        cur = conn.cursor()
        cur.execute("SELECT video_playlist, cheat_sheets FROM stage_training_content WHERE stage_id = %s", (stage_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "source": "PostgreSQL",
                "stage_id": stage_id,
                "videos": row[0],
                "video_playlist": row[0],
                "materials": row[1],
                "cheat_sheets": row[1]
            }
        return None
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_stage_training({stage_id}): {str(e)}")

def get_stage_assessment(stage_id: int):
    """
    Fetches checkpoint multiple-choice questions and coding challenge templates for a stage.
    Enforces PostgreSQL only.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError(f"Database connection is unavailable for get_stage_assessment({stage_id}).")
    try:
        cur = conn.cursor()
        cur.execute("SELECT mcqs, coding_challenge FROM stage_assessments WHERE stage_id = %s", (stage_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "source": "PostgreSQL",
                "stage_id": stage_id,
                "mcqs": row[0],
                "coding": row[1]
            }
        return None
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_stage_assessment({stage_id}): {str(e)}")

def get_profile_builder_template(role_name: str):
    """
    Fetches LinkedIn summaries, resume bullet points, and GitHub readme templates.
    Enforces PostgreSQL only.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError(f"Database connection is unavailable for get_profile_builder_template({role_name}).")
    try:
        cur = conn.cursor()
        cur.execute("SELECT resume_bullets, linkedin_summary, github_readme FROM profile_builder_templates WHERE LOWER(role_name) = %s", (role_name.lower().strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "source": "PostgreSQL",
                "role_name": role_name,
                "resume_bullets": row[0],
                "linkedin_summary": row[1],
                "github_readme": row[2]
            }
        return None
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_profile_builder_template({role_name}): {str(e)}")


def get_company_id_by_name(company_name: str):
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for get_company_id_by_name.")
    try:
        cur = conn.cursor()
        cur.execute("SELECT company_id FROM companies WHERE LOWER(company_name) = %s", (company_name.lower().strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return row[0]
        raise ValueError(f"Company '{company_name}' not found in database.")
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_company_id_by_name: {str(e)}")


def get_role_id_by_name(role_name: str):
    # Normalize common role aliases to match canonical names in the database
    role_clean = role_name.strip().lower()
    aliases = {
        "software development engineer": "software development engineer (sde)",
        "sde": "software development engineer (sde)",
        "backend engineer": "backend developer",
        "frontend engineer": "frontend developer",
        "full stack engineer": "full stack developer",
        "site reliability engineer": "site reliability engineer (sre)",
        "sre": "site reliability engineer (sre)",
        "sdet": "sdet (software development engineer in test)",
        "software development engineer in test": "sdet (software development engineer in test)",
        "apm": "associate product manager (apm)",
        "associate product manager": "associate product manager (apm)"
    }
    canonical_role_name = aliases.get(role_clean, role_clean)

    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for get_role_id_by_name.")
    try:
        cur = conn.cursor()
        cur.execute("SELECT role_id FROM roles WHERE LOWER(role_name) = %s", (canonical_role_name.lower().strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return row[0]
        raise ValueError(f"Role '{role_name}' (canonical: '{canonical_role_name}') not found in database.")
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_role_id_by_name: {str(e)}")



def get_company_job_description(company_name: str, role_name: str):
    company_id = get_company_id_by_name(company_name)
    role_id = get_role_id_by_name(role_name)
    
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for get_company_job_description.")
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT jd_id, experience_required_years, salary_range, description, responsibilities, requirements 
            FROM job_descriptions 
            WHERE company_id = %s AND role_id = %s
        """, (company_id, role_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "source": "PostgreSQL",
                "jd_id": row[0],
                "company_id": company_id,
                "role_id": role_id,
                "experience_required_years": row[1],
                "salary_range": row[2],
                "description": row[3],
                "responsibilities": row[4] if isinstance(row[4], list) else json.loads(row[4]),
                "requirements": row[5] if isinstance(row[5], list) else json.loads(row[5])
            }
        return None
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_company_job_description: {str(e)}")


def get_company_interview_experiences(company_name: str):
    company_id = get_company_id_by_name(company_name)
    
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for get_company_interview_experiences.")
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT experience_id, role_id, candidate_name, verdict, difficulty_rating, experience_story, tips 
            FROM interview_experiences 
            WHERE company_id = %s
        """, (company_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{
            "source": "PostgreSQL",
            "experience_id": r[0],
            "company_id": company_id,
            "role_id": r[1],
            "candidate_name": r[2],
            "verdict": r[3],
            "difficulty_rating": r[4],
            "experience_story": r[5],
            "tips": r[6]
        } for r in rows]
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_company_interview_experiences: {str(e)}")


def get_skill_roadmap_details(skill_name: str):
    skill_id = None
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT skill_id FROM skills WHERE LOWER(skill_name) = LOWER(%s) LIMIT 1", (skill_name.strip(),))
            row = cur.fetchone()
            if row:
                skill_id = row[0]
            cur.close()
        except Exception:
            pass

    # Fallback to CSV search if skill_id not found in DB
    if not skill_id:
        try:
            skills_csv = read_csv_layer("career_layer", "skills_master.csv")
            for s in skills_csv:
                if s["skill_name"].lower().strip() == skill_name.lower().strip():
                    skill_id = int(s["skill_id"])
                    break
        except Exception:
            pass

    if not skill_id:
        skill_id = abs(hash(skill_name.strip())) % 10000 + 1000

    res = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT roadmap_id, level, duration_weeks, learning_goals, recommended_resources, milestone 
                FROM skill_roadmaps 
                WHERE skill_id = %s
                ORDER BY CASE 
                    WHEN LOWER(level) = 'beginner' THEN 1
                    WHEN LOWER(level) = 'intermediate' THEN 2
                    WHEN LOWER(level) = 'advanced' THEN 3
                    ELSE 4
                END
            """, (skill_id,))
            rows = cur.fetchall()
            cur.close()
            for r in rows:
                res.append({
                    "source": "PostgreSQL",
                    "roadmap_id": r[0],
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "level": r[1],
                    "duration_weeks": r[2],
                    "learning_goals": r[3] if isinstance(r[3], list) else json.loads(r[3]),
                    "recommended_resources": r[4],
                    "milestone": r[5]
                })
        except Exception as e:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    if not res:
        # Generate dynamic 3-stage syllabus fallback
        levels = [
            {
                "level": "Beginner",
                "duration_weeks": 4,
                "learning_goals": [
                    f"Understand syntax, core concepts and setup for {skill_name}",
                    f"Build simple programs/scripts using {skill_name}",
                    f"Learn fundamental libraries and tools associated with {skill_name}"
                ],
                "recommended_resources": f"{skill_name} crash course, Official {skill_name} documentation",
                "milestone": f"Complete 5 beginner console or simple projects in {skill_name}."
            },
            {
                "level": "Intermediate",
                "duration_weeks": 6,
                "learning_goals": [
                    f"Explore concurrency, advanced data structures, or patterns in {skill_name}",
                    f"Build a robust CRUD or backend service with {skill_name}",
                    f"Learn unit testing and debugging tools for {skill_name}"
                ],
                "recommended_resources": f"Intermediate {skill_name} programming course, GitHub boilerplate projects",
                "milestone": f"Build and deploy a scalable, tested application using {skill_name}."
            },
            {
                "level": "Advanced",
                "duration_weeks": 8,
                "learning_goals": [
                    f"Performance optimization, memory profiling, and tuning in {skill_name}",
                    f"Design and architect distributed scale architectures using {skill_name}",
                    f"Conduct code reviews and follow production design patterns for {skill_name}"
                ],
                "recommended_resources": f"Advanced {skill_name} design guides, Production scale open-source repos",
                "milestone": f"Optimize performance, latency, and load throughput of a {skill_name}-based system by 30%."
            }
        ]
        
        for idx, lvl in enumerate(levels):
            res.append({
                "source": "Dynamic Fallback",
                "roadmap_id": skill_id * 10 + idx,  # Unique mock roadmap_id
                "skill_id": skill_id,
                "skill_name": skill_name,
                "level": lvl["level"],
                "duration_weeks": lvl["duration_weeks"],
                "learning_goals": lvl["learning_goals"],
                "recommended_resources": lvl["recommended_resources"],
                "milestone": lvl["milestone"]
            })
            
    return res

def create_analysis_session(student_id: int, target_company: str, target_role: str) -> str:
    """
    Creates an analysis session linked to a student_id.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO analysis_sessions (student_id, target_company, target_role, status)
            VALUES (%s, %s, %s, 'uploaded')
            RETURNING session_id
        """, (student_id, target_company, target_role))
        session_id = str(cur.fetchone()[0])
        conn.commit()
        cur.close()
        conn.close()
        return session_id
    except Exception as e:
        if conn: conn.close()
        raise e

def get_analysis_session(session_id: str) -> dict:
    """
    Retrieves analysis session details and progress status.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT session_id, student_id, target_company, target_role, status, created_at
            FROM analysis_sessions
            WHERE session_id = %s
        """, (session_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "session_id": str(row[0]),
                "student_id": row[1],
                "target_company": row[2],
                "target_role": row[3],
                "status": row[4],
                "created_at": row[5]
            }
        return None
    except Exception:
        if conn: conn.close()
        return None

def update_analysis_session_status(session_id: str, status: str) -> bool:
    """
    Updates the progress status of an analysis session.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE analysis_sessions
            SET status = %s
            WHERE session_id = %s
        """, (status, session_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        if conn: conn.close()
        return False

def get_career_transitions():
    """
    Fetches common career transitions.
    Enforces PostgreSQL only.
    """
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection is unavailable for get_career_transitions.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("""
            SELECT source_company, target_company, COUNT(*) as count
            FROM v_career_transitions
            GROUP BY source_company, target_company
            ORDER BY count DESC
            LIMIT 15
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"path": f"{r[0]} → {r[1]}", "count": r[2]} for r in rows]
    except Exception as e:
        if conn: conn.close()
        raise RuntimeError(f"Database query failed in get_career_transitions: {str(e)}")


