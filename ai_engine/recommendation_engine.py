# Orchestrator Recommendation Engine - CareerCompass AI

import sys
import os
import hashlib
import json
import logging

# Ensure this directory and project root are in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.decision_engine.registry import registry
from ai_engine.assessment.skill_assessor import get_role_skills_requirements

logger = logging.getLogger("RecommendationEngine")
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".cache", "guidance_cache"))

def get_cache_key(qualification, known_skills, dream_company, target_role, cgpa, experience_years, skip_llm):
    skills_str = ",".join(sorted(known_skills or []))
    key_str = f"{qualification}|{skills_str}|{dream_company}|{target_role}|{cgpa}|{experience_years}|{skip_llm}"
    return hashlib.md5(key_str.encode("utf-8")).hexdigest()

def get_cached_recommendation(qualification, known_skills, dream_company, target_role, cgpa, experience_years, skip_llm):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    key = get_cache_key(qualification, known_skills, dream_company, target_role, cgpa, experience_years, skip_llm)
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def set_cached_recommendation(qualification, known_skills, dream_company, target_role, cgpa, experience_years, skip_llm, data):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    key = get_cache_key(qualification, known_skills, dream_company, target_role, cgpa, experience_years, skip_llm)
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def generate_recommendation(
    qualification: str, 
    known_skills: list[str], 
    dream_company: str = "Blinkit", 
    dream_sector: str = "Quick-Commerce", 
    fresh_passout: bool = False, 
    target_role: str = "Software Development Engineer (SDE)",
    linkedin_url: str = "",
    github_username: str = "",
    resume_text: str = "",
    cgpa: float = 8.0,
    experience_years: float = 0.0,
    candidate_profile: dict = None,
    skip_llm: bool = False
) -> dict:
    """
    Combines all modular engines via the Registry pattern to build the complete career plan.
    Deterministic algorithms generate the timeline roadmap stages, projects, and questions.
    Gemini is only invoked to generate a conversational coaching explanation ('message').
    """
    # Check cache first
    cached_data = get_cached_recommendation(
        qualification=qualification,
        known_skills=known_skills,
        dream_company=dream_company,
        target_role=target_role,
        cgpa=cgpa,
        experience_years=experience_years,
        skip_llm=skip_llm
    )
    if cached_data:
        return cached_data

    # Ensure profile builds
    if not candidate_profile:
        from profile_analyzer.linkedin_parser import LinkedInParser
        from profile_analyzer.github_analyzer import GitHubAnalyzer
        from profile_analyzer.resume_parser import ResumeParser
        from ai_engine.profile.candidate_builder import CandidateBuilder
        
        parsed_li = {}
        parsed_gh = {}
        parsed_res = {}
        if linkedin_url:
            try: parsed_li = LinkedInParser.parse_profile(linkedin_url, target_role=target_role, qualification=qualification)
            except Exception: parsed_li = {}
        if github_username:
            try: parsed_gh = GitHubAnalyzer.analyze_profile(github_username)
            except Exception: parsed_gh = {}
        if resume_text:
            try: parsed_res = ResumeParser.parse_resume(resume_text)
            except Exception: parsed_res = {}
            
        candidate_profile = CandidateBuilder.build_profile(known_skills, parsed_res, parsed_gh, parsed_li)

    # 1. Run Assessment Engine
    assessment_scores = registry.readiness_engine.evaluate_readiness(
        student_skills=known_skills,
        linkedin_url=linkedin_url,
        github_username=github_username,
        resume_text=resume_text,
        company_name=dream_company,
        role_name=target_role,
        qualification=qualification,
        experience_years=experience_years,
        candidate_profile=candidate_profile
    )
    
    # Calculate overall readiness score
    from readiness_score import calculate_readiness
    readiness_score = int(assessment_scores["overall_readiness"])
    if not linkedin_url and not github_username and not resume_text:
        # Fallback to pure skill-based readiness for legacy tests compatibility
        readiness_score = calculate_readiness(known_skills)
        assessment_scores["overall_readiness"] = readiness_score
    
    # 2. Run Similarity Engine
    similar_engineers = registry.similarity_engine.find_similar_engineers(
        student_skills=known_skills,
        target_company=dream_company,
        target_role=target_role,
        experience_years=experience_years,
        gpa=cgpa,
        qualification=qualification,
        limit=5
    )
    
    # 3. Analyze Career Twins (Peer transitions and paths)
    paths_analysis = registry.career_twin_engine.analyze_career_twins(similar_engineers, known_skills)
    missing_freqs = paths_analysis["missing_skills_frequency"]
    similar_projects = paths_analysis["common_projects"]
    similar_transitions = paths_analysis["common_transitions"]

    # 4. Analyze Gaps
    gaps = registry.skill_gap_engine.analyze_gaps(known_skills, dream_company, target_role)
    matched_skills = gaps["matched"]
    missing_skills = gaps["missing"]

    high_missing = list(missing_skills.get("High", []))
    med_missing = list(missing_skills.get("Medium", []))
    low_missing = list(missing_skills.get("Low", []))
    
    # 5. Compute Priority Score, Expected Impact, and Similar-Peer Evidence
    company_reqs = get_role_skills_requirements(dream_company, target_role)
    coach_recs = []
    
    for category, skills_list in [("High", high_missing), ("Medium", med_missing), ("Low", low_missing)]:
        base_priority = 8.0 if category == "High" else (5.0 if category == "Medium" else 2.0)
        for skill in skills_list:
            freq = missing_freqs.get(skill, 0.0)
            
            comp_prio = company_reqs.get(skill, "Not Required")
            if comp_prio == "High":
                comp_weight = 1.0
            elif comp_prio == "Medium":
                comp_weight = 0.6
            elif comp_prio == "Low":
                comp_weight = 0.2
            else:
                comp_weight = 0.0
                
            priority_score = (base_priority * 0.4) + (freq * 3.5) + (comp_weight * 2.5)
            priority_score = min(round(priority_score, 1), 10.0)
            
            impact = "High" if priority_score >= 7.5 else ("Medium" if priority_score >= 4.5 else "Low")
            expected_increase = round(priority_score * 0.8, 1)
            
            if freq > 0 and comp_prio != "Not Required":
                reason = f"Mastered by {int(freq * 100)}% of matched SDE peers at {dream_company}. Mapped as '{comp_prio}' priority in target job requirements. (+{expected_increase}% Readiness)."
            elif freq > 0:
                reason = f"Mastered by {int(freq * 100)}% of matched SDE peers at {dream_company}. Highly recommended for overall stack breadth. (+{expected_increase}% Readiness)."
            elif comp_prio != "Not Required":
                reason = f"Required SDE competency ('{comp_prio}' priority) for {dream_company} {target_role} candidates. (+{expected_increase}% Readiness)."
            else:
                reason = f"Supplementary SDE skill gap matching standard candidate profiles. (+{expected_increase}% Readiness)."
                
            coach_recs.append({
                "skill": skill,
                "priority": priority_score,
                "impact": impact,
                "reason": reason,
                "expected_readiness_increase": expected_increase
            })
            
    coach_recs.sort(key=lambda x: x["priority"], reverse=True)

    # 6. Run Roadmap Planner & Adaptive Engine stubs
    timeline_data = registry.roadmap_planner.generate_roadmap(
        qualification=qualification,
        missing_skills=missing_skills,
        dream_company=dream_company,
        dream_sector=dream_sector,
        fresh_passout=fresh_passout,
        target_role=target_role,
        similar_engineers=similar_engineers,
        assessment_scores=assessment_scores,
        candidate_profile=candidate_profile
    )
    
    # Run Career Strategy & Adaptive Learning extensions
    strategy_data = registry.career_strategy_engine.determine_priorities(
        student_profile={"gpa": cgpa, "skills": known_skills},
        readiness_score=readiness_score
    )
    adapted_timeline = registry.adaptive_learning_engine.adapt_roadmap(
        current_roadmap=timeline_data,
        assessment_history=[]
    )
    
    calculated_months = adapted_timeline.get("months_remaining")
    calculated_weekly_hours = adapted_timeline.get("weekly_hours_recommended")
    legacy_urgency = adapted_timeline.get("urgency")

    # 7. Run Interview Question Planner
    recommended_questions = registry.interview_planner.recommend_questions(
        missing_skills=missing_skills,
        dream_company=dream_company,
        dream_sector=dream_sector
    )

    # 7.5 Calculate experimental ML specialization affinity scores
    ml_affinity = {
        "general_engineering_score": 0.0,
        "backend_affinity_score": 0.0,
        "frontend_affinity_score": 0.0,
        "model_version": "1.0.0",
        "dataset_version": "1.0.0",
        "ontology_version": "1.1.0",
        "supported": False,
        "confidence_status": "low",
        "limitations": "ML specialization affinity engine not registered."
    }
    
    if registry.ml_affinity_engine:
        college_val = "Other"
        if candidate_profile and isinstance(candidate_profile, dict):
            metadata = candidate_profile.get("metadata", {})
            if isinstance(metadata, dict):
                edu_str = metadata.get("education", "")
                if edu_str:
                    college_val = edu_str
        
        ml_affinity = registry.ml_affinity_engine.calculate_affinities(
            student_skills=known_skills,
            experience_years=experience_years,
            college=college_val,
            degree=qualification
        )

    # 8. Run Explainability Decision Trace
    decision_trace = registry.decision_trace_exporter.build_trace(
        inputs={
            "dream_company": dream_company,
            "target_role": target_role,
            "qualification": qualification,
            "fresh_passout": fresh_passout
        },
        outputs={
            "readiness_score": readiness_score,
            "similar_engineers": similar_engineers,
            "timeline": adapted_timeline,
            "ml_affinity": ml_affinity
        }
    )

    # Compile coach explanation (Gemini vs Heuristic Fallback)
    coach_message = f"Based on your profile, you have an SDE readiness score of {readiness_score}%. Focus on closing key skill gaps."

    total_required_skills = len(matched_skills) + len(high_missing) + len(med_missing) + len(low_missing)
    
    # Extract action plan for legacy structure compatibility
    action_plan = []
    stages_list = adapted_timeline.get("stages", [])
    for i, stage in enumerate(stages_list):
        action_plan.append(f"Week {i+1}: {stage.get('title')} - {stage.get('focus')[:60]}...")

    legacy_high_missing = list(high_missing)
    if legacy_urgency in ("Critical", "High", "Critical (Needs Acceleration)"):
        legacy_high_missing += med_missing
        legacy_high_missing += low_missing
    else:
        legacy_high_missing += med_missing

    legacy_gaps = {
        "high_priority_missing": legacy_high_missing,
        "medium_priority_missing": med_missing,
        "low_priority_missing": low_missing
    }

    legacy_assessment = {
        "readiness_score": readiness_score,
        "skills_matched": len(matched_skills),
        "skills_required": total_required_skills,
        "skills_you_have": matched_skills,
        "skill_strength": assessment_scores.get("skill_strength", 0.5),
        "project_strength": assessment_scores.get("project_strength", 0.5),
        "interview_strength": assessment_scores.get("interview_strength", 0.5),
        "profile_strength": assessment_scores.get("profile_strength", 0.5),
        "linkedin_score": assessment_scores.get("linkedin_score", 50),
        "github_score": assessment_scores.get("github_score", 50),
        "resume_score": assessment_scores.get("resume_score", 50)
    }

    legacy_next_steps = {
        "immediate_priority_skills": legacy_high_missing[:3],
        "30_day_action_plan": action_plan,
        "recommended_projects": [p.get("name") for p in adapted_timeline.get("projects", [])],
        "estimated_months_to_ready": calculated_months,
        "weekly_study_hours_recommended": calculated_weekly_hours
    }

    res = {
        "qualification": qualification,
        "known_skills": known_skills,
        "dream_company": dream_company,
        "dream_sector": dream_sector,
        "fresh_passout": fresh_passout,
        "target_role": target_role,
        "readiness_score": readiness_score,
        "assessment_scores": assessment_scores,
        "similar_engineers": similar_engineers,
        "coach_recommendations": coach_recs,
        "common_transitions": similar_transitions,
        "common_projects": similar_projects,
        "gaps": {
            "high_priority_missing": high_missing,
            "medium_priority_missing": med_missing,
            "low_priority_missing": low_missing,
            "matched_skills": matched_skills
        },
        "timeline": {
            "months_remaining": calculated_months,
            "weekly_hours_recommended": calculated_weekly_hours,
            "urgency": legacy_urgency,
            "stages": stages_list
        },
        "projects": adapted_timeline.get("projects", []),
        "resources": adapted_timeline.get("resources", []),
        "recommended_questions": recommended_questions,
        
        # New upgrades integration
        "decision_trace": decision_trace,
        "strategy_data": strategy_data,
        "ml_affinity": ml_affinity,
        
        # Legacy fields for run_tests.py compatibility
        "input": {
            "qualification": qualification,
            "known_skills": known_skills,
            "target_company": dream_company,
            "target_role": target_role
        },
        "assessment": legacy_assessment,
        "gaps_legacy": legacy_gaps,
        "next_steps": legacy_next_steps,
        "urgency_level": legacy_urgency,
        "message": coach_message
    }
    
    set_cached_recommendation(
        qualification=qualification,
        known_skills=known_skills,
        dream_company=dream_company,
        target_role=target_role,
        cgpa=cgpa,
        experience_years=experience_years,
        skip_llm=skip_llm,
        data=res
    )
    return res
