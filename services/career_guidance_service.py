# Career Guidance Service - Central Orchestrator
# CareerCompass AI

import sys
import os
import json
import logging
from typing import Dict, Any

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.database_connector import get_db_connection
from ai_engine.recommendation_engine import generate_recommendation

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CareerGuidanceService")

class CareerGuidanceService:
    """
    Central orchestrator service for CareerCompass AI.
    Ties together all engines: profile parsing, nlp processing,
    skill gap analysis, readiness scoring, and roadmap timeline generation.
    Loads student profile and skills directly from PostgreSQL.
    """

    @staticmethod
    def generate_career_guidance(student_id: str, target_company: str = "Blinkit", target_role: str = "Junior Software Engineer", skip_llm: bool = False) -> Dict[str, Any]:
        """
        Loads a student profile and their skills from PostgreSQL, runs the recommendation engine
        workflow, caches the results in career_assessments, and returns a unified JSON response.
        """
        logger.info(f"Generating career guidance for student: {student_id}, target: {target_company} ({target_role})")
        
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to PostgreSQL database.")
            raise RuntimeError("Database connection unavailable.")
            
        try:
            cur = conn.cursor()
            
            # 1. Fetch Student Profile
            cur.execute("""
                SELECT s.name, q.qualification_name, s.branch, s.cgpa, s.email, s.linkedin_url, s.github_username, s.resume_text,
                       s.candidate_profile_vector, s.candidate_projects, s.candidate_skill_confidence, s.candidate_metadata
                FROM students s
                LEFT JOIN qualifications q ON s.qualification_id = q.qualification_id
                WHERE s.student_id = %s
            """, (student_id,))
            student_row = cur.fetchone()
            
            if not student_row:
                cur.close()
                conn.close()
                raise ValueError(f"Student profile with ID {student_id} not found in database. Onboarding is required.")
                
            name, qualification, branch, cgpa, email, linkedin_url, github_username, resume_text, profile_vector, projects, skill_confidence, metadata = student_row
            qualification = qualification or "3rd Year Student"
            
            # 2. Fetch Student Skills
            cur.execute("""
                SELECT sk.skill_name
                FROM student_skills ss
                JOIN skills sk ON ss.skill_id = sk.skill_id
                WHERE ss.student_id = %s
            """, (student_id,))
            skills_rows = cur.fetchall()
            known_skills = [row[0] for row in skills_rows]
            
            # Rebuild candidate profile dynamically if JSONB fields are missing
            if not profile_vector or not projects or not skill_confidence or not metadata:
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
                
                profile = CandidateBuilder.build_profile(known_skills, parsed_res, parsed_gh, parsed_li)
                profile_vector = profile["candidate_profile_vector"]
                projects = profile["candidate_projects"]
                skill_confidence = profile["candidate_skill_confidence"]
                metadata = profile["candidate_metadata"]
                
                # Persist rebuilt structures in students table
                from psycopg2.extras import Json
                cur.execute("""
                    UPDATE students
                    SET candidate_profile_vector = %s,
                        candidate_projects = %s,
                        candidate_skill_confidence = %s,
                        candidate_metadata = %s
                    WHERE student_id = %s
                """, (Json(profile_vector), Json(projects), Json(skill_confidence), Json(metadata), student_id))
                conn.commit()
                
            candidate_profile = {
                "candidate_profile_vector": profile_vector,
                "candidate_projects": projects,
                "candidate_skill_confidence": skill_confidence,
                "candidate_metadata": metadata
            }

            logger.info(f"Loaded student '{name}' with {len(known_skills)} skills: {known_skills}")
            
            # Determine target sector (e.g. Quick-Commerce for Blinkit)
            target_sector = "Quick-Commerce"
            if target_company.lower() in ("amazon", "flipkart"):
                target_sector = "E-Commerce"
            elif target_company.lower() in ("google", "microsoft"):
                target_sector = "SaaS"
            elif target_company.lower() in ("tcs", "infosys"):
                target_sector = "Service-Based"
                
            # Determine experience years based on qualification
            experience_years = 0.0
            if qualification == "Junior Software Engineer":
                experience_years = 1.5
            elif qualification == "Trainee Engineer":
                experience_years = 0.5
                
            # 3. Generate recommendation details via recommendation engine
            rec_details = generate_recommendation(
                qualification=qualification,
                known_skills=known_skills,
                dream_company=target_company,
                dream_sector=target_sector,
                fresh_passout=False,
                target_role=target_role,
                linkedin_url=linkedin_url or "",
                github_username=github_username or "",
                resume_text=resume_text or "",
                cgpa=float(cgpa or 8.0),
                experience_years=experience_years,
                candidate_profile=candidate_profile,
                skip_llm=skip_llm
            )
            
            # 4. Cache Assessment in career_assessments Table
            cur.execute("SELECT assessment_id FROM career_assessments WHERE student_id = %s LIMIT 1", (student_id,))
            assessment_row = cur.fetchone()
            
            missing_skills_json = json.dumps(rec_details["gaps"])
            projects_json = json.dumps(rec_details["projects"])
            timeline_json = json.dumps(rec_details["timeline"])
            plan_json = json.dumps(rec_details["next_steps"]["30_day_action_plan"])
            stages_json = json.dumps(rec_details["timeline"]["stages"])
            
            if assessment_row:
                # Update existing cache
                cur.execute("""
                    UPDATE career_assessments
                    SET readiness_score = %s,
                        skill_score = %s,
                        project_score = %s,
                        resume_score = %s,
                        linkedin_score = %s,
                        github_score = %s,
                        interview_score = %s,
                        missing_skills = %s,
                        recommended_projects = %s,
                        next_30_day_plan = %s,
                        estimated_months_to_ready = %s,
                        generated_at = NOW()
                    WHERE student_id = %s
                """, (
                    rec_details["readiness_score"],
                    rec_details["assessment"]["skill_strength"],
                    rec_details["assessment"]["project_strength"],
                    rec_details["assessment"]["resume_score"],
                    rec_details["assessment"]["linkedin_score"],
                    rec_details["assessment"]["github_score"],
                    rec_details["assessment"]["interview_strength"],
                    missing_skills_json,
                    projects_json,
                    plan_json,
                    rec_details["timeline"]["months_remaining"],
                    student_id
                ))
            else:
                # Insert new cache
                cur.execute("""
                    INSERT INTO career_assessments (
                        student_id, readiness_score, skill_score, project_score, resume_score, linkedin_score, github_score, interview_score,
                        missing_skills, recommended_projects, next_30_day_plan, estimated_months_to_ready, generated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                """, (
                    student_id,
                    rec_details["readiness_score"],
                    rec_details["assessment"]["skill_strength"],
                    rec_details["assessment"]["project_strength"],
                    rec_details["assessment"]["resume_score"],
                    rec_details["assessment"]["linkedin_score"],
                    rec_details["assessment"]["github_score"],
                    rec_details["assessment"]["interview_strength"],
                    missing_skills_json,
                    projects_json,
                    plan_json,
                    rec_details["timeline"]["months_remaining"]
                ))
                
            # Save candidate skill gaps in candidate_skill_gaps table
            try:
                # 1. Clear existing gaps for student
                cur.execute("DELETE FROM candidate_skill_gaps WHERE student_id = %s", (int(student_id),))
                
                # 2. Insert missing and matched skills
                cur.execute("SELECT skill_id, skill_name FROM skills;")
                all_skills = cur.fetchall()
                s_map = {name.lower().strip(): s_id for s_id, name in all_skills}
                
                gaps_obj = rec_details.get("gaps", {})
                high_missing = gaps_obj.get("high_priority_missing", [])
                med_missing = gaps_obj.get("medium_priority_missing", [])
                low_missing = gaps_obj.get("low_priority_missing", [])
                matched = gaps_obj.get("matched_skills", [])
                
                for prio, skills_list in [("High", high_missing), ("Medium", med_missing), ("Low", low_missing)]:
                    for skill in skills_list:
                        s_low = skill.lower().strip()
                        if s_low in s_map:
                            cur.execute("""
                                INSERT INTO candidate_skill_gaps (student_id, skill_id, priority, status)
                                VALUES (%s, %s, %s, 'Missing')
                                ON CONFLICT (student_id, skill_id) DO NOTHING;
                            """, (int(student_id), s_map[s_low], prio))
                            
                for skill in matched:
                    s_low = skill.lower().strip()
                    if s_low in s_map:
                        cur.execute("""
                            INSERT INTO candidate_skill_gaps (student_id, skill_id, priority, status)
                            VALUES (%s, %s, 'None', 'Acquired')
                            ON CONFLICT (student_id, skill_id) DO NOTHING;
                        """, (int(student_id), s_map[s_low]))
            except Exception as gap_err:
                logger.warning(f"Failed to save to candidate_skill_gaps: {gap_err}")
                
            # 4b. Write to recommendation_audit_log table
            try:
                cur.execute("""
                    INSERT INTO recommendation_audit_log (
                        student_id, session_id, score_readiness, score_skills, score_projects,
                        score_interview, score_profile, score_company_fit,
                        missing_skills_count, recommended_projects_count, debug_message
                    ) VALUES (
                        %s, (SELECT session_id FROM analysis_sessions WHERE student_id = %s ORDER BY created_at DESC LIMIT 1), 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    int(student_id), int(student_id),
                    int(rec_details["readiness_score"]),
                    int(rec_details["assessment"]["skill_strength"]),
                    int(rec_details["assessment"]["project_strength"]),
                    int(rec_details["assessment"]["interview_strength"]),
                    int(rec_details["assessment"]["resume_score"]),
                    0, 
                    len(rec_details["gaps"].get("high_priority_missing", [])),
                    len(rec_details["projects"]),
                    f"Generated guidance details for target company: {target_company}, role: {target_role}."
                ))
            except Exception as audit_err:
                logger.warning(f"Failed to write to recommendation_audit_log: {audit_err}")
                
            conn.commit()
            cur.close()
            conn.close()
            
            # 5. Build and return unified response
            return {
                "student_id": student_id,
                "name": name,
                "qualification": qualification,
                "branch": branch,
                "cgpa": cgpa,
                "target_company": target_company,
                "target_role": target_role,
                "known_skills": known_skills,
                "readiness_score": rec_details["readiness_score"],
                "gaps": rec_details["gaps"],
                "timeline": rec_details["timeline"],
                "projects": rec_details["projects"],
                "resources": rec_details["resources"],
                "recommended_questions": rec_details["recommended_questions"],
                
                # Legacy structures for UI binding compatibility
                "assessment": rec_details["assessment"],
                "next_steps": rec_details["next_steps"],
                "urgency_level": rec_details["urgency_level"],
                "message": rec_details["message"]
            }
            
        except Exception as e:
            logger.error(f"Error during career guidance orchestration: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise RuntimeError(f"Orchestration failure: {e}")


