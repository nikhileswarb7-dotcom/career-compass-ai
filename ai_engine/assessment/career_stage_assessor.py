# Career Stage Intelligence Assessor - CareerCompass AI

CAREER_STAGES = {
    "Foundational / Early Explorer": {
        "expected_skills": 4,
        "expected_profile_strength": 40.0,
        "expected_project_strength": 40.0,
        "recommended_hours_weekly": 10,
        "advice": "Focus on SDE programming fundamentals, OOPs design, and basic DSA concepts (Arrays, Lists)."
    },
    "Core Developer / Intermediate": {
        "expected_skills": 8,
        "expected_profile_strength": 55.0,
        "expected_project_strength": 55.0,
        "recommended_hours_weekly": 15,
        "advice": "Build intermediate projects (REST APIs, Databases) and master core DSA (Trees, Graphs, SQL)."
    },
    "Advanced / Pre-Placement": {
        "expected_skills": 12,
        "expected_profile_strength": 70.0,
        "expected_project_strength": 70.0,
        "recommended_hours_weekly": 25,
        "advice": "Focus on system design (LLD/HLD), advanced algorithms, and polish your GitHub and resume."
    },
    "Placement Ready / Bootloader": {
        "expected_skills": 16,
        "expected_profile_strength": 80.0,
        "expected_project_strength": 80.0,
        "recommended_hours_weekly": 35,
        "advice": "Rigorous mock interviews, high-concurrency projects, and daily coding sandbox exercises."
    },
    "Transitioning Professional": {
        "expected_skills": 18,
        "expected_profile_strength": 85.0,
        "expected_project_strength": 85.0,
        "recommended_hours_weekly": 12,
        "advice": "Target SDE-2 patterns, production scale tuning, microservices, cloud infrastructure, and SRE/DevOps tools."
    }
}

def classify_career_stage(qualification: str, experience_years: float = 0.0) -> str:
    """
    Classifies a student's qualification year or an engineer's experience 
    into a normalized career stage.
    """
    if experience_years > 0.0:
        return "Transitioning Professional"
        
    q_lower = qualification.lower().strip() if qualification else ""
    
    if "1st" in q_lower:
        return "Foundational / Early Explorer"
    elif "2nd" in q_lower:
        return "Core Developer / Intermediate"
    elif "3rd" in q_lower:
        return "Advanced / Pre-Placement"
    elif "4th" in q_lower or "fresh" in q_lower or "graduate" in q_lower:
        return "Placement Ready / Bootloader"
    elif "trainee" in q_lower or "junior" in q_lower or "sde" in q_lower:
        return "Transitioning Professional"
    else:
        # Default fallback
        return "Core Developer / Intermediate"

def evaluate_career_stage(
    qualification: str, 
    actual_skills_count: int, 
    actual_profile_score: float, 
    actual_project_score: float,
    experience_years: float = 0.0
) -> dict:
    """
    Evaluates a candidate's actual progress compared to their career stage expectations.
    """
    stage_name = classify_career_stage(qualification, experience_years)
    expectations = CAREER_STAGES.get(stage_name)
    
    expected_skills = expectations["expected_skills"]
    skill_ratio = actual_skills_count / max(expected_skills, 1)
    
    if skill_ratio >= 1.1 and actual_project_score >= expectations["expected_project_strength"]:
        status = "Ahead of Schedule"
    elif skill_ratio < 0.75:
        status = "Needs Acceleration"
    else:
        status = "On Track"
        
    return {
        "career_stage": stage_name,
        "expected_skills_count": expected_skills,
        "expected_profile_strength": expectations["expected_profile_strength"],
        "expected_project_strength": expectations["expected_project_strength"],
        "recommended_hours_weekly": expectations["recommended_hours_weekly"],
        "track_status": status,
        "coaching_advice": expectations["advice"]
    }
