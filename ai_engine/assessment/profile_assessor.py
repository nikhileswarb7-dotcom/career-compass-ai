# Profile Maturity Assessor - CareerCompass AI

import os
import sys

# Add directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from github_assessor import assess_github_profile

def assess_profile(linkedin_url: str, github_username: str, resume_text: str) -> dict:
    """
    Computes a score (0 to 100) representing Profile Maturity, 
    and returns a breakdown of LinkedIn, GitHub, and Resume scores.
    """
    linkedin_score = 0.0
    github_score = 0.0
    resume_score = 0.0

    # 1. LinkedIn URL Assessment
    if linkedin_url and linkedin_url.strip():
        li_lower = linkedin_url.lower().strip()
        if "linkedin.com" in li_lower and ("in/" in li_lower or "profile" in li_lower):
            linkedin_score = 100.0  # Fully complete link
        elif "linkedin.com" in li_lower:
            linkedin_score = 75.0   # General homepage link
        else:
            linkedin_score = 40.0   # Simple text entered
            
    # 2. GitHub Username Assessment (using github_assessor module)
    github_data = assess_github_profile(github_username)
    github_score = github_data["github_score"]
            
    # 3. Resume Text Assessment
    if resume_text and resume_text.strip():
        words_count = len(resume_text.split())
        if words_count > 150:
            resume_score = 100.0  # Fully written resume text
        elif words_count > 50:
            resume_score = 70.0   # Short summary
        else:
            resume_score = 40.0   # Simple keyword lists
            
    # Weigh overall score:
    # 30% LinkedIn, 35% GitHub, 35% Resume
    overall_score = (0.30 * linkedin_score) + (0.35 * github_score) + (0.35 * resume_score)
    
    return {
        "profile_strength": round(overall_score, 1),
        "linkedin_score": round(linkedin_score, 1),
        "github_score": round(github_score, 1),
        "resume_score": round(resume_score, 1),
        "github_details": github_data
    }
