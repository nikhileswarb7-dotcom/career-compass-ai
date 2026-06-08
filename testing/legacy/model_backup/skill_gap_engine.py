# Skill Gap Engine - CareerCompass AI

ROLE_REQUIREMENTS = {
    "Java": "High",
    "DSA (Combined)": "High",
    "DBMS": "High",
    "Operating Systems": "High",
    "Computer Networks": "High",
    "Spring Boot": "High",
    "System Design": "High",
    "SQL": "Medium",
    "MySQL": "Medium",
    "Git & GitHub": "Medium",
    "Low Level Design": "Medium",
    "High Level Design": "Medium",
    "Object Oriented Programming": "Medium",
    "REST APIs": "Medium",
    "Docker": "Low",
    "Redis": "Low",
    "Microservices": "Low"
}

def analyze_gaps(known_skills: list[str], dream_company: str = None, target_role: str = None) -> dict:
    """
    Compares the user's known skills against SDE requirements.
    Returns categorized lists of missing skills.
    """
    # Get role requirements dynamically if company and role are provided
    if dream_company and target_role:
        try:
            from ai_engine.assessment.skill_assessor import get_role_skills_requirements
            role_reqs = get_role_skills_requirements(dream_company, target_role)
        except Exception:
            role_reqs = ROLE_REQUIREMENTS
    else:
        role_reqs = ROLE_REQUIREMENTS

    if not role_reqs:
        role_reqs = ROLE_REQUIREMENTS

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
