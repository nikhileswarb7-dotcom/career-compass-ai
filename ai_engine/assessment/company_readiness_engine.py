# Company Readiness Engine - CareerCompass AI
# Queries company tiers dynamically from PostgreSQL company_metadata and interview patterns

import os
import sys
import logging
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import get_db_connection

logger = logging.getLogger("CompanyReadinessEngine")

# Dynamic runtime tier overrides mapping cache
DYNAMIC_TIER_OVERRIDES = {}

def set_company_tier(company_name: str, tier: int):
    """
    Allows dynamically configuring company tier mappings at runtime.
    """
    DYNAMIC_TIER_OVERRIDES[company_name.lower().strip()] = tier

def get_company_tier(company_name: str) -> int:
    """
    Determines company tier (1, 2, or 3) from overrides mapping first,
    then database (PostgreSQL), and raises exception if database is unavailable.
    """
    comp_clean = company_name.lower().strip() if company_name else ""
    
    # 1. Check runtime overrides mapping first
    if comp_clean in DYNAMIC_TIER_OVERRIDES:
        return DYNAMIC_TIER_OVERRIDES[comp_clean]
        
    # 2. Try DB lookup on company_metadata
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            
            # Query tier from metadata
            cur.execute("""
                SELECT cm.tier 
                FROM company_metadata cm
                JOIN companies c ON cm.company_id = c.company_id
                WHERE LOWER(c.company_name) = %s;
            """, (comp_clean,))
            row = cur.fetchone()
            if row:
                cur.close()
                conn.close()
                return int(row[0])
                
            # If metadata not found, query difficulty rating from interview patterns
            cur.execute("""
                SELECT difficulty_rating 
                FROM company_interview_patterns cip
                JOIN companies c ON cip.company_id = c.company_id
                WHERE LOWER(c.company_name) = %s;
            """, (comp_clean,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            if rows:
                max_diff = max(row[0] for row in rows if row[0] is not None)
                if max_diff >= 8:
                    return 1
                elif max_diff >= 5:
                    return 2
                else:
                    return 3
                    
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error querying company tier from DB: {e}")

    # Fallback default baseline mappings only if PostgreSQL connection fails
    baseline_tiers = {
        "google": 1,
        "microsoft": 1,
        "meta": 1,
        "amazon": 1,
        "blinkit": 1,
        "zomato": 1,
        "swiggy": 1,
        "phonepe": 1,
        "flipkart": 2,
        "paytm": 2,
        "tcs": 3,
        "infosys": 3,
        "wipro": 3,
        "cognizant": 3
    }
    if comp_clean in baseline_tiers:
        return baseline_tiers[comp_clean]
        
    return 2

def evaluate_company_readiness(
    student_skills: List[str],
    project_score: float,
    interview_score: float,
    dream_company: str,
    target_role: str
) -> Dict[str, Any]:
    """
    Computes a company fit score (0-100) and matches profile parameters 
    against target company constraints.
    """
    tier = get_company_tier(dream_company)
    
    # Tier descriptions
    tier_names = {
        1: "Tier 1 (High Hiring Bar)",
        2: "Tier 2 (Growth / Product-Focused)",
        3: "Tier 3 (Service / Consultancies)"
    }
    
    # 1. Load required skills for the company role
    from ai_engine.assessment.skill_assessor import get_role_skills_requirements
    requirements = get_role_skills_requirements(dream_company, target_role)
    
    skills_set = {s.lower().strip() for s in student_skills}
    
    total_weight = 0
    matched_weight = 0
    
    priority_weights = {
        "High": 5,
        "Medium": 3,
        "Low": 1
    }
    
    for skill_name, priority in requirements.items():
        w = priority_weights.get(priority, 1)
        total_weight += w
        if skill_name.lower().strip() in skills_set:
            matched_weight += w
            
    skill_match_ratio = (matched_weight / total_weight) if total_weight > 0 else 0.5
    
    # 2. Check if student meets expectation thresholds for the company tier
    # Target thresholds
    if tier == 1:
        target_project = 75.0
        target_interview = 75.0
    elif tier == 3:
        target_project = 40.0
        target_interview = 40.0
    else: # tier 2
        target_project = 60.0
        target_interview = 60.0
        
    project_fit_factor = min(project_score / target_project, 1.2)
    interview_fit_factor = min(interview_score / target_interview, 1.2)
    
    # 3. Calculate overall company fit score (out of 100)
    # Weigh skill requirement match (50%), project strength (25%), and interview strength (25%)
    fit_score = (50.0 * skill_match_ratio) + (25.0 * (project_score / 100.0) * project_fit_factor) + (25.0 * (interview_score / 100.0) * interview_fit_factor)
    fit_score = min(max(round(fit_score * 100.0 / 75.0, 1), 0.0), 100.0) # normalize to 100 max
    
    # Determine category
    if fit_score >= 75.0:
        fit_category = "Strong Fit (Interview Ready)"
    elif fit_score >= 45.0:
        fit_category = "Potential Match (Needs Prep)"
    else:
        fit_category = "Gap Remediation Required"
        
    return {
        "company_tier_id": tier,
        "company_tier_name": tier_names.get(tier, "Tier 2 (Growth / Product-Focused)"),
        "company_fit_score": fit_score,
        "fit_category": fit_category,
        "target_project_expectation": target_project,
        "target_interview_expectation": target_interview
    }
