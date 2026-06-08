# Verification Test for recommendation intelligence upgrades
# CareerCompass AI

import sys
import os

# Add model and ai_engine to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.assessment.career_stage_assessor import classify_career_stage, evaluate_career_stage
from ai_engine.assessment.company_readiness_engine import evaluate_company_readiness, get_company_tier, set_company_tier
from ai_engine.assessment.readiness_engine import configure_readiness_weights, evaluate_career_readiness
from ai_engine.recommendation_engine import generate_recommendation

def verify_intelligence_upgrades():
    print("\nCareerCompass AI - Intelligence Upgrades Verification Suite")
    print("=" * 60)

    # 1. Verify Career Stage Assessor
    print("Testing CareerStageAssessor...")
    stage_1st = classify_career_stage("1st Year Student")
    stage_junior = classify_career_stage("Junior Software Engineer")
    print(f"  Classified '1st Year Student' as: '{stage_1st}'")
    print(f"  Classified 'Junior Software Engineer' as: '{stage_junior}'")
    
    assert stage_1st == "Foundational / Early Explorer"
    assert stage_junior == "Transitioning Professional"
    
    eval_student = evaluate_career_stage(
        qualification="3rd Year Student",
        actual_skills_count=3,
        actual_profile_score=40.0,
        actual_project_score=40.0
    )
    print(f"  3rd Year with 3 skills track status: {eval_student['track_status']}")
    assert eval_student["track_status"] == "Needs Acceleration"
    
    eval_ahead = evaluate_career_stage(
        qualification="2nd Year Student",
        actual_skills_count=12,
        actual_profile_score=80.0,
        actual_project_score=80.0
    )
    print(f"  2nd Year with 12 skills track status: {eval_ahead['track_status']}")
    assert eval_ahead["track_status"] == "Ahead of Schedule"
    print("  [PASS] CareerStageAssessor checks passed!")

    # 2. Verify Company Readiness Engine
    print("Testing CompanyReadinessEngine...")
    tier_google = get_company_tier("Google")
    tier_tcs = get_company_tier("TCS")
    print(f"  Company tier for 'Google' (from DB or config): Tier {tier_google}")
    print(f"  Company tier for 'TCS' (from DB or config): Tier {tier_tcs}")
    
    assert tier_google == 1
    assert tier_tcs == 3
    
    # Test configurability
    set_company_tier("CustomFirm", 1)
    tier_custom = get_company_tier("CustomFirm")
    print(f"  Dynamic company tier configured: 'CustomFirm' -> Tier {tier_custom}")
    assert tier_custom == 1
    
    # Calculate company fit
    fit_data = evaluate_company_readiness(
        student_skills=["Java", "SQL"],
        project_score=50.0,
        interview_score=40.0,
        dream_company="Google",
        target_role="Software Development Engineer"
    )
    print(f"  Google fit score: {fit_data['company_fit_score']}% (Category: {fit_data['fit_category']})")
    assert "company_fit_score" in fit_data
    assert "fit_category" in fit_data
    print("  [PASS] CompanyReadinessEngine checks passed!")

    # 3. Verify Configurable Readiness Weights
    print("Testing Readiness Weights Configuration...")
    configure_readiness_weights({
        "skill_strength": 0.50,
        "project_strength": 0.20,
        "interview_strength": 0.20,
        "profile_strength": 0.10
    })
    
    scores = evaluate_career_readiness(
        student_skills=["Java", "Go", "Redis"],
        linkedin_url="https://linkedin.com/in/test",
        github_username="test",
        resume_text="Implemented Redis and Go pipelines.",
        company_name="Blinkit",
        role_name="Software Development Engineer",
        qualification="3rd Year Student"
    )
    print(f"  Computed overall readiness score: {scores['overall_readiness']}%")
    assert "overall_readiness" in scores
    assert "career_stage" in scores
    assert "company_readiness" in scores
    print("  [PASS] Configurable weights checks passed!")

    # 4. Verify Upgraded Recommendation Engine Output
    print("Testing Recommendation Engine Output Structures...")
    rec = generate_recommendation(
        qualification="3rd Year Student",
        known_skills=["Java", "Git & GitHub"],
        dream_company="Blinkit",
        target_role="Software Development Engineer"
    )
    
    coach_recs = rec.get("coach_recommendations", [])
    print(f"  Coach recommendations output size: {len(coach_recs)}")
    assert len(coach_recs) > 0
    
    # Validate fields inside coach recommendations
    first_rec = coach_recs[0]
    print(f"  First recommendation: {first_rec['skill']} (Priority: {first_rec['priority']}, Impact: {first_rec['impact']})")
    print(f"  Evidence/Reason: '{first_rec['reason']}'")
    
    assert "priority" in first_rec
    assert "impact" in first_rec
    assert "reason" in first_rec
    assert "expected_readiness_increase" in first_rec
    
    # Check timeline for injected learning resources
    timeline = rec.get("timeline", {})
    stages = timeline.get("stages", [])
    assert len(stages) > 0
    
    stage_goals = stages[0].get("learning_goals", [])
    print(f"  Stage 1 learning goals: {stage_goals}")
    # Verify resources injected
    resources_injected = [g for g in stage_goals if "(" in g and ")" in g]
    print(f"  Resources injected under learning goals: {resources_injected}")
    
    # Verify similarity list matches
    sim_engineers = rec.get("similar_engineers", [])
    print(f"  Top Similar engineers count: {len(sim_engineers)}")
    assert len(sim_engineers) > 0
    assert "similarity_score" in sim_engineers[0]
    assert "company_name" in sim_engineers[0]
    
    print("  [PASS] Upgraded recommendation output format verified!")

    print("\nALL INTELLIGENCE UPGRADES CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_intelligence_upgrades()
