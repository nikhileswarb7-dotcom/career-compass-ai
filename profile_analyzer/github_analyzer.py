# GitHub Profile Analyzer - CareerCompass AI

import re
import urllib.request
import json
import base64
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
            print("Error loading skills in GitHubAnalyzer:", e)
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
    def analyze_profile(username_or_url: str) -> dict:
        if not username_or_url:
            return {}
            
        handle = GitHubAnalyzer.extract_handle(username_or_url)
        if not handle:
            return {"error": "Invalid GitHub username or URL.", "skills_raw": [], "frequency_map": {}}

        try:
            # 1. Fetch repositories from live API
            url = f"https://api.github.com/users/{handle}/repos?per_page=30"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=3.0) as response:
                repos = json.loads(response.read().decode('utf-8'))
                
            if not isinstance(repos, list):
                raise ValueError("API response is not a valid list of repositories.")
                
            db_skills = GitHubAnalyzer.get_all_db_skills()
            frequency_map = {}
            skills_raw = set()
            parsed_repos = []
            
            # Sort repos by stargazers_count to analyze the most important ones first
            sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
            
            # Analyze up to 8 repositories to balance depth and performance/rate-limits
            for idx, r in enumerate(sorted_repos[:8]):
                repo_name = r.get("name", "")
                description = r.get("description") or ""
                language = r.get("language") or ""
                topics = r.get("topics") or []
                topics_str = " ".join(topics)
                
                # Fetch README content for the top 3 repositories
                readme_text = ""
                if idx < 3:
                    try:
                        readme_url = f"https://api.github.com/repos/{handle}/{repo_name}/readme"
                        readme_req = urllib.request.Request(readme_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(readme_req, timeout=1.5) as readme_resp:
                            readme_data = json.loads(readme_resp.read().decode('utf-8'))
                            content_b64 = readme_data.get("content", "").replace("\n", "")
                            readme_text = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                    except Exception:
                        pass # Gracefully skip README if unavailable or rate-limited
                
                # Combine repo text
                combined_text = f"{repo_name} {description} {language} {topics_str} {readme_text}"
                
                # Match skills for this repository
                repo_skills = set()
                
                # Direct skill matches
                for skill in db_skills:
                    if GitHubAnalyzer.match_skill_in_text(skill, combined_text):
                        repo_skills.add(skill)
                
                # Inference rules
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
                    if re.search(pattern, combined_text, re.IGNORECASE):
                        for inf_skill in inferred_skills:
                            if inf_skill in db_skills:
                                repo_skills.add(inf_skill)
                
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
            # Under new "Real Data Only" directive, never return simulated repository fallback profiles.
            # Return professional error object
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
