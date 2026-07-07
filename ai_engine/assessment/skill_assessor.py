# Technical Skill Strength Assessor - CareerCompass AI

import os
import sys
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import get_db_connection

logger = logging.getLogger("SkillAssessor")

def get_role_skills_requirements(company_name: str, role_name: str) -> dict:
    """
    Fetches required skills and their priorities for a target company and role from PostgreSQL.
    """
    requirements = {}
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.skill_name, rs.priority 
                FROM role_skills rs
                JOIN skills s ON rs.skill_id = s.skill_id
                JOIN company_roles cr ON rs.company_role_id = cr.company_role_id
                JOIN companies c ON cr.company_id = c.company_id
                JOIN roles r ON cr.role_id = r.role_id
                WHERE LOWER(c.company_name) = %s AND LOWER(r.role_name) = %s
            """, (company_name.lower().strip(), role_name.lower().strip()))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            if rows:
                for row in rows:
                    requirements[row[0]] = row[1]
                return requirements
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error querying role requirements from DB: {e}")

    # Throw error if DB is unavailable
    raise RuntimeError(f"PostgreSQL database unavailable to fetch SDE requirements for company '{company_name}' and role '{role_name}'!")

def assess_skills(student_skills, company_name: str, role_name: str) -> float:
    """
    Computes a score (0 to 100) representing Technical Skill Strength.
    Supports student_skills as a list or dictionary (mapping skill name to proficiency score 0.0-1.0).
    """
    requirements = get_role_skills_requirements(company_name, role_name)
    if not requirements:
        return 0.0
        
    if isinstance(student_skills, dict):
        student_skills_map = {s.lower().strip(): val for s, val in student_skills.items()}
    else:
        student_skills_map = {s.lower().strip(): 1.0 for s in student_skills}
    
    total_weight = 0
    matched_weight = 0
    
    priority_weights = {
        "High": 5,
        "Medium": 3,
        "Low": 1
    }
    
    for skill_name, priority in requirements.items():
        weight = priority_weights.get(priority, 1)
        total_weight += weight
        norm_key = skill_name.lower().strip()
        if norm_key in student_skills_map:
            proficiency = student_skills_map[norm_key]
            matched_weight += weight * proficiency
            
    if total_weight == 0:
        return 0.0
        
    # Extra minor bonus (0.5 points per non-required skill, capped at 8 points bonus)
    non_req_matches = 0
    if isinstance(student_skills, dict):
        for s, val in student_skills.items():
            if s.lower().strip() not in {k.lower().strip() for k in requirements.keys()}:
                non_req_matches += val
    else:
        for s in student_skills:
            if s.lower().strip() not in {k.lower().strip() for k in requirements.keys()}:
                non_req_matches += 1
                
    bonus = min(non_req_matches * 0.5, 8.0)
    
    score = (matched_weight / total_weight) * 100 + bonus
    return min(max(round(score, 1), 0.0), 100.0)
