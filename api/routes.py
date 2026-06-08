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
from services.career_guidance_service import CareerGuidanceService
from profile_analyzer.linkedin_parser import LinkedInParser
from profile_analyzer.github_analyzer import GitHubAnalyzer
from profile_analyzer.resume_parser import ResumeParser
from profile_analyzer.skill_extractor import SkillExtractor

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
    target_role: str = "Junior Software Engineer"

class ChatRequest(BaseModel):
    message: str
    stage_title: str = ""
    dream_company: str = ""
    dream_sector: str = ""
    qualification: str = ""

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
    target_role: str = "Junior Software Engineer"

class RecommendRequest(BaseModel):
    name: str = "SDE Candidate"
    qualification: str = "3rd Year Student"
    branch: str = "Computer Science"
    cgpa: float = 8.0
    dream_company: str = "Blinkit"
    dream_sector: str = "Quick-Commerce"
    fresh_passout: bool = False
    target_role: str = "Junior Software Engineer"
    known_skills: list[str] = []
    linkedin_url: str = ""
    github_username: str = ""
    resume_text: str = ""
    text_input: str = ""
    student_id: int = None
    session_id: str = None

class UpdateProgressRequest(BaseModel):
    status: str


class RoadmapRequest(BaseModel):
    student_id: str = ""
    qualification: str = ""
    known_skills: list[str] = []
    dream_company: str = "Blinkit"
    dream_sector: str = "Quick-Commerce"
    fresh_passout: bool = False
    target_role: str = "Junior Software Engineer"

class ReadinessRequest(BaseModel):
    student_id: str = ""
    known_skills: list[str] = []

class InterviewPlanRequest(BaseModel):
    student_id: str = ""
    target_company: str = ""
    dream_company: str = ""
    dream_sector: str = ""
    known_skills: list[str] = []

class RecommendationsRequest(BaseModel):
    student_id: str = ""
    target_company: str = "Blinkit"
    target_role: str = "Junior Software Engineer"
    known_skills: list[str] = []

class CareerGuidanceRequest(BaseModel):
    student_id: str
    target_company: str = "Blinkit"
    target_role: str = "Junior Software Engineer"

@router.post("/assess")
def assess_student(req: AssessmentRequest):
    try:
        plan = generate_recommendation(
            req.qualification, 
            req.known_skills,
            dream_company=req.dream_company,
            dream_sector=req.dream_sector,
            fresh_passout=req.fresh_passout,
            target_role=req.target_role
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
                parsed_li = LinkedInParser.parse_profile(req.linkedin_url)
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
            
        # Collect sources and details for each skill
        skill_metadata = {} # skill_name -> {"sources": set(), "github_frequency": 0}
        
        # 1. Manual User Selection
        for s in req.known_skills:
            if s:
                if s not in skill_metadata:
                    skill_metadata[s] = {"sources": set(), "github_frequency": 0}
                skill_metadata[s]["sources"].add("Manual")
                
        # 2. LinkedIn Parser
        if req.linkedin_url and parsed_li and "error" not in parsed_li:
            for s in parsed_li.get("skills_raw", []):
                if s:
                    if s not in skill_metadata:
                        skill_metadata[s] = {"sources": set(), "github_frequency": 0}
                    skill_metadata[s]["sources"].add("LinkedIn")
                    
        # 3. GitHub Analyzer
        if req.github_username and parsed_gh and "error" not in parsed_gh:
            freq_map = parsed_gh.get("frequency_map", {})
            for s in parsed_gh.get("skills_raw", []):
                if s:
                    if s not in skill_metadata:
                        skill_metadata[s] = {"sources": set(), "github_frequency": 0}
                    skill_metadata[s]["sources"].add("GitHub")
                    skill_metadata[s]["github_frequency"] = freq_map.get(s, 0)
                    
        # 4. Resume Parser
        if req.resume_text and parsed_res and "error" not in parsed_res:
            for s in parsed_res.get("skills_raw", []):
                if s:
                    if s not in skill_metadata:
                        skill_metadata[s] = {"sources": set(), "github_frequency": 0}
                    skill_metadata[s]["sources"].add("Resume")
                    
        # Normalize and filter skills against database master list
        db_skills = ResumeParser.get_all_db_skills()
        normalized_skill_metadata = {}
        for skill_name, meta in skill_metadata.items():
            canonical_name = None
            for db_s in db_skills:
                if db_s.lower() == skill_name.lower():
                    canonical_name = db_s
                    break
            if not canonical_name:
                # Fallback mapping from SkillExtractor if available
                canon_res = SkillExtractor.extract_and_normalize([skill_name])
                if canon_res:
                    canonical_name = canon_res[0]
                else:
                    canonical_name = skill_name.strip().title()
                
            if canonical_name not in normalized_skill_metadata:
                normalized_skill_metadata[canonical_name] = {"sources": set(), "github_frequency": 0}
            normalized_skill_metadata[canonical_name]["sources"].update(meta["sources"])
            normalized_skill_metadata[canonical_name]["github_frequency"] = max(normalized_skill_metadata[canonical_name]["github_frequency"], meta["github_frequency"])

        # Calculate confidence and format output
        unified_skills = []
        for s_name, meta in normalized_skill_metadata.items():
            sources = sorted(list(meta["sources"]))
            freq = meta["github_frequency"]
            
            # Calculate baseline score
            scores = []
            if "Manual" in sources:
                scores.append(0.85)
            if "Resume" in sources:
                scores.append(0.70)
            if "GitHub" in sources:
                scores.append(0.60)
            if "LinkedIn" in sources:
                scores.append(0.70)
                
            base_score = max(scores) if scores else 0.50
            
            # Boost for multiple sources
            source_count = len(sources)
            if source_count == 2:
                base_score += 0.10
            elif source_count >= 3:
                base_score += 0.15
                
            # Boost for GitHub frequency
            if "GitHub" in sources and freq > 0:
                base_score += min(0.20, freq * 0.05)
                
            confidence_score = min(1.0, base_score)
            
            if confidence_score >= 0.80:
                confidence = "High"
            elif confidence_score >= 0.65:
                confidence = "Medium"
            else:
                confidence = "Low"
                
            unified_skills.append({
                "name": s_name,
                "confidence": confidence,
                "confidence_score": round(confidence_score * 100),
                "sources": sources,
                "github_frequency": freq
            })
        
        # PostgreSQL registration & session creation
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
                company_role_id = row[0] if row else 1
                
                # Generate a unique email for this onboarding to ensure isolation
                import uuid
                unique_suffix = uuid.uuid4().hex[:8]
                email = f"{req.name.lower().replace(' ', '_')}_{unique_suffix}@careercompass.ai"
                cur.execute("SELECT student_id FROM students WHERE email = %s LIMIT 1", (email,))
                row = cur.fetchone()
                
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
                            resume_text = %s
                        WHERE student_id = %s
                    """, (req.name, qualification_id, req.branch, req.cgpa, company_role_id, req.linkedin_url, req.github_username, req.resume_text, student_id))
                else:
                    cur.execute("""
                        INSERT INTO students (name, email, qualification_id, branch, cgpa, target_company_role_id, linkedin_url, github_username, resume_text)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING student_id
                    """, (req.name, email, qualification_id, req.branch, req.cgpa, company_role_id, req.linkedin_url, req.github_username, req.resume_text))
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
        
        return {
            "student_id": student_id,
            "session_id": session_id,
            "linkedin_parsed": parsed_li,
            "github_parsed": parsed_gh,
            "resume_parsed": parsed_res,
            "extracted_skills": unified_skills
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
        company_role_id = row[0] if row else 1
        
        # 3. Check/Get student_id
        student_id = req.student_id
        if not student_id and req.session_id:
            cur.execute("SELECT student_id FROM analysis_sessions WHERE session_id = %s LIMIT 1", (req.session_id,))
            s_row = cur.fetchone()
            if s_row:
                student_id = int(s_row[0])
                
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
                
        # Update student profile
        cur.execute("""
            UPDATE students
            SET name = %s,
                qualification_id = %s,
                branch = %s,
                cgpa = %s,
                target_company_role_id = %s,
                linkedin_url = %s,
                github_username = %s,
                resume_text = %s
            WHERE student_id = %s
        """, (req.name, qualification_id, req.branch, req.cgpa, company_role_id, req.linkedin_url, req.github_username, req.resume_text, student_id))
            
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
            target_role=req.target_role
        )
        res["student_id"] = student_id
        res["session_id"] = session_id
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_dynamic_guidance(session_id: str) -> dict:
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
            experience_years=experience_years
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

@router.get("/readiness/{session_id}")
def get_readiness_by_session(session_id: str):
    rec = get_dynamic_guidance(session_id)
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
        "common_projects": rec.get("common_projects", [])
    }

@router.get("/recommendations/{session_id}")
def get_recommendations_by_session(session_id: str):
    rec = get_dynamic_guidance(session_id)
    return {
        "projects": rec["projects"],
        "resources": rec["resources"],
        "coach_recommendations": rec.get("coach_recommendations", [])
    }

@router.get("/interview-plan/{session_id}")
def get_interview_plan_by_session(session_id: str):
    rec = get_dynamic_guidance(session_id)
    return {
        "recommended_questions": rec["recommended_questions"]
    }

@router.get("/roadmap/{session_id}")
def get_roadmap_by_session(session_id: str):
    rec = get_dynamic_guidance(session_id)
    return rec["timeline"]

@router.post("/roadmap")
def get_roadmap_timeline(req: RoadmapRequest):
    try:
        if req.student_id:
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id, req.dream_company, req.target_role)
            return guidance["timeline"]
        else:
            gaps = analyze_gaps(req.known_skills)
            timeline = generate_timeline(
                qualification=req.qualification,
                missing_skills=gaps["missing"],
                dream_company=req.dream_company,
                dream_sector=req.dream_sector,
                fresh_passout=req.fresh_passout,
                target_role=req.target_role
            )
            return timeline
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
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id, req.target_company, req.target_role)
            return {
                "projects": guidance["projects"],
                "resources": guidance["resources"]
            }
        else:
            gaps = analyze_gaps(req.known_skills)
            timeline = generate_timeline(
                qualification="3rd Year Student",
                missing_skills=gaps["missing"],
                dream_company=req.target_company,
                dream_sector="Quick-Commerce",
                fresh_passout=False,
                target_role=req.target_role
            )
            return {
                "projects": timeline.get("projects", []),
                "resources": timeline.get("resources", [])
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview-plan")
def get_interview_plan(req: InterviewPlanRequest):
    try:
        company = req.dream_company or req.target_company or "Blinkit"
        sector = req.dream_sector or "Quick-Commerce"
        if req.student_id:
            guidance = CareerGuidanceService.generate_career_guidance(req.student_id, company)
            return {"recommended_questions": guidance["recommended_questions"]}
        else:
            gaps = analyze_gaps(req.known_skills)
            questions = recommend_questions(
                missing_skills=gaps["missing"],
                dream_company=company,
                dream_sector=sector
            )
            return {"recommended_questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/career-guidance")
def get_career_guidance(req: CareerGuidanceRequest):
    try:
        res = CareerGuidanceService.generate_career_guidance(req.student_id, req.target_company, req.target_role)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
def chat_with_coach(req: ChatRequest):
    try:
        reply = classify_and_respond(
            req.message,
            dream_company=req.dream_company or "Blinkit",
            active_stage=req.stage_title or "active stage"
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
    template = get_profile_builder_template("Software Development Engineer")
    if not template:
        raise HTTPException(status_code=404, detail="SDE Profile Optimization template not found.")
        
    company = req.dream_company or "Blinkit"
    role = req.target_role or "Software Development Engineer"
    proj = req.project_name or "High-Concurrency Order Dispatching Engine"
    
    bullets = []
    for bullet in template["resume_bullets"]:
        bullet_opt = bullet.replace("{dream_company}", company)\
                           .replace("{target_role}", role)\
                           .replace("{project_name}", proj)\
                           .replace("{name}", req.name)
        bullets.append(bullet_opt)
        
    summary = template["linkedin_summary"].replace("{dream_company}", company)\
                                         .replace("{target_role}", role)\
                                         .replace("{project_name}", proj)\
                                         .replace("{name}", req.name)
                                         
    readme = template["github_readme"].replace("{dream_company}", company)\
                                     .replace("{target_role}", role)\
                                     .replace("{project_name}", proj)\
                                     .replace("{name}", req.name)
                                     
    return {
        "source": template["source"],
        "name": req.name,
        "dream_company": company,
        "target_role": role,
        "project_name": proj,
        "resume_bullets": bullets,
        "linkedin_summary": summary,
        "github_readme": readme
    }


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

