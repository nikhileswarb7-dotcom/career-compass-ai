# Career Path Analyzer - CareerCompass AI

import os
import csv
import sys
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import get_db_connection

def analyze_career_paths(similar_engineers: List[Dict[str, Any]], student_skills: List[str]) -> Dict[str, Any]:
    """
    Analyzes the career histories of top similar SDE peers to extract:
    1. Frequencies of missing skills (to serve as evidence/weights for recommendations).
    2. Common transition paths.
    3. Mapped SDE projects from DB relevant to missing skills.
    """
    if not similar_engineers:
        return {
            "missing_skills_frequency": {},
            "common_transitions": [],
            "common_projects": []
        }

    student_skills_lower = {s.lower().strip() for s in student_skills}
    
    # 1. Calculate missing skill frequencies among similar engineers
    missing_skill_counts = {}
    for eng in similar_engineers:
        for skill in eng["skills"]:
            skill_clean = skill.strip()
            if skill_clean.lower() not in student_skills_lower:
                missing_skill_counts[skill_clean] = missing_skill_counts.get(skill_clean, 0) + 1
                
    # Convert counts to frequencies (ratio out of total similar engineers, e.g. 0.8 for 4/5)
    total_peers = len(similar_engineers)
    missing_skills_frequency = {
        skill: round(count / total_peers, 2) 
        for skill, count in missing_skill_counts.items()
    }

    # 2. Extract common transitions
    transitions = []
    for eng in similar_engineers:
        # Check list format first, then fallback to string
        path = eng.get("career_path")
        if isinstance(path, list):
            clean_path = " -> ".join(path)
        else:
            path_str = eng.get("career_path_str") or eng.get("career_path") or ""
            clean_path = " -> ".join([step.strip() for step in path_str.split("->") if step.strip()])
            
        if clean_path and clean_path not in transitions:
            transitions.append(clean_path)
                
    if not transitions:
        transitions = ["Intern -> SDE-1 -> SDE-2"]

    # 3. Dynamic Projects lookup from DB matching missing skills
    # Prioritizes projects covering skills that the student is missing but similar peers possess.
    common_projects = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT pm.project_name, pm.description, 
                       COALESCE(ARRAY_TO_STRING(ARRAY_AGG(s.skill_name), ','), '') as skills
                FROM projects_master pm
                LEFT JOIN project_skill_mapping psm ON pm.project_id = psm.project_id
                LEFT JOIN skills_master s ON psm.skill_id = s.skill_id
                GROUP BY pm.project_id, pm.project_name, pm.description
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            project_candidates = []
            for row in rows:
                p_name, desc, skills_str = row
                p_skills = [sk.strip() for sk in skills_str.split(',') if sk.strip()]
                
                # Count matching missing skills that have a high frequency among peers
                overlap_score = 0.0
                for sk in p_skills:
                    if sk.lower().strip() in {ms.lower().strip() for ms in missing_skills_frequency.keys()}:
                        # Add similar peer frequency weight
                        overlap_score += missing_skills_frequency.get(sk, 0.5)
                        
                if overlap_score > 0:
                    project_candidates.append((p_name, overlap_score))
                    
            # Sort by overlap score descending
            project_candidates.sort(key=lambda x: x[1], reverse=True)
            common_projects = [item[0] for item in project_candidates[:3]]
        except Exception:
            if conn: conn.close()
            
    # Fallback if DB is empty or fails
    if not common_projects:
        projects_pool = {
            "blinkit": [
                "High-Concurrency Order Dispatching System using Go and Kafka",
                "Real-Time Geo-Indexing Rider Service with Redis and PostgreSQL",
                "Scalable Flash Sale Booking Engine with distributed locks"
            ],
            "amazon": [
                "Locker Booking Service LLD using Java and Spring Boot",
                "High-Throughput Pub/Sub Message Queue for Order Fulfillment",
                "Distributed Rate Limiter for secure API Gateway endpoints"
            ],
            "google": [
                "Parallel Web Crawler System Design with MapReduce and Go",
                "Cinematic Video Compression Transcoder Engine using C++",
                "High-Throughput Spatial Search API with distributed caches"
            ]
        }
        company_key = similar_engineers[0].get("current_company", "blinkit").lower().strip()
        common_projects = projects_pool.get(company_key, projects_pool["blinkit"])

    return {
        "missing_skills_frequency": missing_skills_frequency,
        "common_transitions": transitions[:3],
        "common_projects": common_projects
    }
