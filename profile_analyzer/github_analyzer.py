# GitHub Profile Analyzer - CareerCompass AI
# Dynamically queries PostgreSQL skills, pulls live repositories, and generates a consolidated technology map.

import re
import urllib.request
import json
import base64
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

class GitHubAnalyzer:
    """
    Analyzes GitHub profiles, repository layouts, and languages used.
    Extracts SDE skills and builds a technology frequency map.
    """
    
    @staticmethod
    def extract_handle(url_or_text: str) -> str:
        if not url_or_text:
            return ""
        s = url_or_text.lower().strip()
        match = re.search(r'github\.com/([a-zA-Z0-9\-\_]+)', s)
        if match:
            return match.group(1).strip()
        if "github.com/" in s:
            parts = s.split("github.com/")
            if len(parts) > 1:
                return parts[1].split("/")[0].split(" ")[0].strip()
        return s.split("/")[-1].split(" ")[0].strip()

    @staticmethod
    def get_all_db_skills() -> list:
        """
        Dynamically queries skills from PostgreSQL.
        Throws RuntimeError if DB is unreachable.
        """
        return ResumeParser.get_all_db_skills()

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
    def analyze_profile(username_or_url: str) -> dict:
        if not username_or_url:
            return {}
            
        handle = GitHubAnalyzer.extract_handle(username_or_url)
        if not handle:
            return {"error": "Invalid GitHub username or URL.", "skills_raw": [], "frequency_map": {}}

        try:
            # 1. Load dynamic skills from database
            db_skills = GitHubAnalyzer.get_all_db_skills()
            db_skills_lower = {s.lower().strip(): s for s in db_skills}

            # 2. Fetch repositories from live API
            url = f"https://api.github.com/users/{handle}/repos?per_page=30"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=4.0) as response:
                repos = json.loads(response.read().decode('utf-8'))
                
            if not isinstance(repos, list):
                raise ValueError("API response is not a valid list of repositories.")
                
            frequency_map = {}
            skills_raw = set()
            parsed_repos = []
            
            # Sort repos by stargazers_count
            sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
            
            # Analyze top 8 repositories
            for idx, r in enumerate(sorted_repos[:8]):
                repo_name = r.get("name", "")
                description = r.get("description") or ""
                language = r.get("language") or ""
                topics = r.get("topics") or []
                topics_str = " ".join(topics)
                
                # Fetch README content for top 3 repos
                readme_text = ""
                if idx < 3:
                    try:
                        readme_url = f"https://api.github.com/repos/{handle}/{repo_name}/readme"
                        readme_req = urllib.request.Request(readme_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(readme_req, timeout=2.0) as readme_resp:
                            readme_data = json.loads(readme_resp.read().decode('utf-8'))
                            content_b64 = readme_data.get("content", "").replace("\n", "")
                            readme_text = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                    except Exception:
                        pass # Skip README if unavailable
                
                # Combine repo text
                combined_text = f"{repo_name} {description} {language} {topics_str} {readme_text}"
                
                # Match skills for this repository
                repo_skills = set()
                
                # Direct skill matches
                for skill in db_skills:
                    if GitHubAnalyzer.match_skill_in_text(skill, combined_text):
                        repo_skills.add(skill)
                
                # Inference rules (aligned with DB skills)
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
                
                for term, inf_list in inference_rules.items():
                    if re.search(r'\b' + re.escape(term) + r'\b', combined_text.lower()):
                        for inf_skill in inf_list:
                            if inf_skill in db_skills_lower:
                                repo_skills.add(db_skills_lower[inf_skill])
                
                # Update frequency map
                for skill in repo_skills:
                    frequency_map[skill] = frequency_map.get(skill, 0) + 1
                    skills_raw.add(skill)
                    
                parsed_repos.append({
                    "name": repo_name,
                    "description": description or "SDE repository",
                    "language": language or "Other",
                    "stars": r.get("stargazers_count", 0),
                    "topics": topics,
                    "extracted_skills": sorted(list(repo_skills))
                })
                
            return {
                "username": handle,
                "public_repos": len(repos),
                "pinned_projects": parsed_repos,
                "skills_raw": sorted(list(skills_raw)),
                "frequency_map": frequency_map,
                "source": "GitHub Live API"
            }
            
        except Exception as e:
            # Under new "Real Data Only" directive, never return simulated repositories fallbacks.
            # Return professional clean error state
            return {
                "error": "GitHub profile analysis is temporarily unavailable.",
                "details": str(e),
                "username": handle,
                "public_repos": 0,
                "pinned_projects": [],
                "skills_raw": [],
                "frequency_map": {},
                "source": "GitHub Profile Analyzer Error"
            }
