# API Routes - CareerCompass AI

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
import sys
import os
import io
import pypdf

# Include root in import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.recommendation_engine import generate_recommendation
from ai_engine.roadmap_generator import generate_timeline
from ai_engine.skill_gap_engine import analyze_gaps
from ai_engine.readiness_score import calculate_readiness
from ai_engine.interview_recommender import recommend_questions
from ai_engine.assessment.skill_assessor import get_role_skills_requirements
from services.career_guidance_service import CareerGuidanceService
from profile_analyzer.linkedin_parser import LinkedInParser
from profile_analyzer.github_analyzer import GitHubAnalyzer
from profile_analyzer.resume_parser import ResumeParser
from profile_analyzer.skill_extractor import SkillExtractor
from ai_engine.profile.candidate_builder import CandidateBuilder

from api.database_connector import (
    get_db_connection, query_stats, get_hiring_signals, get_stage_training, get_stage_assessment, get_profile_builder_template,
    get_company_job_description, get_company_interview_experiences, get_skill_roadmap_details,
    create_analysis_session, get_analysis_session, update_analysis_session_status, get_career_transitions
)
from ai_engine.nlp.nlp_classifier import classify_and_respond

router = APIRouter()

class AuthRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register_user(req: AuthRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("SELECT user_id FROM users WHERE LOWER(username) = %s LIMIT 1", (req.username.lower(),))
        if cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Username already exists.")
            
        if len(req.password) < 6:
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
            
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (req.username, req.password))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "Account created successfully."}
    except Exception as e:
        if conn: conn.close()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login_user(req: AuthRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("SELECT password FROM users WHERE LOWER(username) = %s LIMIT 1", (req.username.lower(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row or row[0] != req.password:
            raise HTTPException(status_code=401, detail="Invalid username or password.")
            
        return {"success": True, "username": req.username}
    except Exception as e:
        if conn: conn.close()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/student/parse-resume")
def parse_resume_pdf(file: UploadFile = File(...)):
    try:
        content = file.file.read()
        if file.filename.lower().endswith('.pdf'):
            pdf_stream = io.BytesIO(content)
            reader = pypdf.PdfReader(pdf_stream)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        else:
            text = content.decode('utf-8', errors='ignore')
            
        parsed_data = ResumeParser.parse_resume(text)
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

class AssessmentRequest(BaseModel):
    qualification: str
    known_skills: list[str]
    branch: str = ""
    cgpa: float = 0.0
    dream_company: str = "Blinkit"
    dream_sector: str = "Quick-Commerce"
    fresh_passout: bool = False
    target_role: str = "Software Development Engineer (SDE)"
    skip_llm: bool = False

class ChatRequest(BaseModel):
    message: str
    stage_title: str = ""
    dream_company: str = ""
    dream_sector: str = ""
    qualification: str = ""
    session_id: str = ""

class StageProgressRequest(BaseModel):
    stage_title: str
    status: str
    completion_pct: int = 0

# Request schemas for new database-driven endpoints
class AnalyzeRequest(BaseModel):
    name: str = ""
    linkedin_url: str = ""
    github_username: str = ""
    resume_text: str = ""
    known_skills: list[str] = []
    qualification: str = "3rd Year Student"
    branch: str = "Computer Science"
    cgpa: float = 8.0
    dream_company: str = "Blinkit"
    dream_sector: str = "Quick-Commerce"
    fresh_passout: bool = False
    target_role: str = "Software Development Engineer (SDE)"

class RecommendRequest(BaseModel):
    name: str = "SDE Candidate"
    qualification: str = "3rd Year Student"
    branch: str = "Computer Science"
    cgpa: float = 8.0
    dream_company: str = "Blinkit"
    dream_sector: str = "Quick-Commerce"
    fresh_passout: bool = False
    target_role: str = "Software Development Engineer (SDE)"
    known_skills: list[str] = []
    linkedin_url: str = ""
    github_username: str = ""
    resume_text: str = ""
    text_input: str = ""
    student_id: int = None
    session_id: str = None
    skip_llm: bool = False

class UpdateProgressRequest(BaseModel):
    status: str


class RoadmapRequest(BaseModel):
    student_id: str = ""
    qualification: str = ""
    known_skills: list[str] = []
    dream_company: str = "Blinkit"
    dream_sector: str = "Quick-Commerce"
    fresh_passout: bool = False
    target_role: str = "Software Development Engineer (SDE)"
    skip_llm: bool = False

class ReadinessRequest(BaseModel):
    student_id: str = ""
    known_skills: list[str] = []

class InterviewPlanRequest(BaseModel):
    student_id: str = ""
    target_company: str = ""
    dream_company: str = ""
    dream_sector: str = ""
    target_role: str = ""
    known_skills: list[str] = []
    skip_llm: bool = False

class RecommendationsRequest(BaseModel):
    student_id: str = ""
    target_company: str = "Blinkit"
    target_role: str = "Software Development Engineer (SDE)"
    known_skills: list[str] = []
    skip_llm: bool = False

class CareerGuidanceRequest(BaseModel):
    student_id: str
    target_company: str = "Blinkit"
    target_role: str = "Software Development Engineer (SDE)"
    skip_llm: bool = False

@router.post("/assess")
def assess_student(req: AssessmentRequest):
    try:
        plan = generate_recommendation(
            req.qualification, 
            req.known_skills,
            dream_company=req.dream_company,
            dream_sector=req.dream_sector,
            fresh_passout=req.fresh_passout,
            target_role=req.target_role,
            skip_llm=req.skip_llm
        )
        plan["branch"] = req.branch
        plan["cgpa"] = req.cgpa
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/student/analyze")
def analyze_student_profile(req: AnalyzeRequest):
    try:
        parsed_li = {}
        parsed_gh = {}
        parsed_res = {}
        
        if req.linkedin_url:
            try:
                parsed_li = LinkedInParser.parse_profile(req.linkedin_url, target_role=req.target_role, qualification=req.qualification)
            except Exception as e:
                parsed_li = {"error": f"LinkedIn profile analysis is temporarily unavailable: {str(e)}", "skills_raw": []}
            
        if req.github_username:
            try:
                parsed_gh = GitHubAnalyzer.analyze_profile(req.github_username)
            except Exception as e:
                parsed_gh = {"error": f"GitHub profile analysis is temporarily unavailable: {str(e)}", "skills_raw": [], "frequency_map": {}}
            
        if req.resume_text:
            try:
                parsed_res = ResumeParser.parse_resume(req.resume_text)
            except Exception as e:
                parsed_res = {"error": f"Unable to extract resume information: {str(e)}", "skills_raw": []}
            
        # 1. Build unified candidate profile using CandidateBuilder
        profile = CandidateBuilder.build_profile(req.known_skills, parsed_res, parsed_gh, parsed_li)
        
        # 2. Persist profile and student record to database
        conn = get_db_connection()
        student_id = None
        session_id = None
        if conn:
            try:
                cur = conn.cursor()
                
                # Fetch qualification_id
                cur.execute("SELECT qualification_id FROM qualifications WHERE LOWER(qualification_name) = %s LIMIT 1", (req.qualification.lower(),))
                row = cur.fetchone()
                qualification_id = row[0] if row else 3
                
                # Fetch target_company_role_id
                cur.execute("""
                    SELECT cr.company_role_id 
                    FROM company_roles cr
                    JOIN companies c ON cr.company_id = c.company_id
                    JOIN roles r ON cr.role_id = r.role_id
                    WHERE LOWER(c.company_name) = %s AND LOWER(r.role_name) = %s 
                    LIMIT 1
                """, (req.dream_company.lower(), req.target_role.lower()))
                row = cur.fetchone()
                if not row:
                    cur.execute("""
                        SELECT cr.company_role_id 
                        FROM company_roles cr
                        JOIN companies c ON cr.company_id = c.company_id
                        JOIN roles r ON cr.role_id = r.role_id
                        WHERE LOWER(c.company_name) = 'blinkit' AND LOWER(r.role_name) = 'software development engineer (sde)'
                        LIMIT 1
                    """)
                    row = cur.fetchone()
                company_role_id = row[0] if row else 1982
                
                import uuid
                from psycopg2.extras import Json
                unique_suffix = uuid.uuid4().hex[:8]
                email = f"{req.name.lower().replace(' ', '_')}_{unique_suffix}@careercompass.ai"
                
                cur.execute("SELECT student_id FROM students WHERE email = %s LIMIT 1", (email,))
                row = cur.fetchone()
                
                vector_json = Json(profile["candidate_profile_vector"])
                projects_json = Json(profile["candidate_projects"])
                confidence_json = Json(profile["candidate_skill_confidence"])
                metadata_json = Json(profile["candidate_metadata"])
                
                if row:
                    student_id = int(row[0])
                    cur.execute("""
                        UPDATE students
                        SET name = %s,
                            qualification_id = %s,
                            branch = %s,
                            cgpa = %s,
                            target_company_role_id = %s,
                            linkedin_url = %s,
                            github_username = %s,
                            resume_text = %s,
                            candidate_profile_vector = %s,
                            candidate_projects = %s,
                            candidate_skill_confidence = %s,
                            candidate_metadata = %s
                        WHERE student_id = %s
                    """, (req.name, qualification_id, req.branch, req.cgpa, company_role_id, req.linkedin_url, req.github_username, req.resume_text, 
                          vector_json, projects_json, confidence_json, metadata_json, student_id))
                else:
                    cur.execute("""
                        INSERT INTO students (name, email, qualification_id, branch, cgpa, target_company_role_id, linkedin_url, github_username, resume_text,
                                             candidate_profile_vector, candidate_projects, candidate_skill_confidence, candidate_metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING student_id
                    """, (req.name, email, qualification_id, req.branch, req.cgpa, company_role_id, req.linkedin_url, req.github_username, req.resume_text,
                          vector_json, projects_json, confidence_json, metadata_json))
                    student_id = int(cur.fetchone()[0])
                    
                # Create session in analysis_sessions
                cur.execute("""
                    INSERT INTO analysis_sessions (student_id, target_company, target_role, status)
                    VALUES (%s, %s, %s, 'analyzed')
                    RETURNING session_id
                """, (student_id, req.dream_company, req.target_role))
                session_id = str(cur.fetchone()[0])
                
                conn.commit()
                cur.close()
                conn.close()
            except Exception as db_err:
                if conn: conn.rollback(); conn.close()
                print("Database error during analyze registration:", db_err)
        
        # Format the return keys expected by frontend/tests
        extracted_skills = []
        for s_name, s_meta in profile["candidate_skill_confidence"].items():
            extracted_skills.append({
                "name": s_name,
                "confidence": s_meta["confidence"],
                "confidence_score": s_meta["confidence_score"],
                "sources": s_meta["sources"],
                "github_frequency": s_meta["github_frequency"]
            })
            
        return {
            "student_id": student_id,
            "session_id": session_id,
            "linkedin_parsed": parsed_li,
            "github_parsed": parsed_gh,
            "resume_parsed": parsed_res,
            "extracted_skills": extracted_skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend")
def recommend_career_guidance(req: RecommendRequest):
    try:
        # Upsert student profile in PostgreSQL
        conn = get_db_connection()
        if not conn:
            raise RuntimeError("Database connection unavailable.")
            
        cur = conn.cursor()
        
        # 1. Fetch qualification_id
        cur.execute("SELECT qualification_id FROM qualifications WHERE LOWER(qualification_name) = %s LIMIT 1", (req.qualification.lower(),))
        row = cur.fetchone()
        qualification_id = row[0] if row else 3
        
        # 2. Fetch target_company_role_id
        cur.execute("""
            SELECT cr.company_role_id 
            FROM company_roles cr
            JOIN companies c ON cr.company_id = c.company_id
            JOIN roles r ON cr.role_id = r.role_id
            WHERE LOWER(c.company_name) = %s AND LOWER(r.role_name) = %s 
            LIMIT 1
        """, (req.dream_company.lower(), req.target_role.lower()))
        row = cur.fetchone()
        if not row:
            cur.execute("""
                SELECT cr.company_role_id 
                FROM company_roles cr
                JOIN companies c ON cr.company_id = c.company_id
                JOIN roles r ON cr.role_id = r.role_id
                WHERE LOWER(c.company_name) = 'blinkit' AND LOWER(r.role_name) = 'software development engineer (sde)'
                LIMIT 1
            """)
            row = cur.fetchone()
        company_role_id = row[0] if row else 1982
        
        # 3. Check/Get student_id
        student_id = req.student_id
        if not student_id and req.session_id:
            cur.execute("SELECT student_id FROM analysis_sessions WHERE session_id = %s LIMIT 1", (req.session_id,))
            s_row = cur.fetchone()
            if s_row:
                student_id = int(s_row[0])
                
        db_li = ""
        db_gh = ""
        db_res = ""
        if student_id:
            cur.execute("""
                SELECT linkedin_url, github_username, resume_text 
                FROM students 
                WHERE student_id = %s LIMIT 1
            """, (student_id,))
            s_exist = cur.fetchone()
            if s_exist:
                db_li = s_exist[0] or ""
                db_gh = s_exist[1] or ""
                db_res = s_exist[2] or ""
                
        if not student_id:
            import uuid
            unique_suffix = uuid.uuid4().hex[:8]
            email = f"{req.name.lower().replace(' ', '_')}_{unique_suffix}@careercompass.ai"
            cur.execute("""
                INSERT INTO students (name, email, qualification_id, branch, cgpa, target_company_role_id, linkedin_url, github_username, resume_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING student_id
            """, (req.name, email, qualification_id, req.branch, req.cgpa, company_role_id, req.linkedin_url, req.github_username, req.resume_text))
            student_id = int(cur.fetchone()[0])
            
        # Re-resolve urls/text for analyzer re-runs
        li_url = req.linkedin_url or db_li
        gh_user = req.github_username or db_gh
        res_txt = req.resume_text or db_res

        parsed_li = {}
        parsed_gh = {}
        parsed_res = {}
        
        if li_url:
            try:
                parsed_li = LinkedInParser.parse_profile(li_url, target_role=req.target_role, qualification=req.qualification)
            except Exception as e:
                parsed_li = {"error": str(e), "skills_raw": []}
        if gh_user:
            try:
                parsed_gh = GitHubAnalyzer.analyze_profile(gh_user)
            except Exception as e:
                parsed_gh = {"error": str(e), "skills_raw": [], "frequency_map": {}}
        if res_txt:
            try:
                parsed_res = ResumeParser.parse_resume(res_txt)
            except Exception as e:
                parsed_res = {"error": str(e), "skills_raw": []}
                
        # Build unified candidate profile
        profile = CandidateBuilder.build_profile(req.known_skills, parsed_res, parsed_gh, parsed_li)
        
        from psycopg2.extras import Json
        vector_json = Json(profile["candidate_profile_vector"])
        projects_json = Json(profile["candidate_projects"])
        confidence_json = Json(profile["candidate_skill_confidence"])
        metadata_json = Json(profile["candidate_metadata"])

        # Update student profile with JSONB structures
        cur.execute("""
            UPDATE students
            SET name = %s,
                qualification_id = %s,
                branch = %s,
                cgpa = %s,
                target_company_role_id = %s,
                linkedin_url = %s,
                github_username = %s,
                resume_text = %s,
                candidate_profile_vector = %s,
                candidate_projects = %s,
                candidate_skill_confidence = %s,
                candidate_metadata = %s
            WHERE student_id = %s
        """, (req.name, qualification_id, req.branch, req.cgpa, company_role_id, li_url, gh_user, res_txt, 
              vector_json, projects_json, confidence_json, metadata_json, student_id))
            
        # 4. Clear and insert skills in student_skills
        cur.execute("DELETE FROM student_skills WHERE student_id = %s", (student_id,))
        for skill_name in req.known_skills:
            cur.execute("SELECT skill_id FROM skills WHERE LOWER(skill_name) = %s LIMIT 1", (skill_name.lower(),))
            s_row = cur.fetchone()
            if s_row:
                cur.execute("""
                    INSERT INTO student_skills (student_id, skill_id, proficiency)
                    VALUES (%s, %s, 'Intermediate')
                    ON CONFLICT DO NOTHING
                """, (student_id, s_row[0]))
                
        # 5. Handle session_id updates
        session_id = req.session_id
        if session_id:
            cur.execute("""
                UPDATE analysis_sessions
                SET status = 'skills_confirmed'
                WHERE session_id = %s
            """, (session_id,))
        else:
            cur.execute("""
                INSERT INTO analysis_sessions (student_id, target_company, target_role, status)
                VALUES (%s, %s, %s, 'skills_confirmed')
                RETURNING session_id
            """, (student_id, req.dream_company, req.target_role))
            session_id = str(cur.fetchone()[0])
                
        conn.commit()
        cur.close()
        conn.close()
        
        # 6. Call CareerGuidanceService to calculate plan details (returns dynamically computed payload)
        res = CareerGuidanceService.generate_career_guidance(
            student_id=str(student_id),
            target_company=req.dream_company,
            target_role=req.target_role,
            skip_llm=req.skip_llm
        )
        res["student_id"] = student_id
        res["session_id"] = session_id
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_dynamic_guidance(session_id: str, skip_llm: bool = False) -> dict:
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        
        # 1. Fetch Session
        cur.execute("""
            SELECT student_id, target_company, target_role, status
            FROM analysis_sessions
            WHERE session_id = %s
        """, (session_id,))
        session_row = cur.fetchone()
        if not session_row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Session not found.")
            
        student_id, target_company, target_role, status = session_row
        
        # 2. Fetch Student Profile
        cur.execute("""
            SELECT s.name, q.qualification_name, s.branch, s.cgpa, s.email, s.college, s.linkedin_url, s.github_username, s.resume_text
            FROM students s
            LEFT JOIN qualifications q ON s.qualification_id = q.qualification_id
            WHERE s.student_id = %s
        """, (student_id,))
        student_row = cur.fetchone()
        if not student_row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Student not found.")
            
        name, qualification, branch, cgpa, email, college, linkedin_url, github_username, resume_text = student_row
        qualification = qualification or "3rd Year Student"
        
        # 3. Fetch Student Skills
        cur.execute("""
            SELECT sk.skill_name
            FROM student_skills ss
            JOIN skills sk ON ss.skill_id = sk.skill_id
            WHERE ss.student_id = %s
        """, (student_id,))
        skills_rows = cur.fetchall()
        known_skills = [row[0] for row in skills_rows]
        
        cur.close()
        conn.close()
        
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
            
        rec = generate_recommendation(
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
            skip_llm=skip_llm
        )
        
        rec["name"] = name
        rec["student_id"] = student_id
        rec["session_id"] = session_id
        rec["branch"] = branch
        rec["cgpa"] = cgpa
        rec["qualification"] = qualification
        rec["dream_company"] = target_company
        rec["dream_sector"] = target_sector
        rec["target_role"] = target_role
        rec["status"] = status
        rec["resume_text"] = resume_text
        
        return rec
    except Exception as e:
        if conn: conn.close()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
def get_session_details(session_id: str):
    sess = get_analysis_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found.")
    return sess

@router.post("/session/{session_id}/progress")
def update_session_progress(session_id: str, req: UpdateProgressRequest):
    success = update_analysis_session_status(session_id, req.status)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update session progress.")
    return {"success": True, "status": req.status}

@router.post("/session/{session_id}/stage-progress")
def update_stage_progress(session_id: str, req: StageProgressRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        
        # Resolve student_id
        cur.execute("SELECT student_id FROM analysis_sessions WHERE session_id = %s LIMIT 1", (session_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Session not found.")
            
        student_id = row[0]
        
        # Upsert stage progress
        cur.execute("""
            INSERT INTO student_dynamic_progress (student_id, stage_title, status, completion_pct)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id, stage_title)
            DO UPDATE SET status = EXCLUDED.status, completion_pct = EXCLUDED.completion_pct
        """, (student_id, req.stage_title, req.status, req.completion_pct))
        
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "stage_title": req.stage_title, "status": req.status}
    except Exception as e:
        if conn: conn.close()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/stage-progress")
def get_stage_progress(session_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        
        # Resolve student_id
        cur.execute("SELECT student_id FROM analysis_sessions WHERE session_id = %s LIMIT 1", (session_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Session not found.")
            
        student_id = row[0]
        
        # Fetch stage progress
        cur.execute("""
            SELECT stage_title, status, completion_pct 
            FROM student_dynamic_progress 
            WHERE student_id = %s
        """, (student_id,))
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        progress = []
        for r in rows:
            progress.append({
                "stage_title": r[0],
                "status": r[1],
                "completion_pct": r[2]
            })
        return {"success": True, "progress": progress}
    except Exception as e:
        if conn: conn.close()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/readiness/{session_id}")
def get_readiness_by_session(session_id: str, skip_llm: bool = False):
    rec = get_dynamic_guidance(session_id, skip_llm=skip_llm)
    return {
        "readiness_score": rec["readiness_score"],
        "name": rec["name"],
        "dream_company": rec["dream_company"],
        "dream_sector": rec["dream_sector"],
        "timeline": rec["timeline"],
        "qualification": rec["qualification"],
        "branch": rec["branch"],
        "cgpa": rec["cgpa"],
        "gaps": rec["gaps"],
        "assessment_scores": rec.get("assessment_scores", {}),
        "similar_engineers": rec.get("similar_engineers", []),
        "common_transitions": rec.get("common_transitions", []),
        "common_projects": rec.get("common_projects", []),
        "known_skills": rec.get("known_skills", []),
        "projects": rec.get("projects", []),
        "recommended_next_project": rec.get("recommended_next_project"),
        "resume_text": rec.get("resume_text", ""),
        "common_projects": rec.get("common_projects", [])
    }

@router.get("/recommendations/{session_id}")
def get_recommendations_by_session(session_id: str, skip_llm: bool = False):
    rec = get_dynamic_guidance(session_id, skip_llm=skip_llm)
    return {
        "projects": rec["projects"],
        "resources": rec["resources"],
        "coach_recommendations": rec.get("coach_recommendations", [])
    }

@router.get("/interview-plan/{session_id}")
def get_interview_plan_by_session(session_id: str, skip_llm: bool = False):
    rec = get_dynamic_guidance(session_id, skip_llm=skip_llm)
    return {
        "recommended_questions": rec["recommended_questions"]
    }

@router.get("/roadmap/{session_id}")
def get_roadmap_by_session(session_id: str, skip_llm: bool = False):
    rec = get_dynamic_guidance(session_id, skip_llm=skip_llm)
    return rec["timeline"]

@router.post("/roadmap")
def get_roadmap_timeline(req: RoadmapRequest):
    try:
        if req.student_id:
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id, req.dream_company, req.target_role, skip_llm=req.skip_llm)
            return guidance["timeline"]
        else:
            rec = generate_recommendation(
                qualification=req.qualification,
                known_skills=req.known_skills,
                dream_company=req.dream_company,
                dream_sector=req.dream_sector,
                fresh_passout=req.fresh_passout,
                target_role=req.target_role,
                skip_llm=req.skip_llm
            )
            return rec["timeline"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/readiness")
def get_readiness_score(req: ReadinessRequest):
    try:
        if req.student_id:
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id)
            return {"readiness_score": guidance["readiness_score"]}
        else:
            gaps = analyze_gaps(req.known_skills)
            score = calculate_readiness(gaps["matched"])
            return {"readiness_score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations")
def get_recommendations(req: RecommendationsRequest):
    try:
        if req.student_id:
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id, req.target_company, req.target_role, skip_llm=req.skip_llm)
            return {
                "projects": guidance["projects"],
                "resources": guidance["resources"]
            }
        else:
            rec = generate_recommendation(
                qualification="3rd Year Student",
                known_skills=req.known_skills,
                dream_company=req.target_company or "Blinkit",
                dream_sector="Quick-Commerce",
                fresh_passout=False,
                target_role=req.target_role or "Software Development Engineer (SDE)",
                skip_llm=req.skip_llm
            )
            return {
                "projects": rec["projects"],
                "resources": rec["resources"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview-plan")
def get_interview_plan(req: InterviewPlanRequest):
    try:
        company = req.dream_company or req.target_company or "Blinkit"
        sector = req.dream_sector or "Quick-Commerce"
        role = req.target_role or "Software Development Engineer (SDE)"
        if req.student_id:
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id, company, role, skip_llm=req.skip_llm)
            return {"recommended_questions": guidance["recommended_questions"]}
        else:
            rec = generate_recommendation(
                qualification="3rd Year Student",
                known_skills=req.known_skills,
                dream_company=company,
                dream_sector=sector,
                fresh_passout=False,
                target_role=role,
                skip_llm=req.skip_llm
            )
            return {"recommended_questions": rec["recommended_questions"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/career-guidance")
def get_career_guidance(req: CareerGuidanceRequest):
    try:
        res = CareerGuidanceService.generate_career_guidance(req.student_id, req.target_company, req.target_role, skip_llm=req.skip_llm)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
def chat_with_coach(req: ChatRequest):
    try:
        student_context = None
        dream_company = req.dream_company or "Blinkit"
        if req.session_id:
            conn = get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SET search_path TO career_compass_ai, public;")
                    cur.execute("""
                        SELECT s.student_id, s.name, s.branch, s.cgpa,
                               sess.target_company, sess.target_role
                        FROM analysis_sessions sess
                        JOIN students s ON sess.student_id = s.student_id
                        WHERE sess.session_id = %s LIMIT 1
                    """, (req.session_id,))
                    row = cur.fetchone()
                    if row:
                        student_id, name, branch, cgpa, sess_company, sess_role = row
                        
                        # Query missing skills from candidate_skill_gaps
                        cur.execute("""
                            SELECT sk.skill_name 
                            FROM candidate_skill_gaps csg
                            JOIN skills sk ON csg.skill_id = sk.skill_id
                            WHERE csg.student_id = %s AND csg.status = 'Missing'
                        """, (student_id,))
                        gap_rows = cur.fetchall()
                        missing_skills = [r[0] for r in gap_rows]
                        
                        student_context = {
                            "name": name,
                            "target_role": sess_role or "Software Development Engineer",
                            "branch": branch or "Computer Science",
                            "cgpa": str(cgpa or 8.0),
                            "missing_skills": missing_skills
                        }
                        if sess_company:
                            dream_company = sess_company
                    cur.close()
                    conn.close()
                except Exception as db_err:
                    if conn: conn.close()
                    print("Error loading student context for chat:", db_err)
                    
        reply = classify_and_respond(
            req.message,
            dream_company=dream_company,
            active_stage=req.stage_title or "active stage",
            student_context=student_context
        )
        return {
            "reply": reply,
            "coach": "Placement Coach"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/stats")
def dashboard_stats():

    try:
        return query_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/signals")
def analytics_signals():
    try:
        return get_hiring_signals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/transitions")
def analytics_transitions():
    try:
        return get_career_transitions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProfileOptimizeRequest(BaseModel):
    name: str
    dream_company: str = "Blinkit"
    target_role: str = "Software Development Engineer"
    project_name: str = ""
    skills: list[str] = []
    resume_text: str = ""
    skip_llm: bool = False

@router.get("/stages/{stage_id}/content")
def read_stage_content(stage_id: int):
    data = get_stage_training(stage_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Stage content for stage {stage_id} not found.")
    return data

@router.get("/stages/{stage_id}/assessment")
def read_stage_assessment(stage_id: int):
    data = get_stage_assessment(stage_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Stage assessment for stage {stage_id} not found.")
    return data

@router.post("/profile/optimize")
def optimize_profile(req: ProfileOptimizeRequest):
    company = req.dream_company or "Blinkit"
    role = req.target_role or "Software Development Engineer"
    proj = req.project_name or "High-Concurrency Order Dispatching Engine"
    
    # 1. Fetch SDE skills from database to calculate ATS Score
    conn = get_db_connection()
    db_skills = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT skill_name FROM skills;")
            db_skills = [r[0] for r in cur.fetchall()]
            cur.close()
            conn.close()
        except Exception:
            if conn: conn.close()
            
    if not db_skills:
        db_skills = ["Java", "Spring Boot", "Go", "Redis", "Kafka", "PostgreSQL", "System Design", "Docker", "Kubernetes", "AWS Basics", "TypeScript", "React"]

    # 2. Extract matched SDE skills from resume_text
    matched_skills = []
    if req.resume_text:
        text_lower = req.resume_text.lower()
        for skill in db_skills:
            if skill.lower().strip() in text_lower:
                matched_skills.append(skill)
    else:
        # Fallback to selected tags
        matched_skills = req.skills

    # 3. Calculate ATS Score based on company SDE requirements
    company_reqs = get_role_skills_requirements(company, role)
    required_company_skills = [sk for sk, prio in company_reqs.items() if prio in ("High", "Medium")]
    if not required_company_skills:
        required_company_skills = ["Java", "SQL", "Git", "Data Structures", "Algorithms", "Spring Boot"]
        
    matched_required = [sk for sk in required_company_skills if any(sk.lower().strip() in ms.lower().strip() for ms in matched_skills)]
    
    match_rate = len(matched_required) / len(required_company_skills) if required_company_skills else 0.5
    ats_score = int(50 + (match_rate * 45))
    ats_score = min(max(ats_score, 0), 100)
    
    missing_required = [sk for sk in required_company_skills if sk not in matched_required]

    # Check if Gemini key is set and we can call it
    is_offline = req.skip_llm
    
    # Dynamically load env keys to catch any runtime changes in .env
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except Exception:
            pass

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        is_offline = True

    if is_offline:
        # Build smart custom offline bullets using user's SDE keywords
        bullets = []
        user_skills = matched_skills[:4] if matched_skills else ["Go", "Redis", "Kafka", "PostgreSQL"]
        if len(user_skills) < 4:
            user_skills.extend(["Git", "System Design", "REST APIs", "DSA"][:4 - len(user_skills)])
            
        bullets.append(f"Engineered and deployed a highly scalable {proj} backend using {user_skills[0]}, handling transaction workloads with low-latency execution.")
        bullets.append(f"Implemented asynchronous communications and event streaming channels using {user_skills[1]} to reduce system queuing latency by 30%.")
        bullets.append(f"Optimized relational schemas and cache query patterns utilizing {user_skills[2]}, reducing index lookups and cut-off load by 40%.")
        bullets.append(f"Utilized {user_skills[3]} and SDE design principles to construct comprehensive verification test coverage for backend microservices.")

        return {
            "source": "Simulated/Offline AI Optimization",
            "name": req.name,
            "dream_company": company,
            "target_role": role,
            "project_name": proj,
            "resume_bullets": bullets,
            "linkedin_summary": f"Experienced software developer targeting SDE roles at {company}. Experienced in building high-concurrency systems, optimizing database queries, and utilizing modern backend technologies like {', '.join(user_skills[:3])}.\n\nMy focus is on writing clean, maintainable code, implementing SDE scaling practices, and closing critical technical gaps. Let's connect!",
            "github_readme": f"# {proj}\n\nA high-performance backend application designed for {company}.\n\n## Tech Stack\n- Language: {user_skills[0]}\n- Data Storage: {user_skills[2]}\n- Messaging/Caching: {user_skills[1]}\n\n## Key Features\n- High throughput design matching target company requirements\n- Concurrent connection management\n- Comprehensive verification test suite",
            "ats_score": ats_score,
            "matched_keywords": matched_required,
            "missing_keywords": missing_required[:5]
        }

    try:
        import google.generativeai as genai
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="google-generativeai SDK is not installed on the backend server."
        )

    prompt = (
        "You are an expert SDE Placement Coach and Technical Career Optimization Engine.\n"
        "Your task is to generate and optimize three technical profile components based on these candidate details:\n"
        f"- Candidate Name: {req.name}\n"
        f"- Target Company: {company}\n"
        f"- Target SDE Role: {role}\n"
        f"- Active SDE Project: {proj}\n"
        f"- Key Tech Skills: {matched_skills}\n"
        f"- Current Resume Content: {req.resume_text or 'Not provided'}\n\n"
        "Generate these exact components:\n"
        "1. resume_bullets: Exactly 4 professional, action-oriented, and quantitative SDE resume bullet points about the project. Integrate the skills and optimize the project bullet points from their current resume text if provided. Highlight SDE impact (e.g. latency, scale, performance metrics).\n"
        "2. linkedin_summary: A professional, first-person summary (2-3 paragraphs, around 150 words) for a LinkedIn profile. Show passion, technical depth, and target company/role alignment.\n"
        "3. github_readme: A clean, complete, professional markdown README file for the project. Include project name as title, brief overview, tech stack list, list of key features, architecture overview, and getting started guide.\n\n"
        "You MUST return the output strictly as a JSON object with these exact keys: 'resume_bullets' (list of 4 strings), 'linkedin_summary' (string), and 'github_readme' (markdown string).\n"
        "Return ONLY the raw JSON block. Do not include markdown code block formatting (like ```json or ```)."
    )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        resp_text = response.text.strip()
        
        # Clean markdown code blocks if present
        if resp_text.startswith("```"):
            lines = resp_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            resp_text = "\n".join(lines).strip()
            
        import json
        data = json.loads(resp_text)
        
        return {
            "source": "Google Gemini (Real-Time AI)",
            "name": req.name,
            "dream_company": company,
            "target_role": role,
            "project_name": proj,
            "resume_bullets": data.get("resume_bullets", []),
            "linkedin_summary": data.get("linkedin_summary", ""),
            "github_readme": data.get("github_readme", ""),
            "ats_score": ats_score,
            "matched_keywords": matched_required,
            "missing_keywords": missing_required[:5]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google Gemini generation failed: {str(e)}"
        )


@router.get("/companies/{company_name}/job-description")
def get_company_jd(company_name: str, role_name: str = "Software Development Engineer"):
    data = get_company_job_description(company_name, role_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Job description for {company_name} and role {role_name} not found.")
    return data


@router.get("/companies/{company_name}/interview-experiences")
def get_company_experiences(company_name: str):
    data = get_company_interview_experiences(company_name)
    return data


@router.get("/skills/roadmap")
def get_skill_roadmap(skill_name: str):
    data = get_skill_roadmap_details(skill_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Skill roadmap for {skill_name} not found.")
    return data


class OutcomeFeedbackRequest(BaseModel):
    feedback_notes: str


@router.get("/student/{student_id}/outcome")
def get_student_placement_outcome(student_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        
        # Check if outcome already exists
        cur.execute("""
            SELECT o.outcome_id, o.package_lpa, o.placement_status, o.prediction_accuracy_score, o.feedback_notes, c.company_name, r.role_name
            FROM student_outcomes o
            LEFT JOIN companies c ON o.placed_company_id = c.company_id
            LEFT JOIN roles r ON o.placed_role_id = r.role_id
            WHERE o.student_id = %s
            LIMIT 1
        """, (student_id,))
        row = cur.fetchone()
        
        if row:
            outcome_id, package_lpa, placement_status, accuracy, feedback, company_name, role_name = row
            cur.close()
            conn.close()
            return {
                "outcome_id": outcome_id,
                "placed_company": company_name,
                "placed_role": role_name,
                "package_lpa": package_lpa,
                "placement_status": placement_status,
                "prediction_accuracy_score": accuracy,
                "feedback_notes": feedback,
                "startup_scalability_score": min(100.0, accuracy * 115)
            }
            
        # If not, generate a prediction based on student info
        cur.execute("""
            SELECT s.name, s.cgpa, s.target_company_role_id, c.company_id, c.company_name, r.role_id, r.role_name, c.company_type
            FROM students s
            LEFT JOIN company_roles cr ON s.target_company_role_id = cr.company_role_id
            LEFT JOIN companies c ON cr.company_id = c.company_id
            LEFT JOIN roles r ON cr.role_id = r.role_id
            WHERE s.student_id = %s
            LIMIT 1
        """, (student_id,))
        s_row = cur.fetchone()
        if not s_row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Student not found.")
            
        name, cgpa, target_cr_id, company_id, company_name, role_id, role_name, company_type = s_row
        
        cgpa_val = cgpa or 8.0
        accuracy = min(0.98, max(0.60, (cgpa_val / 10.0) + 0.15))
        
        if company_name and company_name.lower() in ['google', 'microsoft', 'meta']:
            package_lpa = round(22.0 + (cgpa_val - 7) * 4.0, 1)
        elif company_type and 'startup' in company_type.lower():
            package_lpa = round(12.0 + (cgpa_val - 7) * 2.5, 1)
        else:
            package_lpa = round(8.0 + (cgpa_val - 7) * 2.0, 1)
            
        package_lpa = max(5.0, min(50.0, package_lpa))
        
        p_company_id = company_id or 1
        p_role_id = role_id or 99
        p_company_name = company_name or "Blinkit"
        p_role_name = role_name or "Software Development Engineer"
        
        cur.execute("""
            INSERT INTO student_outcomes (student_id, placed_company_id, placed_role_id, package_lpa, placement_status, prediction_accuracy_score, feedback_notes)
            VALUES (%s, %s, %s, %s, 'Forecasted', %s, 'Forecasted based on SDE roadmap progression.')
            RETURNING outcome_id
        """, (student_id, p_company_id, p_role_id, package_lpa, accuracy))
        
        outcome_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "outcome_id": outcome_id,
            "placed_company": p_company_name,
            "placed_role": p_role_name,
            "package_lpa": package_lpa,
            "placement_status": "Forecasted",
            "prediction_accuracy_score": accuracy,
            "feedback_notes": "Forecasted based on SDE roadmap progression.",
            "startup_scalability_score": min(100.0, accuracy * 115)
        }
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/student/{student_id}/outcome/feedback")
def update_outcome_feedback(student_id: int, req: OutcomeFeedbackRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("""
            UPDATE student_outcomes
            SET feedback_notes = %s
            WHERE student_id = %s
        """, (req.feedback_notes, student_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True}
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))


class InterviewChatRequest(BaseModel):
    session_id: str
    jd_id: int
    message: str


@router.get("/job-descriptions")
def get_all_job_descriptions():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("""
            SELECT jd.jd_id, c.company_name, r.role_name, jd.experience_required_years, jd.salary_range, jd.description, jd.responsibilities, jd.requirements
            FROM job_descriptions jd
            JOIN companies c ON jd.company_id = c.company_id
            JOIN roles r ON jd.role_id = r.role_id
            ORDER BY jd.jd_id;
        """)
        rows = cur.fetchall()
        jds = []
        for row in rows:
            import json
            resp = row[6]
            if isinstance(resp, str):
                try: resp = json.loads(resp)
                except Exception: resp = [resp]
            elif not resp:
                resp = []
                
            reqs = row[7]
            if isinstance(reqs, str):
                try: reqs = json.loads(reqs)
                except Exception: reqs = [reqs]
            elif not reqs:
                reqs = []

            jds.append({
                "jd_id": row[0],
                "company_name": row[1],
                "role_name": row[2],
                "experience_required_years": row[3],
                "salary_range": row[4],
                "description": row[5],
                "responsibilities": resp,
                "requirements": reqs
            })
        cur.close()
        conn.close()
        return jds
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/interview")
def chat_mock_interview(req: InterviewChatRequest):
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except Exception:
            pass

    api_key = os.environ.get("GEMINI_API_KEY")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("""
            SELECT c.company_name, r.role_name, jd.experience_required_years, jd.salary_range, jd.description, jd.responsibilities, jd.requirements
            FROM job_descriptions jd
            JOIN companies c ON jd.company_id = c.company_id
            JOIN roles r ON jd.role_id = r.role_id
            WHERE jd.jd_id = %s LIMIT 1;
        """, (req.jd_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Job description not found.")
            
        company_name, role_name, exp, salary, desc, resp, reqs = row
        cur.close()
        conn.close()
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    import json
    if isinstance(resp, str):
        try: resp = json.loads(resp)
        except Exception: resp = [resp]
    if isinstance(reqs, str):
        try: reqs = json.loads(reqs)
        except Exception: reqs = [reqs]

    jd_context = (
        f"Job Title: {role_name} at {company_name}\n"
        f"Required Experience: {exp} years\n"
        f"Salary Range: {salary}\n"
        f"Job Overview: {desc}\n"
        f"Core Responsibilities: {', '.join(resp) if resp else 'None'}\n"
        f"Core Requirements: {', '.join(reqs) if reqs else 'None'}\n"
    )

    msg = req.message.strip()
    if not msg or msg.lower() == "/start":
        start_message = (
            f"Hello and welcome to your simulated SDE mock interview session for the **{role_name}** position at **{company_name}**!\n\n"
            f"I have loaded the specific job description requirements:\n"
            f"- **Focus Tech**: {', '.join(reqs[:4]) if reqs else 'Core SDE Skills'}\n"
            f"- **Experience Bracket**: {exp} years\n\n"
            f"Let's begin! Please introduce yourself, summarize your relevant programming/project experience, and mention any of these SDE skills you are comfortable with."
        )
        return {"reply": start_message, "mode": "interview_started"}

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            system_instruction = (
                "You are an SDE Technical Interviewer for a mock interview simulation.\n"
                "Your task is to conduct an interactive, professional SDE technical interview for the job description provided.\n"
                "You should ask one technical or behavioral question at a time. Do NOT list all questions at once.\n"
                "Review the candidate's last answer, provide very brief, constructive feedback on their answer (e.g. correctness, optimization suggestions), and then ask the next relevant question (e.g. system design choice, concurrency question, database normalization topic, or behavioral question).\n"
                "Keep your response concise (3-4 sentences maximum). Be a professional and slightly challenging interviewer."
            )
            
            prompt = (
                f"{system_instruction}\n\n"
                f"Job Description Context:\n{jd_context}\n\n"
                f"Candidate Response: {msg}\n"
                f"Interviewer Response:"
            )
            
            response = model.generate_content(prompt)
            if response and response.text:
                return {"reply": response.text.strip(), "mode": "interview_ongoing"}
        except Exception as e:
            print(f"Gemini mock interview failed: {e}. Falling back to offline interviewer logic.")

    lowered_msg = msg.lower()
    fallback_questions = [
        "Can you explain the difference between a load balancer and reverse proxy, and how you would design rate-limiting for this role?",
        "If our transaction volume spikes by 10x during flash-sales, how would you design database indexing (B-Tree vs GIN/Hash index) and cache eviction policies?",
        "How would you ensure absolute message ordering in a distributed queue system like Apache Kafka when using multiple partitions?",
        "Describe a challenging bug you encountered in a recent project. What steps did you take to isolate, debug, and patch it under time constraints?",
        "Thank you! That completes our simulated mock interview session. Your responses demonstrate solid baseline alignment with our core requirements. Keep refining low-latency design patterns!"
    ]
    
    question_idx = (len(lowered_msg) + len(msg.split())) % len(fallback_questions)
    reply = (
        f"[Offline Interviewer Fallback] Thank you for that response. Let's move to the next topic:\n\n"
        f"{fallback_questions[question_idx]}"
    )
    
    return {"reply": reply, "mode": "interview_ongoing"}


