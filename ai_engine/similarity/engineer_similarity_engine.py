# Engineer Similarity Engine - CareerCompass AI

import os
import sys
import csv
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import get_db_connection
from ai_engine.similarity.profile_vectorizer import vectorize_profile, compute_cosine_similarity

def load_employee_profiles() -> List[Dict[str, Any]]:
    """
    Loads all parsed SDE employee profiles and their associated skills.
    Queries PostgreSQL first, then falls back to CSV files.
    """
    profiles = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT p.profile_id, p.name, p.current_company, r.role_name, p.experience_years, p.college, p.degree, p.previous_company, p.career_path,
                       COALESCE(ARRAY_TO_STRING(ARRAY_AGG(s.skill_name), ','), '') as skills
                FROM employee_profiles p
                LEFT JOIN roles r ON p.role_id = r.role_id
                LEFT JOIN employee_skills es ON p.profile_id = es.profile_id
                LEFT JOIN skills s ON es.skill_id = s.skill_id
                GROUP BY p.profile_id, p.name, p.current_company, r.role_name, p.experience_years, p.college, p.degree, p.previous_company, p.career_path
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            for row in rows:
                p_skills = [s.strip() for s in row[9].split(',') if s.strip()] if row[9] else []
                path_str = row[8] or ""
                career_path_list = [step.strip() for step in path_str.split("->") if step.strip()]
                if not career_path_list:
                    career_path_list = ["Intern", "SDE-1", "SDE-2"]
                    
                profiles.append({
                    "profile_id": int(row[0]),
                    "name": row[1],
                    "current_company": row[2] or "Blinkit",
                    "company_name": row[2] or "Blinkit", # Safe duplicate for front-end rendering
                    "role_name": row[3] or "Software Development Engineer",
                    "experience_years": float(row[4] or 0.0),
                    "college": row[5] or "",
                    "degree": row[6] or "",
                    "previous_company": row[7] or "",
                    "career_path": career_path_list,
                    "career_path_str": path_str,
                    "skills": p_skills
                })
            if profiles:
                return profiles
        except Exception as e:
            if conn: conn.close()
            print("PostgreSQL error in load_employee_profiles, falling back to CSV:", e)

    # Fallback to CSV files
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_dir = os.path.join(base_dir, "database")
        
        profiles_csv = os.path.join(db_dir, "industry_layer", "employee_profiles.csv")
        skills_csv = os.path.join(db_dir, "industry_layer", "employee_skills.csv")
        skills_master_csv = os.path.join(db_dir, "career_layer", "skills_master.csv")
        roles_csv = os.path.join(db_dir, "industry_layer", "roles.csv")

        # 1. Map skill ID to skill name
        skill_id_to_name = {}
        if os.path.exists(skills_master_csv):
            with open(skills_master_csv, mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    skill_id_to_name[int(row["skill_id"])] = row["skill_name"]

        # 2. Map role ID to role name
        role_id_to_name = {}
        if os.path.exists(roles_csv):
            with open(roles_csv, mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    role_id_to_name[int(row["role_id"])] = row["role_name"]

        # 3. Map profile ID to their list of skill names
        profile_skills = {}
        if os.path.exists(skills_csv):
            with open(skills_csv, mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    p_id = int(row["profile_id"])
                    s_id = int(row["skill_id"])
                    s_name = skill_id_to_name.get(s_id)
                    if s_name:
                        if p_id not in profile_skills:
                            profile_skills[p_id] = []
                        profile_skills[p_id].append(s_name)

        # 4. Load profiles
        if os.path.exists(profiles_csv):
            with open(profiles_csv, mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    p_id = int(row["profile_id"])
                    r_id = int(row["role_id"]) if row.get("role_id") else None
                    role_name = role_id_to_name.get(r_id, "Software Development Engineer")
                    
                    path_str = row.get("career_path", "")
                    career_path_list = [step.strip() for step in path_str.split("->") if step.strip()]
                    if not career_path_list:
                        career_path_list = ["Intern", "SDE-1", "SDE-2"]
                        
                    profiles.append({
                        "profile_id": p_id,
                        "name": row.get("name", "SDE Peer"),
                        "current_company": row.get("current_company", "Blinkit"),
                        "company_name": row.get("current_company", "Blinkit"),
                        "role_name": role_name,
                        "experience_years": float(row.get("experience_years", 0.0) or 0.0),
                        "college": row.get("college", ""),
                        "degree": row.get("degree", ""),
                        "previous_company": row.get("previous_company", ""),
                        "career_path": career_path_list,
                        "career_path_str": path_str,
                        "skills": profile_skills.get(p_id, [])
                    })
    except Exception as err:
        print("CSV fallback error in load_employee_profiles:", err)

    return profiles

class EngineerSimilarityEngine:
    """
    Compares student profiles against parsed database engineers to calculate top matches.
    """

    @staticmethod
    def find_similar_engineers(
        student_skills: list, 
        target_company: str, 
        target_role: str, 
        experience_years: float = 0.0,
        gpa: float = 0.0,
        qualification: str = "",
        limit: int = 5
    ) -> list:
        """
        Calculates cosine similarities against all employees and returns the top matched peers.
        Applies similarity boosts based on company and role match.
        """
        employees = load_employee_profiles()
        if not employees:
            return []

        # Vectorize the target student profile
        student_vec = vectorize_profile(
            skills=student_skills, 
            company=target_company, 
            role=target_role, 
            experience_years=experience_years, 
            gpa=gpa, 
            qualification=qualification
        )

        scored_profiles = []
        for emp in employees:
            # Vectorize employee profile
            emp_vec = vectorize_profile(
                skills=emp["skills"], 
                company=emp["current_company"], 
                role=emp["role_name"],
                experience_years=emp["experience_years"],
                gpa=8.0, # default average industry GPA
                qualification="" # classify by experience
            )
            similarity = compute_cosine_similarity(student_vec, emp_vec)
            
            # Apply boosting
            # 1. Company Match Boost (+20%)
            if emp["current_company"].lower().strip() == target_company.lower().strip():
                similarity *= 1.20
            # 2. Role Match Boost (+15%)
            if emp["role_name"].lower().strip() == target_role.lower().strip():
                similarity *= 1.15
                
            similarity = min(similarity, 1.0)
            
            scored_profiles.append({
                "profile_id": emp["profile_id"],
                "name": emp["name"],
                "current_company": emp["current_company"],
                "company_name": emp["current_company"], # safe duplication
                "role_name": emp["role_name"],
                "similarity_score": round(similarity, 4),
                "skills": emp["skills"],
                "career_path": emp["career_path"],
                "career_path_str": emp["career_path_str"]
            })

        # Sort by similarity score descending
        scored_profiles.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_profiles[:limit]
