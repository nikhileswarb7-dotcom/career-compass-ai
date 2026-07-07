# Professional Feature Builder - CareerCompass AI

import re
import pandas as pd

SKILL_NAMES = [
    "C Programming", "C++", "Java", "Python", "SQL", "Data Structures", "Algorithms", 
    "DSA (Combined)", "DBMS", "Operating Systems", "Computer Networks", "Object Oriented Programming", 
    "Spring Boot", "REST APIs", "Microservices", "Message Queues (Kafka)", "MySQL", 
    "PostgreSQL", "Redis", "Git & GitHub", "Docker", "AWS Basics", "Linux Basics", 
    "Low Level Design", "High Level Design", "System Design", "Go", "Kubernetes", 
    "JavaScript", "TypeScript", "HTML & CSS", "React", "NodeJS", "Angular", "Vue.js", 
    "Express.js", "FastAPI", "Django", "MongoDB", "DynamoDB", "JUnit", "Selenium", 
    "Playwright", "Android", "iOS", "Flutter", "Terraform", "Prometheus", "Grafana", 
    "PyTorch", "TensorFlow", "Pandas", "Scikit-Learn"
]

class ProfessionalFeatureBuilder:
    def __init__(self):
        self.skill_names = SKILL_NAMES
        self.feature_columns = ["experience_years", "college", "degree"] + [
            f"skill_{s.replace(' ', '_').replace('&', 'and')}" for s in self.skill_names
        ]

    def clean_college(self, name):
        if not name:
            return "Other"
        name_lower = str(name).lower().strip()
        if "iit" in name_lower or "indian institute of technology" in name_lower:
            return "IIT"
        if "nit" in name_lower or "national institute of technology" in name_lower:
            return "NIT"
        if "iiit" in name_lower or "indian institute of information" in name_lower:
            return "IIIT"
        if "bits" in name_lower or "birla institute" in name_lower:
            return "BITS"
        return "Other"

    def clean_degree(self, deg):
        if not deg:
            return "Other"
        deg_lower = str(deg).lower().strip()
        if "b.tech" in deg_lower or "btech" in deg_lower or "bachelor of technology" in deg_lower:
            return "BTech"
        if "m.tech" in deg_lower or "mtech" in deg_lower or "master of technology" in deg_lower:
            return "MTech"
        if "mca" in deg_lower or "master of computer applications" in deg_lower:
            return "MCA"
        if "b.e" in deg_lower or "be" in deg_lower or "bachelor of engineering" in deg_lower:
            return "BE"
        if "dual degree" in deg_lower or "dual" in deg_lower:
            return "Dual Degree"
        return "Other"

    def normalize_skill_name(self, raw_name):
        name_low = str(raw_name).lower().strip()
        name_low = re.sub(r'\(.*\)', '', name_low).strip()
        
        alias_map = {
            "react.js": "react",
            "reactjs": "react",
            "react js": "react",
            "node.js": "nodejs",
            "nodejs": "nodejs",
            "node js": "nodejs",
            "next.js": "nextjs",
            "nextjs": "nextjs",
            "next js": "nextjs",
            "javascript": "javascript",
            "js": "javascript",
            "typescript": "typescript",
            "ts": "typescript",
            "html": "html & css",
            "css": "html & css",
            "html5": "html & css",
            "css3": "html & css",
            "cascading style sheets": "html & css",
            "amazon web services": "aws basics",
            "aws": "aws basics",
            "apache kafka": "message queues (kafka)",
            "kafka": "message queues (kafka)",
            "amazon dynamodb": "dynamodb",
            "dynamodb": "dynamodb",
            "systems design": "system design",
            "object oriented programming": "object oriented programming",
            "oop": "object oriented programming",
            "oops": "object oriented programming",
            "postgres": "postgresql",
            "postgresql": "postgresql",
            "git": "git & github",
            "github": "git & github",
            "git & github": "git & github"
        }
        
        if name_low in alias_map:
            return alias_map[name_low]
        return name_low

    def build_features(self, skills, experience_years, college, degree):
        """
        Builds a single-row pandas DataFrame matching the schema expected by the pipelines.
        """
        # Clean numeric/categorical features
        try:
            exp_val = float(experience_years or 0.0)
        except Exception:
            exp_val = 0.0
            
        coll_val = self.clean_college(college)
        deg_val = self.clean_degree(degree)
        
        # Build skills map
        skills_set = {self.normalize_skill_name(s) for s in (skills or [])}
        
        row_dict = {
            "experience_years": exp_val,
            "college": coll_val,
            "degree": deg_val
        }
        
        for s_name in self.skill_names:
            col_name = f"skill_{s_name.replace(' ', '_').replace('&', 'and')}"
            # Check direct match or normalized match
            s_name_norm = self.normalize_skill_name(s_name)
            if s_name_norm in skills_set or s_name.lower().strip() in skills_set:
                row_dict[col_name] = 1
            else:
                # Substring check fallback
                matched = 0
                for user_s in skills_set:
                    if user_s in s_name_norm or s_name_norm in user_s:
                        matched = 1
                        break
                row_dict[col_name] = matched
                
        # Return structured DataFrame with exact column ordering
        return pd.DataFrame([row_dict], columns=self.feature_columns)
