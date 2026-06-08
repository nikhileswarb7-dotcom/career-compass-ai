# LinkedIn Profile Parser - CareerCompass AI

import re
import os
import csv
import psycopg2

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
    experiences, headlines, current roles, and raw skills for SDE mapping.
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
    def parse_profile(url_or_text: str) -> dict:
        if not url_or_text:
            return {}
            
        is_url = url_or_text.strip().startswith("http") or "linkedin.com" in url_or_text
        handle = LinkedInParser.extract_handle(url_or_text) if is_url else ""
        
        # 1. Try PostgreSQL lookup
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SET search_path TO career_compass_ai, public;")
                cur.execute("SELECT profile_id, name, current_company, linkedin_url FROM employee_profiles")
                rows = cur.fetchall()
                
                matched_row = None
                if handle:
                    for r in rows:
                        r_handle = LinkedInParser.extract_handle(r[3])
                        if r_handle and (r_handle in handle or handle in r_handle):
                            matched_row = r
                            break
                            
                if matched_row:
                    profile_id, name, company, li_url = matched_row
                    cur.execute("""
                        SELECT s.skill_name 
                        FROM employee_skills es
                        JOIN skills s ON es.skill_id = s.skill_id
                        WHERE es.profile_id = %s
                    """, (profile_id,))
                    skills = [row[0] for row in cur.fetchall()]
                    
                    cur.close()
                    conn.close()
                    
                    return {
                        "name": name,
                        "headline": f"Software Engineer at {company}" if company else "Software Engineer",
                        "current_company": company,
                        "summary": f"SDE profile matching LinkedIn profile in database.",
                        "experience": [
                            {
                                "role": "Software Engineer",
                                "company": company,
                                "duration": "N/A",
                                "description": f"Real employee profile from database."
                            }
                        ],
                        "skills_raw": skills,
                        "source": "LinkedIn Database Match"
                    }
                cur.close()
                conn.close()
            except Exception as e:
                if conn: conn.close()
                print(f"Error querying LinkedIn profile in database: {e}")

        # 2. Try CSV Fallback lookup
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            profiles_csv = os.path.join(base_dir, "database", "industry_layer", "employee_profiles.csv")
            skills_csv = os.path.join(base_dir, "database", "industry_layer", "employee_skills.csv")
            skills_master_csv = os.path.join(base_dir, "database", "industry_layer", "skills_master.csv")
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
                                    
                    return {
                        "name": name,
                        "headline": f"Software Engineer at {company}" if company else "Software Engineer",
                        "current_company": company,
                        "summary": f"SDE profile matching LinkedIn profile in local CSV.",
                        "experience": [
                            {
                                "role": "Software Engineer",
                                "company": company,
                                "duration": "N/A",
                                "description": f"Real employee profile from CSV."
                            }
                        ],
                        "skills_raw": skills,
                        "source": "LinkedIn CSV Match"
                    }
        except Exception as e:
            print(f"Error in LinkedIn CSV fallback: {e}")

        # 3. Parse from raw text or match words
        text = url_or_text
        name = handle.replace("-", " ").title() if handle else "SDE Candidate"
        headline = "Software Development Engineer"
        skills_raw = []
        
        potential_skills = ["java", "spring boot", "go", "golang", "kafka", "redis", "postgresql", "mysql", "docker", "kubernetes", "aws", "python", "system design", "dsa", "c++", "react", "typescript", "nodejs", "django"]
        for word in potential_skills:
            if re.search(r'\b' + re.escape(word) + r'\b', text.lower()) or (handle and word in handle.lower()):
                skills_raw.append(word.title())
                
        return {
            "name": name,
            "headline": headline,
            "current_company": None,
            "summary": text[:200] + "..." if len(text) > 200 else text,
            "experience": [],
            "skills_raw": skills_raw,
            "source": "LinkedIn Parsed Data"
        }
