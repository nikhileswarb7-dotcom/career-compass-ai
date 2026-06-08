# Career Readiness Engine - CareerCompass AI

import os
import sys

# Add project directories to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from skill_assessor import assess_skills
from project_assessor import assess_projects
from profile_assessor import assess_profile
from career_stage_assessor import evaluate_career_stage
from company_readiness_engine import evaluate_company_readiness, get_company_tier

# Configurable readiness weights
DEFAULT_READINESS_WEIGHTS = {
    "skill_strength": 0.40,
    "project_strength": 0.25,
    "interview_strength": 0.20,
    "profile_strength": 0.15
}

READINESS_WEIGHTS = dict(DEFAULT_READINESS_WEIGHTS)

def configure_readiness_weights(weights: dict):
    """
    Dynamically configures overall readiness calculation weights.
    """
    global READINESS_WEIGHTS
    for k, v in weights.items():
        if k in READINESS_WEIGHTS:
            READINESS_WEIGHTS[k] = float(v)

def evaluate_career_readiness(
    student_skills: list,
    linkedin_url: str,
    github_username: str,
    resume_text: str,
    company_name: str,
    role_name: str,
    qualification: str = "3rd Year Student",
    experience_years: float = 0.0
) -> dict:
    """
    Orchestrates the individual assessor engines to calculate the core readiness scores,
    career stage expectation status, and company fit diagnostics.
    """
    # 1. Compute individual metrics
    skill_strength = assess_skills(student_skills, company_name, role_name)
    project_strength = assess_projects(resume_text, student_skills)
    profile_data = assess_profile(linkedin_url, github_username, resume_text)
    profile_strength = profile_data["profile_strength"]

    # 2. Compute Interview Strength
    student_skills_lower = {s.lower().strip() for s in student_skills}
    
    interview_competencies = {
        "dsa": ["dsa", "data structures", "algorithms", "dsa (combined)", "java", "go", "python", "kotlin", "typescript"],
        "design": ["system design", "high level design", "low level design", "lld", "hld", "microservices", "distributed systems", "oops", "object oriented programming", "docker", "kubernetes", "containers", "orchestration"],
        "fundamentals": ["dbms", "sql", "postgresql", "mysql", "operating systems", "os", "computer networks", "cn", "networks", "redis"]
    }
    
    dsa_matched = any(c in student_skills_lower for c in interview_competencies["dsa"])
    design_matched = any(c in student_skills_lower for c in interview_competencies["design"])
    fundamentals_matched = any(c in student_skills_lower for c in interview_competencies["fundamentals"])
    
    matched_cats = 0
    if dsa_matched: matched_cats += 1
    if design_matched: matched_cats += 1
    if fundamentals_matched: matched_cats += 1
    
    interview_score = 30.0 + (matched_cats * 20.0) + (skill_strength * 0.1)
    
    # Scale based on target company difficulty tier
    company_tier = get_company_tier(company_name)
    if company_tier == 1:
        # High hiring bar
        interview_score *= 0.88
    elif company_tier == 3:
        # Standard hiring bar
        interview_score *= 1.12
        
    interview_strength = min(max(round(interview_score, 1), 0.0), 100.0)

    # 3. Calculate Overall Career Readiness Score using configurable weights + dynamic boosters
    base_readiness = (
        (READINESS_WEIGHTS["skill_strength"] * skill_strength) + 
        (READINESS_WEIGHTS["project_strength"] * project_strength) + 
        (READINESS_WEIGHTS["interview_strength"] * interview_strength) + 
        (READINESS_WEIGHTS["profile_strength"] * profile_strength)
    )
    
    # Dynamic Boosters:
    # A. Career Maturity Boost
    q_lower = qualification.lower().strip() if qualification else ""
    maturity_boost = 0.0
    if experience_years > 0.0 or "junior" in q_lower or "trainee" in q_lower or "professional" in q_lower:
        maturity_boost = 18.0
    elif "4th" in q_lower or "fresh" in q_lower or "graduate" in q_lower:
        maturity_boost = 12.0
    elif "3rd" in q_lower:
        maturity_boost = 6.0
    elif "2nd" in q_lower:
        maturity_boost = 2.0
        
    # B. Demonstrated Skills quantity boost
    skills_boost = min(len(student_skills) * 2.0, 16.0)
    
    # C. Project Complexity Boost
    project_boost = 0.0
    if resume_text:
        res_lower = resume_text.lower()
        complex_terms = ["kubernetes", "docker", "microservices", "distributed", "concurrency", "kafka", "redis", "scale", "scaling"]
        matched_complex = sum(1 for term in complex_terms if term in res_lower)
        project_boost = min(matched_complex * 3.0, 12.0)
        
    overall_readiness = base_readiness + maturity_boost + skills_boost + project_boost
    
    # Ensure overall readiness is a valid percentage (0-100)
    overall_readiness_score = min(max(round(overall_readiness, 1), 0.0), 100.0)

    # 4. Integrate Career Stage expectations
    stage_evaluation = evaluate_career_stage(
        qualification=qualification,
        actual_skills_count=len(student_skills),
        actual_profile_score=profile_strength,
        actual_project_score=project_strength,
        experience_years=experience_years
    )

    # 5. Integrate Company Fit score
    company_fit_evaluation = evaluate_company_readiness(
        student_skills=student_skills,
        project_score=project_strength,
        interview_score=interview_strength,
        dream_company=company_name,
        target_role=role_name
    )

    return {
        "skill_strength": skill_strength,
        "project_strength": project_strength,
        "interview_strength": interview_strength,
        "profile_strength": profile_strength,
        "overall_readiness": overall_readiness_score,
        
        # Breakdown values for caching table
        "linkedin_score": profile_data["linkedin_score"],
        "github_score": profile_data["github_score"],
        "resume_score": profile_data["resume_score"],
        
        # New upgrades integration
        "career_stage": stage_evaluation,
        "company_readiness": company_fit_evaluation
    }
