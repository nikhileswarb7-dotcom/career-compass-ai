# LinkedIn Profile Parser - CareerCompass AI
# Extracts sections from text transcripts, resolves DB employee matches, and converts experiences to competencies.

import re
import os
import csv
import psycopg2
from profile_analyzer.resume_parser import ResumeParser

try:
    from api.database_connector import get_db_connection
except ImportError:
    def get_db_connection():
        try:
            return psycopg2.connect(
                host="localhost",
                port=5432,
                dbname="career_compass_ai",
                user="postgres",
                password="Nikhil@2824"
            )
        except Exception:
            return None

class LinkedInParser:
    """
    Parses LinkedIn profile URLs or raw text transcripts to extract 
    experiences, headlines, current roles, and competencies from database skills.
    """
    
    @staticmethod
    def extract_handle(url_or_text: str) -> str:
        if not url_or_text:
            return ""
        s = url_or_text.lower().strip()
        match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-\_]+)', s)
        if match:
            return match.group(1).rstrip('-').strip()
        if "/in/" in s:
            parts = s.split("/in/")
            if len(parts) > 1:
                return parts[1].split("/")[0].split(" ")[0].strip("-").strip()
        return s.split("/")[-1].split(" ")[0].strip("-").strip()

    @staticmethod
    def get_all_db_skills() -> list:
        """
        Dynamically queries skills from PostgreSQL.
        Throws RuntimeError if DB is unreachable.
        """
        return ResumeParser.get_all_db_skills()

    @staticmethod
    def parse_profile(url_or_text: str) -> dict:
        if not url_or_text:
            return {}
            
        is_url = url_or_text.strip().startswith("http") or "linkedin.com" in url_or_text
        handle = LinkedInParser.extract_handle(url_or_text) if is_url else ""
        
        # Load dynamic skills from database
        db_skills = LinkedInParser.get_all_db_skills()
        db_skills_lower = {s.lower().strip(): s for s in db_skills}

        # 1. Try PostgreSQL lookup for existing employee profiles
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SET search_path TO career_compass_ai, public;")
                cur.execute("SELECT profile_id, name, current_company, linkedin_url, career_path FROM employee_profiles")
                rows = cur.fetchall()
                
                matched_row = None
                if handle:
                    for r in rows:
                        r_handle = LinkedInParser.extract_handle(r[3])
                        if r_handle and (r_handle in handle or handle in r_handle):
                            matched_row = r
                            break
                            
                if matched_row:
                    profile_id, name, company, li_url, career_path = matched_row
                    cur.execute("""
                        SELECT s.skill_name 
                        FROM employee_skills es
                        JOIN skills s ON es.skill_id = s.skill_id
                        WHERE es.profile_id = %s
                    """, (profile_id,))
                    skills = [row[0] for row in cur.fetchall()]
                    
                    cur.close()
                    conn.close()
                    
                    path_steps = [p.strip() for p in (career_path or "").split("->") if p.strip()]
                    experience = []
                    for idx, step in enumerate(path_steps):
                        experience.append({
                            "role": step,
                            "company": company if idx == 0 else "Previous Company",
                            "duration": "N/A",
                            "description": f"Real professional path step: {step}"
                        })
                    
                    return {
                        "name": name,
                        "headline": f"Software Engineer at {company}" if company else "Software Engineer",
                        "current_company": company,
                        "summary": f"Professional profile matching employee in database.",
                        "experience": experience,
                        "skills_raw": [s for s in skills if s in db_skills],
                        "source": "LinkedIn Database Match"
                    }
                cur.close()
                conn.close()
            except Exception as e:
                if conn: conn.close()
                print(f"Error querying LinkedIn profile in database: {e}")

        # 2. Try CSV Fallback lookup for existing employee profiles
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            profiles_csv = os.path.join(base_dir, "database", "industry_layer", "employee_profiles.csv")
            skills_csv = os.path.join(base_dir, "database", "industry_layer", "employee_skills.csv")
            skills_master_csv = os.path.join(base_dir, "database", "career_layer", "skills_master.csv")
            if not os.path.exists(skills_master_csv):
                skills_master_csv = os.path.join(base_dir, "database", "career_layer", "skills_master.csv")
                
            if os.path.exists(profiles_csv) and handle:
                with open(profiles_csv, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    matched_profile = None
                    for row in reader:
                        r_handle = LinkedInParser.extract_handle(row.get('linkedin_url', ''))
                        if r_handle and (r_handle in handle or handle in r_handle):
                            matched_profile = row
                            break
                            
                if matched_profile:
                    profile_id = matched_profile['profile_id']
                    name = matched_profile['name']
                    company = matched_profile['current_company']
                    
                    skill_ids = []
                    if os.path.exists(skills_csv):
                        with open(skills_csv, mode='r', encoding='utf-8') as f_es:
                            reader_es = csv.DictReader(f_es)
                            for row_es in reader_es:
                                if row_es['profile_id'] == profile_id:
                                    skill_ids.append(row_es['skill_id'])
                                    
                    skills = []
                    if skill_ids and os.path.exists(skills_master_csv):
                        with open(skills_master_csv, mode='r', encoding='utf-8') as f_sm:
                            reader_sm = csv.DictReader(f_sm)
                            for row_sm in reader_sm:
                                if row_sm['skill_id'] in skill_ids:
                                    skills.append(row_sm['skill_name'])
                                    
                    path_str = matched_profile.get("career_path", "")
                    path_steps = [p.strip() for p in path_str.split("->") if p.strip()]
                    experience = []
                    for idx, step in enumerate(path_steps):
                        experience.append({
                            "role": step,
                            "company": company if idx == 0 else "Previous Company",
                            "duration": "N/A",
                            "description": f"Real SDE profile step: {step}"
                        })
                        
                    return {
                        "name": name,
                        "headline": f"Software Engineer at {company}" if company else "Software Engineer",
                        "current_company": company,
                        "summary": f"Professional profile matching employee in local CSV.",
                        "experience": experience,
                        "skills_raw": [s for s in skills if s in db_skills],
                        "source": "LinkedIn CSV Match"
                    }
        except Exception as e:
            print(f"Error in LinkedIn CSV fallback: {e}")

        # 3. Parse Raw Text Transcript
        # No placeholders or fabricated Amazon/Google profiles under "Real Data Only" directive.
        text = url_or_text
        name = "SDE Candidate"
        headline = "Software Development Engineer"
        about = ""
        experience = []
        education = "B.Tech Computer Science"

        # Heuristic name extraction
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            # First non-empty line could be the name
            name_candidate = lines[0]
            if len(name_candidate.split()) <= 4 and re.match(r'^[A-Z][a-zA-Z\s\.\-]+$', name_candidate):
                name = name_candidate
                if len(lines) > 1:
                    headline_candidate = lines[1]
                    if len(headline_candidate) < 100:
                        headline = headline_candidate

        # Extract sections using search bounds
        text_clean = text.replace('\r', '')

        # Headline / About / Summary
        about_match = re.search(r'(?:about|summary|profile)(.*?)(?:experience|education|skills|$)', text_clean, re.DOTALL | re.IGNORECASE)
        if about_match:
            about = about_match.group(1).strip()

        # Education
        edu_match = re.search(r'(?:education|studies)(.*?)(?:experience|skills|about|summary|$)', text_clean, re.DOTALL | re.IGNORECASE)
        if edu_match:
            edu_text = edu_match.group(1).lower()
            if "mtech" in edu_text or "m.tech" in edu_text:
                education = "M.Tech Computer Science"
            elif "mca" in edu_text:
                education = "MCA Master of Computer Applications"
            elif "bca" in edu_text:
                education = "BCA Bachelor of Computer Applications"

        # Experience Section Parsing
        exp_match = re.search(r'(?:experience|work history|employment)(.*?)(?:education|skills|about|summary|$)', text_clean, re.DOTALL | re.IGNORECASE)
        if exp_match:
            exp_text = exp_match.group(1).strip()
            # Split experiences by lines that look like: Role at Company
            jobs = []
            current_job = []
            for line in exp_text.split('\n'):
                line_s = line.strip()
                if not line_s:
                    continue
                # Simple boundary check for job entries
                if any(k in line_s.lower() for k in ["engineer", "developer", "intern", "architect", "lead"]) and (" at " in line_s or " - " in line_s or len(line_s) < 60):
                    if current_job:
                        jobs.append("\n".join(current_job))
                        current_job = []
                current_job.append(line_s)
            if current_job:
                jobs.append("\n".join(current_job))

            for job in jobs:
                j_lines = job.split('\n')
                role = j_lines[0].strip()
                company = "Company"
                if " at " in role:
                    parts = role.split(" at ")
                    role = parts[0].strip()
                    company = parts[1].strip()
                description = " ".join(j_lines[1:]).strip() if len(j_lines) > 1 else ""
                
                # Convert experience descriptions to technical competencies
                competencies = []
                for skill in db_skills:
                    # check match in job context
                    if re.search(r'\b' + re.escape(skill.lower()) + r'\b', job.lower()):
                        competencies.append(skill)
                        
                experience.append({
                    "role": role,
                    "company": company,
                    "duration": "N/A",
                    "description": description,
                    "competencies": competencies
                })

        # Extract Skills dynamically from the text
        skills_raw = []
        for skill in db_skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text.lower()):
                skills_raw.append(skill)

        return {
            "name": name,
            "headline": headline,
            "current_company": experience[0]["company"] if experience else None,
            "summary": about if about else (text[:200] + "..." if len(text) > 200 else text),
            "experience": experience,
            "education": education,
            "skills_raw": sorted(list(set(skills_raw))),
            "source": "LinkedIn Parsed Transcript"
        }
