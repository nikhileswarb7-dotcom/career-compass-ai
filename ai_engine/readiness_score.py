# Readiness Score Engine - CareerCompass AI
# Queries PostgreSQL database skills_frequency dynamically for readiness weights

import os
import sys
import logging
from api.database_connector import get_db_connection

logger = logging.getLogger("ReadinessScore")

def get_db_skill_weights() -> dict:
    """
    Queries skills and their computed importance scores from the PostgreSQL skills_frequency table
    for skills that are actually mapped to SDE / Software Development Engineer roles.
    Calibrates the weights dynamically using role skill priorities.
    """
    weights = {}
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT DISTINCT LOWER(s.skill_name), sf.importance_score, rs.priority
                FROM role_skills rs
                JOIN skills s ON rs.skill_id = s.skill_id
                JOIN skills_frequency sf ON s.skill_id = sf.skill_id
                JOIN company_roles cr ON rs.company_role_id = cr.company_role_id
                JOIN roles r ON cr.role_id = r.role_id
                WHERE LOWER(r.role_name) LIKE %s OR LOWER(r.role_name) LIKE %s OR LOWER(r.role_name) LIKE %s;
            """, ("%software development engineer%", "%sde%", "%junior%"))
            for row in cur.fetchall():
                if row[0]:
                    skill_name = row[0].strip()
                    imp_score = int(row[1] or 5)
                    priority = row[2]
                    
                    # Calibrate importance_score dynamically based on SDE priority constraints
                    if priority == "High":
                        weight = max(imp_score, 10)
                    elif priority == "Medium":
                        weight = max(imp_score, 5)
                    else:
                        weight = max(imp_score, 2)
                        
                    if skill_name in weights:
                        weights[skill_name] = max(weights[skill_name], weight)
                    else:
                        weights[skill_name] = weight
            cur.close()
            conn.close()
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error querying skill weights from DB: {e}")
            
    # Default SDE skill weight mappings fallback only if DB is completely offline
    if not weights:
        weights = {
            "java": 10,
            "dsa (combined)": 10,
            "dbms": 10,
            "operating systems": 10,
            "computer networks": 10,
            "spring boot": 10,
            "system design": 10,
            "sql": 5,
            "mysql": 5,
            "git & github": 5,
            "low level design": 5,
            "high level design": 5,
            "object oriented programming": 5,
            "rest apis": 5,
            "docker": 2,
            "redis": 2,
            "microservices": 2
        }
    return weights

def calculate_readiness(matched_skills: list[str]) -> int:
    """
    Calculates the readiness score out of 100 based on matched skills and PostgreSQL weights.
    """
    weights = get_db_skill_weights()
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0
        
    matched_set = {s.lower().strip() for s in matched_skills}
    score_weight = sum(w for s, w in weights.items() if s in matched_set)
    
    return int((score_weight / total_weight) * 100)
