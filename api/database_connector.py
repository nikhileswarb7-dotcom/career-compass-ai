# Database & CSV Connector - CareerCompass AI

import os
import csv
import psycopg2
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

# Database connection credentials (default local postgres)
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "career_compass_ai",
    "user":     "postgres",
    "password": "Nikhil@2824"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        return None

def read_csv_layer(layer_folder, filename):
    filepath = os.path.join(DB_DIR, layer_folder, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def query_stats():
    """
    Fetches stats for the dashboard.
    Attempts PostgreSQL first, then falls back to CSV files.
    """
    conn = get_db_connection()
    if conn:
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
            # Fallback to CSV on error
            pass
            
    # Graceful Fallback: Query CSV files directly
    profiles = read_csv_layer("industry_layer", "employee_profiles.csv")
    skills_freq = read_csv_layer("career_layer", "skill_frequency.csv")
    
    # 1. Total profiles
    total_profiles = len(profiles)
    
    # 2. Avg exp
    exp_sum = sum(float(p["experience_years"]) for p in profiles if p["experience_years"])
    avg_exp = round(exp_sum / total_profiles, 1) if total_profiles else 0.0
    
    # 3. Top colleges
    college_counts = {}
    for p in profiles:
        col = p["college"]
        if col:
            college_counts[col] = college_counts.get(col, 0) + 1
    colleges = [{"college": k, "count": v} for k, v in sorted(college_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    # 4. Top skills
    skills = []
    for sf in sorted(skills_freq, key=lambda x: int(x["frequency"]), reverse=True)[:8]:
        skills.append({
            "skill_name": sf["skill_name"],
            "frequency": int(sf["frequency"]),
            "importance_score": int(sf["importance_score"])
        })
        
    return {
        "source": "CSV Files",
        "colleges": colleges,
        "skills": skills,
        "total_profiles": total_profiles,
        "avg_exp": avg_exp
    }

def get_hiring_signals():
    """
    Fetches the top hiring signals.
    """
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT signal_name, signal_type, weight, description FROM hiring_signals ORDER BY weight DESC LIMIT 15")
            signals = [{"name": r[0], "type": r[1], "weight": r[2], "description": r[3]} for r in cur.fetchall()]
            cur.close()
            conn.close()
            return signals
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    signals_csv = read_csv_layer("career_layer", "hiring_signals.csv")
    return [{"name": r["signal_name"], "type": r["signal_type"], "weight": int(r["weight"]), "description": r["description"]} for r in signals_csv]

import json

def get_stage_training(stage_id: int):
    """
    Fetches SDE training lecture video playlists and cheat sheets for a stage.
    Attempts PostgreSQL first, then falls back to CSV.
    """
    conn = get_db_connection()
    if conn:
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
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    csv_data = read_csv_layer("learning_layer", "stage_training_content.csv")
    for r in csv_data:
        if int(r["stage_id"]) == stage_id:
            v_list = json.loads(r["video_playlist"])
            c_sheets = json.loads(r["cheat_sheets"])
            return {
                "source": "CSV Files",
                "stage_id": stage_id,
                "videos": v_list,
                "video_playlist": v_list,
                "materials": c_sheets,
                "cheat_sheets": c_sheets
            }
    return None

def get_stage_assessment(stage_id: int):
    """
    Fetches checkpoint multiple-choice questions and coding challenge templates for a stage.
    Attempts PostgreSQL first, then falls back to CSV.
    """
    conn = get_db_connection()
    if conn:
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
        except Exception:
            if conn: conn.close()
            
    # Fallback to JSON
    filepath = os.path.join(DB_DIR, "learning_layer", "stage_assessments.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                for r in json_data:
                    if int(r["stage_id"]) == stage_id:
                        return {
                            "source": "JSON Fallback",
                            "stage_id": stage_id,
                            "mcqs": r["mcqs"],
                            "coding": r["coding_challenge"]
                        }
        except Exception:
            pass
    return None

def get_profile_builder_template(role_name: str):
    """
    Fetches LinkedIn summaries, resume bullet points, and GitHub readme templates.
    Attempts PostgreSQL first, then falls back to CSV.
    """
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT resume_bullets, linkedin_summary, github_readme FROM profile_builder_templates WHERE role_name = %s", (role_name,))
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
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    csv_data = read_csv_layer("career_layer", "profile_builder_templates.csv")
    for r in csv_data:
        if r["role_name"].lower() == role_name.lower():
            return {
                "source": "CSV Files",
                "role_name": r["role_name"],
                "resume_bullets": json.loads(r["resume_bullets"]),
                "linkedin_summary": r["linkedin_summary"],
                "github_readme": r["github_readme"]
            }
    return None


def get_company_id_by_name(company_name: str):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT company_id FROM companies WHERE LOWER(company_name) = %s", (company_name.lower(),))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return row[0]
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    companies = read_csv_layer("industry_layer", "companies.csv")
    for c in companies:
        if c["company_name"].lower() == company_name.lower():
            return int(c["company_id"])
    return 1  # Default fallback


def get_role_id_by_name(role_name: str):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT role_id FROM roles WHERE LOWER(role_name) = %s", (role_name.lower(),))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return row[0]
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    roles = read_csv_layer("industry_layer", "roles.csv")
    for r in roles:
        if r["role_name"].lower() == role_name.lower():
            return int(r["role_id"])
    return 102  # Default fallback (SDE I)


def get_company_job_description(company_name: str, role_name: str):
    company_id = get_company_id_by_name(company_name)
    role_id = get_role_id_by_name(role_name)
    
    conn = get_db_connection()
    if conn:
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
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    csv_data = read_csv_layer("hiring_layer", "job_descriptions.csv")
    for r in csv_data:
        if int(r["company_id"]) == company_id and int(r["role_id"]) == role_id:
            return {
                "source": "CSV Files",
                "jd_id": int(r["jd_id"]),
                "company_id": company_id,
                "role_id": role_id,
                "experience_required_years": r["experience_required_years"],
                "salary_range": r["salary_range"],
                "description": r["description"],
                "responsibilities": json.loads(r["responsibilities"]),
                "requirements": json.loads(r["requirements"])
            }
            
    # Role fallback: try to find any JD for this company
    for r in csv_data:
        if int(r["company_id"]) == company_id:
            return {
                "source": "CSV Files (Role Fallback)",
                "jd_id": int(r["jd_id"]),
                "company_id": company_id,
                "role_id": int(r["role_id"]),
                "experience_required_years": r["experience_required_years"],
                "salary_range": r["salary_range"],
                "description": r["description"],
                "responsibilities": json.loads(r["responsibilities"]),
                "requirements": json.loads(r["requirements"])
            }
    return None


def get_company_interview_experiences(company_name: str):
    company_id = get_company_id_by_name(company_name)
    
    conn = get_db_connection()
    if conn:
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
            if rows:
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
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    csv_data = read_csv_layer("hiring_layer", "interview_experiences.csv")
    exps = []
    for r in csv_data:
        if int(r["company_id"]) == company_id:
            exps.append({
                "source": "CSV Files",
                "experience_id": int(r["experience_id"]),
                "company_id": company_id,
                "role_id": int(r["role_id"]),
                "candidate_name": r["candidate_name"],
                "verdict": r["verdict"],
                "difficulty_rating": int(r["difficulty_rating"]),
                "experience_story": r["experience_story"],
                "tips": r["tips"]
            })
    return exps


def get_skill_roadmap_details(skill_name: str):
    skill_id = None
    skills_csv = read_csv_layer("career_layer", "skills_master.csv")
    for s in skills_csv:
        if s["skill_name"].lower() == skill_name.lower():
            skill_id = int(s["skill_id"])
            break
            
    if not skill_id:
        return None
        
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT roadmap_id, level, duration_weeks, learning_goals, recommended_resources, milestone 
                FROM skill_roadmaps 
                WHERE skill_id = %s
            """, (skill_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            if rows:
                res = []
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
                return res
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    csv_data = read_csv_layer("learning_layer", "skill_roadmaps.csv")
    res = []
    for r in csv_data:
        if int(r["skill_id"]) == skill_id:
            res.append({
                "source": "CSV Files",
                "roadmap_id": int(r["roadmap_id"]),
                "skill_id": skill_id,
                "skill_name": skill_name,
                "level": r["level"],
                "duration_weeks": int(r["duration_weeks"]),
                "learning_goals": json.loads(r["learning_goals"]),
                "recommended_resources": r["recommended_resources"],
                "milestone": r["milestone"]
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
    Attempts PostgreSQL first, then falls back to CSV files.
    """
    conn = get_db_connection()
    if conn:
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
        except Exception:
            if conn: conn.close()
            
    # Fallback to CSV
    transitions_csv = read_csv_layer("industry_layer", "career_transitions.csv")
    companies_csv = read_csv_layer("industry_layer", "companies.csv")
    
    # Map company_id to company_name
    company_map = {}
    for c in companies_csv:
        company_map[int(c["company_id"])] = c["company_name"]
        
    counts = {}
    for row in transitions_csv:
        src_id = int(row["source_company_id"])
        tgt_id = int(row["target_company_id"])
        src_name = company_map.get(src_id, f"Company {src_id}")
        tgt_name = company_map.get(tgt_id, f"Company {tgt_id}")
        path = f"{src_name} → {tgt_name}"
        counts[path] = counts.get(path, 0) + 1
        
    sorted_paths = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:15]
    return [{"path": k, "count": v} for k, v in sorted_paths]


