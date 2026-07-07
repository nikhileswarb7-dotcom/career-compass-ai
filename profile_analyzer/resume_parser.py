# Resume Parser - CareerCompass AI
# Dynamically queries PostgreSQL skills, extracts projects, experience, and certifications, and applies tech inference.

import re
import psycopg2

try:
    from api.database_connector import get_db_connection
except ImportError:
    def get_db_connection():
        try:
            import os
            return psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 5432)),
                dbname=os.environ.get("DB_NAME", "career_compass_ai"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", "")
            )
        except Exception:
            return None

class ResumeParser:
    """
    Parses resume text transcripts to extract name, education,
    experiences, projects list, certifications, and dynamically mapped skills.
    """
    
    CANONICAL_SYNONYMS = {
        "c programming": ["c programming", r"\bc\b"],
        "c++": [r"c\+\+"],
        "java": ["java"],
        "python": ["python"],
        "sql": ["sql"],
        "data structures": ["data structures", "data structure"],
        "algorithms": ["algorithms"],
        "dsa (combined)": ["dsa (combined)", r"\bdsa\b"],
        "dbms": ["dbms", "database management"],
        "operating systems": ["operating systems", "operating system", r"\bos\b"],
        "computer networks": ["computer networks", "computer network", r"\bcn\b"],
        "object oriented programming": ["object oriented programming", "object oriented", r"\boop\b", r"\boops\b"],
        "spring boot": ["spring boot", "springboot", "spring"],
        "rest apis": ["rest apis", "rest api", "restful"],
        "microservices": ["microservices", "microservice"],
        "message queues (kafka)": ["message queues (kafka)", "kafka"],
        "mysql": ["mysql"],
        "postgresql": ["postgresql", "postgres"],
        "redis": ["redis"],
        "git & github": ["git & github", "git", "github"],
        "docker": ["docker"],
        "aws basics": ["aws basics", "aws"],
        "linux basics": ["linux basics", "linux"],
        "low level design": ["low level design", r"\blld\b"],
        "high level design": ["high level design", r"\bhld\b"],
        "system design": ["system design"],
        "go": ["go", "golang"],
        "kubernetes": ["kubernetes", r"\bk8s\b"]
    }
    
    @staticmethod
    def get_all_db_skills() -> list:
        """
        Dynamically queries all skills from PostgreSQL.
        Throws RuntimeError if DB is unreachable to comply with 'no fallback arrays' rule.
        """
        conn = get_db_connection()
        if not conn:
            raise RuntimeError("Database connection unavailable for dynamic skill loading.")
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT skill_name FROM skills")
            skills = [r[0] for r in cur.fetchall()]
            cur.close()
            conn.close()
            if not skills:
                raise ValueError("PostgreSQL skills table is empty.")
            return skills
        except Exception as e:
            if conn: conn.close()
            raise RuntimeError(f"Failed to query database skills: {str(e)}")

    @staticmethod
    def match_skill_in_text(skill_name: str, text: str) -> bool:
        if not skill_name or not text:
            return False
        
        name_lower = skill_name.lower().strip()
        synonyms = ResumeParser.CANONICAL_SYNONYMS.get(name_lower, [name_lower])
        
        for syn in synonyms:
            if "\\" in syn or "^" in syn or "$" in syn:
                if re.search(syn, text, re.IGNORECASE):
                    return True
            else:
                escaped = re.escape(syn)
                boundary_before = r'(?:^|[\s\.,;\(\)\[\]\{\}/\|])'
                boundary_after = r'(?:$|[\s\.,;\(\)\[\]\{\}/\|])'
                pattern = boundary_before + escaped + boundary_after
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        return False

    @staticmethod
    def parse_resume(text: str) -> dict:
        if not text:
            return {}
            
        # 1. Load dynamic skills from Database
        db_skills = ResumeParser.get_all_db_skills()
        db_skills_lower = {s.lower().strip(): s for s in db_skills}

        # 2. Extract Name & Email
        name = "SDE Candidate"
        email = None
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            email = email_match.group(0)
            
        words = text.strip().split()
        if len(words) >= 2:
            potential_name = f"{words[0]} {words[1]}"
            if re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+$', potential_name):
                name = potential_name
                
        # 3. Extract Education & CGPA
        education = "B.Tech Computer Science"
        cgpa = 8.0
        
        cgpa_match = re.search(r'\b(cgpa|gpa|pointer)\s*[:\-]?\s*([0-9\.]+)\b', text, re.IGNORECASE)
        if cgpa_match:
            try:
                cgpa = float(cgpa_match.group(2))
            except ValueError:
                pass
                
        text_lower = text.lower()
        if "mtech" in text_lower or "m.tech" in text_lower:
            education = "M.Tech Computer Science"
        elif "mca" in text_lower:
            education = "MCA Master of Computer Applications"
        elif "bca" in text_lower:
            education = "BCA Bachelor of Computer Applications"

        # 4. Extract Experience Section
        experience_section = ""
        exp_match = re.search(r'(?:experience|employment|work history)(.*?)(?:projects|education|skills|certificates|certifications|$)', text, re.DOTALL | re.IGNORECASE)
        if exp_match:
            experience_section = exp_match.group(1).strip()
            
        # 5. Extract Certifications
        certifications = []
        cert_section_match = re.search(r'(?:certificates|certifications|credentials)(.*?)(?:experience|projects|education|skills|$)', text, re.DOTALL | re.IGNORECASE)
        if cert_section_match:
            lines = cert_section_match.group(1).strip().split('\n')
            for line in lines:
                line_clean = line.strip().strip('•-*· ').strip()
                if line_clean and len(line_clean) > 5 and len(line_clean) < 100:
                    certifications.append(line_clean)
        # If no specific block, search lines matching common certified keywords
        if not certifications:
            for line in text.split('\n'):
                if any(k in line.lower() for k in ["certified", "certification", "credential"]):
                    line_clean = line.strip().strip('•-*· ').strip()
                    if line_clean and len(line_clean) > 5 and len(line_clean) < 120:
                        certifications.append(line_clean)

        # 6. Parse Project Blocks and Project Tech
        projects = []
        projects_section = ""
        proj_match = re.search(r'(?:projects|personal projects|academic projects)(.*?)(?:experience|education|skills|certificates|certifications|$)', text, re.DOTALL | re.IGNORECASE)
        if proj_match:
            projects_section = proj_match.group(1).strip()
            
        if projects_section:
            # Split by line breaks followed by typical project separators (e.g. bolded line, bullet points, numbers)
            project_blocks = []
            current_block = []
            for line in projects_section.split('\n'):
                line_strip = line.strip()
                if not line_strip:
                    continue
                # If a line looks like a title (e.g. starts with bullet or number, or short title line)
                if line_strip.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')) or (len(line_strip) < 60 and any(k in line_strip.lower() for k in ["system", "application", "app", "website", "engine", "platform", "pipeline", "tool"])):
                    if current_block:
                        project_blocks.append("\n".join(current_block))
                        current_block = []
                current_block.append(line_strip)
            if current_block:
                project_blocks.append("\n".join(current_block))

            for block in project_blocks:
                lines = block.split('\n')
                title = lines[0].strip().strip('•-*· 123456789. ')
                description = " ".join(lines[1:]).strip() if len(lines) > 1 else lines[0].strip()
                
                # Match technologies in this project block
                proj_tech = []
                for skill in db_skills:
                    if ResumeParser.match_skill_in_text(skill, block):
                        proj_tech.append(skill)
                
                if len(title) > 3 and len(title) < 100:
                    projects.append({
                        "title": title,
                        "description": description,
                        "technologies": sorted(list(set(proj_tech)))
                    })

        # 7. Extract Explicit Skills
        skills_raw = []
        for skill in db_skills:
            if ResumeParser.match_skill_in_text(skill, text):
                skills_raw.append(skill)

        # 8. Technology Inference Rules
        # Associative rules mapping keywords to DB skill canonical names (lowercase for safe matching)
        inference_rules = {
            "spring boot": ["java", "rest apis", "microservices"],
            "springboot": ["java", "rest apis", "microservices"],
            "spring": ["java", "rest apis", "microservices"],
            "kafka": ["message queues (kafka)", "microservices", "system design"],
            "apache kafka": ["message queues (kafka)", "microservices", "system design"],
            "postgresql": ["sql", "dbms"],
            "postgres": ["sql", "dbms"],
            "mysql": ["sql", "dbms"],
            "kubernetes": ["docker"],
            "docker": ["git & github"],
            "low level design": ["object oriented programming"],
            "lld": ["object oriented programming"],
            "high level design": ["system design"],
            "hld": ["system design"],
            "system design": ["microservices"],
            "go": ["rest apis"],
            "golang": ["rest apis"],
            "microservices": ["rest apis"],
            "django": ["python"],
            "flask": ["python"]
        }

        # Apply inference
        inferred = set()
        for term, inf_list in inference_rules.items():
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                for inf_skill in inf_list:
                    # Match back to dynamic DB skills lower mapping
                    if inf_skill in db_skills_lower:
                        inferred.add(db_skills_lower[inf_skill])

        # Combine explicit and inferred skills
        final_skills = sorted(list(set(skills_raw + list(inferred))))

        return {
            "name": name,
            "email": email,
            "education": education,
            "cgpa": cgpa,
            "experience": experience_section,
            "certifications": certifications,
            "projects": projects,
            "skills_raw": final_skills,
            "source": "Resume PDF Parser"
        }
