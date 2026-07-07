"""
CareerCompass AI — Database Importer
Reads all JSON dataset files and inserts them into PostgreSQL.

Run after executing schema.sql and seed_data.sql.

Requirements:
    pip install psycopg2-binary --break-system-packages

Usage:
    python import_data.py
"""

import json
import os
import csv
import psycopg2
from psycopg2.extras import Json

# ----------------------------------------------------------------
# Database connection config — update before running
# ----------------------------------------------------------------
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database_connector import DB_CONFIG

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")


def load_json(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(filepath: str):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ----------------------------------------------------------------
# Importers
# ----------------------------------------------------------------

def import_qualifications(conn):
    data = load_json(os.path.join(DATASETS_DIR, "qualifications", "all_qualifications.json"))
    cur = conn.cursor()
    for q in data:
        cur.execute("""
            INSERT INTO qualifications
                (qualification_name, level_order, available_time, learning_speed,
                 urgency, typical_duration_months, description)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (qualification_name) DO NOTHING
        """, (
            q["qualification_name"],
            q["level_order"],
            q["available_time"],
            q["learning_speed"],
            q["urgency"],
            q["typical_duration_months"],
            q["description"],
        ))
    conn.commit()
    cur.close()
    print(f"  Qualifications: {len(data)} records inserted.")


def import_resources(conn):
    data = load_json(os.path.join(DATASETS_DIR, "resources", "learning_resources.json"))
    cur = conn.cursor()
    for r in data:
        # skill_id lookup
        skill_id = None
        if r.get("topic"):
            cur.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (r["topic"],))
            row = cur.fetchone()
            if row:
                skill_id = row[0]

        cur.execute("""
            INSERT INTO resources
                (title, resource_type, topic, skill_id, url, platform,
                 difficulty, duration_hours, is_free, rating, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            r["title"],
            r["resource_type"],
            r.get("topic"),
            skill_id,
            r.get("url"),
            r.get("platform"),
            r.get("difficulty"),
            r.get("duration_hours"),
            r.get("is_free", True),
            r.get("rating"),
            r.get("notes"),
        ))
    conn.commit()
    cur.close()
    print(f"  Resources: {len(data)} records inserted.")


def import_projects(conn):
    data = load_json(os.path.join(DATASETS_DIR, "projects", "projects.json"))
    cur = conn.cursor()
    for p in data:
        cur.execute("""
            INSERT INTO projects
                (project_name, description, difficulty, estimated_days, skills_covered, outcome)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            p["project_name"],
            p.get("description"),
            p.get("difficulty"),
            p.get("estimated_days"),
            Json(p.get("skills_covered", [])),
            p.get("outcome"),
        ))
    conn.commit()
    cur.close()
    print(f"  Projects: {len(data)} records inserted.")


def import_interview_questions(conn):
    data = load_json(os.path.join(DATASETS_DIR, "interview_questions", "interview_questions.json"))
    cur = conn.cursor()

    # Get Blinkit SDE company_role_id
    cur.execute("""
        SELECT cr.company_role_id FROM company_roles cr
        JOIN companies c ON cr.company_id = c.company_id
        JOIN roles r ON cr.role_id = r.role_id
        WHERE c.company_name = 'Blinkit' AND r.role_name = 'Software Development Engineer (SDE)'
    """)
    row = cur.fetchone()
    company_role_id = row[0] if row else None

    for q in data:
        cur.execute("""
            INSERT INTO interview_questions
                (company_role_id, category, difficulty, question, answer, explanation, tags, frequency)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            company_role_id,
            q.get("category"),
            q.get("difficulty"),
            q["question"],
            q.get("answer"),
            q.get("explanation"),
            Json(q.get("tags", [])),
            q.get("frequency"),
        ))
    conn.commit()
    cur.close()
    print(f"  Interview Questions: {len(data)} records inserted.")


def import_resume_guidance(conn):
    data = load_json(os.path.join(DATASETS_DIR, "guidance", "resume", "resume_guidance.json"))
    cur = conn.cursor()
    for r in data:
        cur.execute("SELECT qualification_id FROM qualifications WHERE qualification_name = %s",
                    (r["qualification"],))
        row = cur.fetchone()
        if not row:
            print(f"  WARN: Qualification '{r['qualification']}' not found. Skipping.")
            continue
        qualification_id = row[0]

        cur.execute("""
            INSERT INTO resume_guidance
                (qualification_id, required_sections, optional_sections,
                 ats_tips, common_mistakes, word_limit, example_summary)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            qualification_id,
            Json(r.get("required_sections", [])),
            Json(r.get("optional_sections", [])),
            Json(r.get("ats_tips", [])),
            Json(r.get("common_mistakes", [])),
            r.get("word_limit"),
            r.get("example_summary"),
        ))
    conn.commit()
    cur.close()
    print(f"  Resume Guidance: {len(data)} records inserted.")


def import_linkedin_github_guidance(conn):
    data = load_json(os.path.join(DATASETS_DIR, "guidance", "linkedin", "linkedin_github_guidance.json"))
    cur = conn.cursor()

    linkedin_data = data.get("linkedin_guidance", [])
    github_data = data.get("github_guidance", [])

    for r in linkedin_data:
        cur.execute("SELECT qualification_id FROM qualifications WHERE qualification_name = %s",
                    (r["qualification"],))
        row = cur.fetchone()
        if not row:
            continue
        qualification_id = row[0]

        cur.execute("""
            INSERT INTO linkedin_guidance
                (qualification_id, headline_examples, about_examples,
                 skills_to_list, networking_tips, profile_checklist)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            qualification_id,
            Json(r.get("headline_examples", [])),
            Json([r.get("about_example", "")]),
            Json(r.get("skills_to_list", [])),
            Json(r.get("networking_tips", [])),
            Json(r.get("profile_checklist", [])),
        ))

    for r in github_data:
        cur.execute("SELECT qualification_id FROM qualifications WHERE qualification_name = %s",
                    (r["qualification"],))
        row = cur.fetchone()
        if not row:
            continue
        qualification_id = row[0]

        cur.execute("""
            INSERT INTO github_guidance
                (qualification_id, profile_readme_tips, required_repos,
                 repo_naming_standards, commit_standards, readme_template,
                 contribution_strategy, profile_checklist)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            qualification_id,
            r.get("profile_readme_tips"),
            Json(r.get("required_repos", [])),
            r.get("repo_naming_standards"),
            r.get("commit_standards"),
            r.get("readme_template"),
            r.get("contribution_strategy"),
            Json(r.get("profile_checklist", [])),
        ))

    conn.commit()
    cur.close()
    print(f"  LinkedIn Guidance: {len(linkedin_data)} records inserted.")
    print(f"  GitHub Guidance: {len(github_data)} records inserted.")


def import_roadmaps(conn):
    data = load_json(os.path.join(DATASETS_DIR, "roadmaps", "blinkit_sde_roadmaps.json"))
    cur = conn.cursor()

    # Get company_role_id
    cur.execute("""
        SELECT cr.company_role_id FROM company_roles cr
        JOIN companies c ON cr.company_id = c.company_id
        JOIN roles r ON cr.role_id = r.role_id
        WHERE c.company_name = 'Blinkit' AND r.role_name = 'Software Development Engineer (SDE)'
    """)
    row = cur.fetchone()
    if not row:
        print("  ERROR: Blinkit SDE company_role not found. Run seed_data.sql first.")
        return
    company_role_id = row[0]

    for rm in data["roadmaps"]:
        cur.execute("SELECT qualification_id FROM qualifications WHERE qualification_name = %s",
                    (rm["qualification"],))
        row = cur.fetchone()
        if not row:
            print(f"  WARN: Qualification '{rm['qualification']}' not found. Skipping.")
            continue
        qualification_id = row[0]

        cur.execute("""
            INSERT INTO roadmaps (qualification_id, company_role_id, total_duration_months, overview)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (qualification_id, company_role_id) DO NOTHING
            RETURNING roadmap_id
        """, (qualification_id, company_role_id, rm["total_duration_months"], rm["overview"]))
        result = cur.fetchone()
        if not result:
            continue
        roadmap_id = result[0]

        for stage in rm["stages"]:
            cur.execute("""
                INSERT INTO roadmap_stages
                    (roadmap_id, stage_number, stage_title, duration_weeks,
                     focus_area, learning_goals, weekly_hours, milestone)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING stage_id
            """, (
                roadmap_id,
                stage["stage_number"],
                stage["stage_title"],
                stage["duration_weeks"],
                stage["focus_area"],
                Json(stage.get("learning_goals", [])),
                stage.get("weekly_hours"),
                stage.get("milestone"),
            ))
            stage_id = cur.fetchone()[0]

            # Link skills
            for skill_name in stage.get("skills", []):
                cur.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,))
                skill_row = cur.fetchone()
                if skill_row:
                    cur.execute("""
                        INSERT INTO stage_skills (stage_id, skill_id) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (stage_id, skill_row[0]))

    conn.commit()
    cur.close()
    print(f"  Roadmaps: {len(data['roadmaps'])} qualification roadmaps inserted.")


def import_job_descriptions(conn):
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hiring_layer", "job_descriptions.csv"))
    data = load_csv(csv_path)
    cur = conn.cursor()
    for r in data:
        cur.execute("""
            INSERT INTO job_descriptions
                (jd_id, company_id, role_id, experience_required_years, salary_range, description, responsibilities, requirements)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (jd_id) DO NOTHING
        """, (
            int(r["jd_id"]),
            int(r["company_id"]),
            int(r["role_id"]),
            r["experience_required_years"],
            r["salary_range"],
            r["description"],
            r["responsibilities"],
            r["requirements"],
        ))
    conn.commit()
    cur.close()
    print(f"  Job Descriptions: {len(data)} records inserted.")


def import_interview_experiences(conn):
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hiring_layer", "interview_experiences.csv"))
    data = load_csv(csv_path)
    cur = conn.cursor()
    for r in data:
        cur.execute("""
            INSERT INTO interview_experiences
                (experience_id, company_id, role_id, candidate_name, verdict, difficulty_rating, experience_story, tips)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (experience_id) DO NOTHING
        """, (
            int(r["experience_id"]),
            int(r["company_id"]),
            int(r["role_id"]),
            r["candidate_name"],
            r["verdict"],
            int(r["difficulty_rating"]),
            r["experience_story"],
            r["tips"],
        ))
    conn.commit()
    cur.close()
    print(f"  Interview Experiences: {len(data)} records inserted.")


def import_skill_roadmaps(conn):
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "learning_layer", "skill_roadmaps.csv"))
    data = load_csv(csv_path)
    cur = conn.cursor()
    for r in data:
        cur.execute("""
            INSERT INTO skill_roadmaps
                (roadmap_id, skill_id, level, duration_weeks, learning_goals, recommended_resources, milestone)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (roadmap_id) DO NOTHING
        """, (
            int(r["roadmap_id"]),
            int(r["skill_id"]),
            r["level"],
            int(r["duration_weeks"]),
            r["learning_goals"],
            r["recommended_resources"],
            r["milestone"],
        ))
    conn.commit()
    cur.close()
    print(f"  Skill Roadmaps: {len(data)} records inserted.")


# ----------------------------------------------------------------
# Main runner
# ----------------------------------------------------------------

def run_all_imports():
    print("\nCareerCompass AI — Database Importer")
    print("=" * 45)
    print("Connecting to PostgreSQL...")

    try:
        conn = get_connection()
        print("Connected successfully.\n")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Check DB_CONFIG at top of this file.")
        return

    steps = [
        ("Qualifications",           import_qualifications),
        ("Resources",                import_resources),
        ("Projects",                 import_projects),
        ("Interview Questions",      import_interview_questions),
        ("Resume Guidance",          import_resume_guidance),
        ("LinkedIn/GitHub Guidance", import_linkedin_github_guidance),
        ("Roadmaps & Stages",        import_roadmaps),
        ("Job Descriptions",         import_job_descriptions),
        ("Interview Experiences",    import_interview_experiences),
        ("Skill Roadmaps",           import_skill_roadmaps),
    ]

    for name, fn in steps:
        print(f"Importing {name}...")
        try:
            fn(conn)
        except Exception as e:
            print(f"  ERROR in {name}: {e}")
            conn.rollback()

    conn.close()
    print("\nAll imports complete. Database is ready.")


if __name__ == "__main__":
    run_all_imports()
