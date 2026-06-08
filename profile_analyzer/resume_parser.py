# Resume Parser - CareerCompass AI

import re
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

class ResumeParser:
    """
    Parses resume text transcripts to extract name, education,
    experiences, projects list, and raw skill lists for mapping.
    """
    
    @staticmethod
    def get_all_db_skills() -> list:
        fallback_skills = [
            "C Programming", "C++", "Java", "Python", "SQL", "Data Structures", 
            "Algorithms", "DSA (Combined)", "DBMS", "Operating Systems", "Computer Networks", 
            "Object Oriented Programming", "Spring Boot", "REST APIs", "Microservices", 
            "Message Queues (Kafka)", "MySQL", "PostgreSQL", "Redis", "Git & GitHub", 
            "Docker", "AWS Basics", "Linux Basics", "Low Level Design", "High Level Design", 
            "System Design", "Go", "Kubernetes"
        ]
        conn = get_db_connection()
        if not conn:
            return fallback_skills
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT skill_name FROM skills")
            skills = [r[0] for r in cur.fetchall()]
            cur.close()
            conn.close()
            return skills if skills else fallback_skills
        except Exception as e:
            print("Error loading skills from database in ResumeParser:", e)
            if conn: conn.close()
            return fallback_skills

    @staticmethod
    def match_skill_in_text(skill_name: str, text: str) -> bool:
        escaped = re.escape(skill_name)
        if re.search(r'\W$', skill_name):
            pattern = r'\b' + escaped
        elif re.search(r'^\W', skill_name):
            pattern = escaped + r'\b'
        else:
            pattern = r'\b' + escaped + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))

    @staticmethod
    def parse_resume(text: str) -> dict:
        if not text:
            return {}
            
        # Standard cleaning
        text_clean = re.sub(r'\s+', ' ', text)
        
        # Name detection
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
                
        # Experience section extraction
        experience_section = ""
        exp_match = re.search(r'(?:experience|employment|work history)(.*?)(?:education|projects|skills|certificates|certifications|$)', text, re.IGNORECASE)
        if exp_match:
            experience_section = exp_match.group(1).strip()
            
        # Projects section extraction
        projects_section = ""
        proj_match = re.search(r'(?:projects|personal projects|academic projects)(.*?)(?:education|experience|skills|certificates|certifications|$)', text, re.IGNORECASE)
        if proj_match:
            projects_section = proj_match.group(1).strip()
            
        # Skills section extraction
        skills_section = ""
        skills_match = re.search(r'(?:skills|technical skills|key skills|expertise)(.*?)(?:education|experience|projects|certificates|certifications|$)', text, re.IGNORECASE)
        if skills_match:
            skills_section = skills_match.group(1).strip()
            
        # Education extraction
        education = "B.Tech Computer Science"
        cgpa = 8.0
        
        cgpa_match = re.search(r'\b(cgpa|gpa|pointer)\s*[:\-]?\s*([0-9\.]+)\b', text, re.IGNORECASE)
        if cgpa_match:
            try:
                cgpa = float(cgpa_match.group(2))
            except ValueError:
                pass
                
        if "mtech" in text.lower() or "m.tech" in text.lower():
            education = "M.Tech Computer Science"
        elif "mca" in text.lower():
            education = "MCA Master of Computer Applications"
        elif "bca" in text.lower():
            education = "BCA Bachelor of Computer Applications"
            
        # Load skills from DB dynamically
        db_skills = ResumeParser.get_all_db_skills()
        skills_raw = []
        
        # 1. Direct Skill Mentions Check
        search_space = text
        for skill in db_skills:
            if ResumeParser.match_skill_in_text(skill, search_space):
                skills_raw.append(skill)
                
        # 2. Tech Inference Rules
        inference_rules = {
            r'\b(kafka|apache kafka|rabbitmq|message queue[s]?)\b': [
                "Message Queues (Kafka)", 
                "Microservices"
            ],
            r'\b(spring boot|springboot|spring)\b': [
                "Spring Boot", 
                "Java", 
                "REST APIs", 
                "Microservices"
            ],
            r'\b(rest|rest api[s]?|restful)\b': [
                "REST APIs"
            ],
            r'\b(microservice[s]?)\b': [
                "Microservices", 
                "REST APIs"
            ],
            r'\b(docker|container[s]?)\b': [
                "Docker"
            ],
            r'\b(kubernetes|k8s)\b': [
                "Kubernetes", 
                "Docker"
            ],
            r'\b(aws|amazon web services|s3|ec2)\b': [
                "AWS Basics"
            ],
            r'\b(linux|unix|bash|shell)\b': [
                "Linux Basics"
            ],
            r'\b(mysql)\b': [
                "MySQL",
                "SQL",
                "DBMS"
            ],
            r'\b(postgresql|postgres)\b': [
                "PostgreSQL",
                "SQL",
                "DBMS"
            ],
            r'\b(sql)\b': [
                "SQL",
                "DBMS"
            ],
            r'\b(system design|distributed system[s]?|hld|high level design)\b': [
                "System Design",
                "High Level Design"
            ],
            r'\b(lld|low level design|design patterns?)\b': [
                "Low Level Design",
                "Object Oriented Programming"
            ],
            r'\b(oop[s]?|object oriented)\b': [
                "Object Oriented Programming"
            ],
            r'\b(dsa|data structures?|algorithms?|leetcode)\b': [
                "DSA (Combined)",
                "Data Structures",
                "Algorithms"
            ],
            r'\b(git|github)\b': [
                "Git & GitHub"
            ]
        }
        
        for pattern, inferred_skills in inference_rules.items():
            if re.search(pattern, search_space, re.IGNORECASE):
                for inf_skill in inferred_skills:
                    if inf_skill in db_skills:
                        skills_raw.append(inf_skill)
                        
        return {
            "name": name,
            "email": email,
            "education": education,
            "cgpa": cgpa,
            "experience_extracted": experience_section[:400] + "..." if len(experience_section) > 400 else experience_section,
            "projects_extracted": projects_section[:400] + "..." if len(projects_section) > 400 else projects_section,
            "skills_raw": sorted(list(set(skills_raw))),
            "source": "Resume Parser"
        }
