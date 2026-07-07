# Skill Gap Engine - CareerCompass AI
# Queries PostgreSQL for company role requirements and raises exceptions if unavailable

import os
import sys
import logging

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai_engine.assessment.skill_assessor import get_role_skills_requirements

logger = logging.getLogger("SkillGapEngine")

def analyze_gaps(known_skills: list[str], dream_company: str = None, target_role: str = None) -> dict:
    """
    Compares the user's known skills against SDE requirements loaded from PostgreSQL.
    Returns categorized lists of missing skills.
    """
    company = dream_company or "Blinkit"
    role = target_role or "Software Development Engineer (SDE)"

    # Get role requirements dynamically from the database
    role_reqs = get_role_skills_requirements(company, role)
    
    if not role_reqs:
        # Try a baseline SDE role query from the database before raising
        role_reqs = get_role_skills_requirements("Blinkit", "Software Development Engineer (SDE)")
        
    if not role_reqs:
        logger.error(f"No requirements found in PostgreSQL for company '{company}' and role '{role}'!")
        raise RuntimeError(f"Database requirements unavailable for company '{company}' and role '{role}'.")

    # Normalize input
    known_set = {s.strip().lower() for s in known_skills}
    
    missing_skills = {
        "High": [],
        "Medium": [],
        "Low": []
    }
    matched_skills = []
    
    for skill, priority in role_reqs.items():
        if skill.lower() in known_set:
            matched_skills.append(skill)
        else:
            if priority not in ["High", "Medium", "Low"]:
                priority = "Medium"
            missing_skills[priority].append(skill)
            
    return {
        "matched": matched_skills,
        "missing": missing_skills
    }
