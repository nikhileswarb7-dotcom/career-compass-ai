# Roadmap Generator - CareerCompass AI
# Dynamic stage-centric roadmap generator based on skill dependency graph

import os
import sys
import re
import logging
from pypdf import PdfReader
from api.database_connector import get_db_connection

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

logger = logging.getLogger("RoadmapGenerator")

# ----------------------------------------------------------------
# Stage-Centric Mapping Datasets
# ----------------------------------------------------------------

STAGE_SKILL_MAPPING = {
    1: ["c programming", "c++", "java", "python", "git & github", "git", "linux basics", "linux"],
    2: ["dsa (combined)", "data structures", "algorithms", "object oriented programming", "oop", "oops"],
    3: ["dbms", "sql", "postgresql", "mysql", "rest apis", "spring boot", "nodejs", "react", "typescript", "nextjs", "kotlin", "android", "django", "elasticsearch"],
    4: ["system design", "low level design", "lld", "high level design", "hld", "distributed systems", "redis", "message queues (kafka)", "kafka", "microservices", "docker", "kubernetes", "aws", "gcp", "sre"]
}

STAGE_FALLBACKS = {
    1: {
        "name": "Programming Foundations & Git",
        "objective": "Establish fundamental SDE programming capabilities and version control tracking.",
        "videos": [
            {"title": "Java Programming for Beginners (FreeCodeCamp)", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/A74TOX803D0", "embed": "https://www.youtube.com/embed/A74TOX803D0", "topic": "Java", "difficulty": "Beginner", "duration": "3 hrs"},
            {"title": "Git & GitHub Version Control Tutorial (FreeCodeCamp)", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/YS4e4q9oBaU", "embed": "https://www.youtube.com/embed/YS4e4q9oBaU", "topic": "Git", "difficulty": "Beginner", "duration": "1 hr"}
        ],
        "materials": [
            {"title": "Git Cheat Sheet.pdf", "platform": "PDF Resource", "type": "Article", "url": "#", "difficulty": "Beginner", "duration_hours": 1.0, "duration": "1 hr"}
        ],
        "mcqs": [
            {"question": "What is the primary purpose of version control systems like Git?", "options": ["To automate backend deployments", "To track change history and collaborate on source code", "To host SQL databases in the cloud", "To speed up local machine boot times"], "correct": 1, "explanation": "Git tracks commit history and enables developers to collaborate on a single codebase."},
            {"question": "In Git, what is the default branch name created upon git init?", "options": ["master or main", "dev", "trunk", "origin"], "correct": 0, "explanation": "Modern Git repositories initialize with 'main' or legacy 'master' as the default active branch."},
            {"question": "Which of these is a statically typed programming language?", "options": ["Python", "JavaScript", "Java", "Ruby"], "correct": 2, "explanation": "Java requires explicit declaration of variables and types during compilation."}
        ],
        "coding": {
            "title": "Reverse String",
            "desc": "Write a function to reverse a string in-place.",
            "template": "function reverseString(s) {\n    return s.split('').reverse().join('');\n}"
        },
        "interview_questions": [
            {"question": "Explain Git commit and push.", "answer": "Commit saves changes locally; push uploads commits to remote.", "explanation": "Allows developer changes synchronization.", "category": "Version Control"},
            {"question": "Difference between interpreter and compiler.", "answer": "Compiler translates the whole program; interpreter translates line-by-line.", "explanation": "Affects execution latency.", "category": "Programming Languages"}
        ],
        "project": {"name": "Version Controlled Syntax Sandbox", "difficulty": "Beginner", "details": "Build a modular utility using Python or Java, and track changes using Git branches."}
    },
    2: {
        "name": "Data Structures & OOP",
        "objective": "Understand object-oriented paradigms and analyze algorithm time/space complexities.",
        "videos": [
            {"title": "Data Structures & Algorithms Course for SDEs", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/RGOj5yH7evk", "embed": "https://www.youtube.com/embed/RGOj5yH7evk", "topic": "DSA", "difficulty": "Beginner", "duration": "2 hrs"},
            {"title": "Object Oriented Programming (OOP) Crash Course", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/zOjov-2OZ0E", "embed": "https://www.youtube.com/embed/zOjov-2OZ0E", "topic": "OOP", "difficulty": "Beginner", "duration": "1 hr"}
        ],
        "materials": [
            {"title": "OOP Cheat Sheet.pdf", "platform": "PDF Resource", "type": "Article", "url": "#", "difficulty": "Beginner", "duration_hours": 1.0, "duration": "1 hr"}
        ],
        "mcqs": [
            {"question": "What is the average search complexity in a balanced Binary Search Tree (BST)?", "options": ["O(N)", "O(N log N)", "O(log N)", "O(1)"], "correct": 2, "explanation": "Balanced BSTs halve search partitions at each node level, yielding logarithmic search latency."},
            {"question": "Which data structure follows the Last-In-First-Out (LIFO) access template?", "options": ["Queue", "Stack", "Tree", "Graph"], "correct": 1, "explanation": "Stacks store and retrieve elements where the latest element added is popped first."},
            {"question": "Which OOP concept refers to wrapping data and operations into a single class block?", "options": ["Inheritance", "Polymorphism", "Abstraction", "Encapsulation"], "correct": 3, "explanation": "Encapsulation hides internal state and exposes structured access via methods."}
        ],
        "coding": {
            "title": "Height-Balanced Binary Tree Check",
            "desc": "Implement a function isBalanced(root) returning true if a binary tree's left and right depths differ by at most 1.",
            "template": "function isBalanced(root) {\n    if (root === null) return true;\n    return checkHeight(root) !== -1;\n}"
        },
        "interview_questions": [
            {"question": "Explain Big-O notation.", "answer": "It describes the upper bound of execution time/space bounds.", "explanation": "Calculates worst-case scaling bounds.", "category": "Algorithms"},
            {"question": "Difference between Stack and Queue.", "answer": "Stack is LIFO; Queue is FIFO.", "explanation": "Fundamental elements ordering paradigms.", "category": "Data Structures"}
        ],
        "project": {"name": "Custom Data Structure Library", "difficulty": "Intermediate", "details": "Implement a balanced binary search tree or custom HashMap class using OOP principles."}
    },
    3: {
        "name": "Databases & Web APIs",
        "objective": "Build database schemas, normalizations, and deploy secure backend REST services.",
        "videos": [
            {"title": "SQL Tutorial - Full Database Course for Beginners", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/HXV3zeQKqGY", "embed": "https://www.youtube.com/embed/HXV3zeQKqGY", "topic": "SQL", "difficulty": "Intermediate", "duration": "4 hrs"},
            {"title": "Spring Boot Backend Development Tutorial", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/35EQXmHKZYs", "embed": "https://www.youtube.com/embed/35EQXmHKZYs", "topic": "Spring Boot", "difficulty": "Intermediate", "duration": "2.5 hrs"}
        ],
        "materials": [
            {"title": "PostgreSQL Indexing Cheat Sheet.pdf", "platform": "PDF Resource", "type": "Article", "url": "#", "difficulty": "Intermediate", "duration_hours": 1.0, "duration": "1 hr"}
        ],
        "mcqs": [
            {"question": "Which SQL key uniquely identifies a row in a relational database?", "options": ["Foreign Key", "Primary Key", "Composite Key", "Candidate Key"], "correct": 1, "explanation": "Primary keys strictly restrict duplicate rows and act as identifiers."},
            {"question": "What does the 'I' represent in the ACID transactional template?", "options": ["Idempotency", "Integrity", "Isolation", "Inheritance"], "correct": 2, "explanation": "Isolation guarantees concurrent transaction execution results match sequential order."},
            {"question": "Which HTTP method is idiomatic for updating an existing database record?", "options": ["GET", "POST", "PUT", "DELETE"], "correct": 2, "explanation": "PUT is standard for idempotently replacing target resources."}
        ],
        "coding": {
            "title": "REST Simple Rate Limiter",
            "desc": "Implement a helper returning false if a userId exceeds 5 requests per minute.",
            "template": "class RateLimiter {\n    constructor() {\n        this.requests = new Map();\n    }\n    isAllowed(userId) {\n        return true;\n    }\n}"
        },
        "interview_questions": [
            {"question": "What is an index in a database?", "answer": "A binary performance tree to speed up record lookup.", "explanation": "Avoids full table scans.", "category": "Databases"},
            {"question": "Explain database transactions and ACID.", "answer": "Atomicity, Consistency, Isolation, Durability.", "explanation": "Ensures storage integrity.", "category": "Databases"}
        ],
        "project": {"name": "RESTful Web Store Catalog Backend", "difficulty": "Intermediate", "details": "Build a Spring Boot or Node.js REST API with Postgres persistence and index optimization."}
    },
    4: {
        "name": "System Design, Scale & Cloud",
        "objective": "Design fault-tolerant high-concurrency systems using caches, message streams, and containers.",
        "videos": [
            {"title": "System Design Primer - High Level Architecture", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/m8I0esEK6so", "embed": "https://www.youtube.com/embed/m8I0esEK6so", "topic": "System Design", "difficulty": "Advanced", "duration": "30 mins"},
            {"title": "Apache Kafka for System Design & Queues (ByteByteGo)", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/R87354hyY2E", "embed": "https://www.youtube.com/embed/R87354hyY2E", "topic": "Kafka", "difficulty": "Advanced", "duration": "40 mins"}
        ],
        "materials": [
            {"title": "System Design Handbook.pdf", "platform": "PDF Resource", "type": "Article", "url": "#", "difficulty": "Advanced", "duration_hours": 1.0, "duration": "1 hr"}
        ],
        "mcqs": [
            {"question": "According to the CAP Theorem, which two attributes are selected during a network partition?", "options": ["Consistency & Latency", "Availability & Scalability", "Consistency & Availability (but Partition is guaranteed)", "None of the above"], "correct": 2, "explanation": "CAP states that under partitioning (P), a distributed system trades off Consistency (C) or Availability (A)."},
            {"question": "Which cache eviction policy discards the least recently updated keys first?", "options": ["LFU", "LRU", "FIFO", "LIFO"], "correct": 1, "explanation": "LRU (Least Recently Used) tracks update age and evicts the oldest read/write key."},
            {"question": "What is the primary benefit of pub-sub message queues like Kafka?", "options": ["Decrease client query latencies", "Decouple microservices and buffer system peak loads", "Enforce relational schema normalization", "Encrypt data payloads"], "correct": 1, "explanation": "Kafka acts as an asynchronous buffer, enabling message producers and consumers to scale independently."}
        ],
        "coding": {
            "title": "Concurrent Worker Channel",
            "desc": "Implement concurrent worker goroutines or threads dispatching messages.",
            "template": "function worker(jobs, results) {\n    // concurrent consumer worker logic\n}"
        },
        "interview_questions": [
            {"question": "Explain CAP theorem and how it applies to databases.", "answer": "Consistency, Availability, and Partition Tolerance choice constraints.", "explanation": "Governs database replica scaling.", "category": "System Design"},
            {"question": "Explain horizontal vs vertical scaling.", "answer": "Horizontal adds machines; vertical adds processing power/memory.", "explanation": "Affects capacity bounds.", "category": "System Design"}
        ],
        "project": {"name": "High-Concurrency Order Dispatching Engine", "difficulty": "Advanced", "details": "Build a scalable dispatcher in Go/Java utilizing Redis Geo-indexing and Apache Kafka message queuing."}
    }
}

# ----------------------------------------------------------------
# Database queries
# ----------------------------------------------------------------

def get_qualification_metadata(qualification_name: str) -> dict:
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT urgency, typical_duration_months, available_time
                FROM qualifications
                WHERE LOWER(qualification_name) = %s;
            """, (qualification_name.lower().strip(),))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                urgency, months, av_time = row
                weekly_hours = 15
                if av_time == "High":
                    weekly_hours = 35
                elif av_time == "Medium":
                    weekly_hours = 25
                elif av_time in ("Low", "Very Low"):
                    weekly_hours = 12
                
                return {
                    "urgency": urgency or "Medium",
                    "weekly_hours": weekly_hours,
                    "months": months or 12
                }
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error querying qualification metadata: {e}")
            
    baselines = {
        "1st Year Student":         {"urgency": "Low",      "weekly_hours": 10, "months": 48},
        "2nd Year Student":         {"urgency": "Low",      "weekly_hours": 15, "months": 36},
        "3rd Year Student":         {"urgency": "High",     "weekly_hours": 25, "months": 18},
        "4th Year Student":         {"urgency": "Critical", "weekly_hours": 35, "months": 6},
        "Fresh Graduate":           {"urgency": "Critical", "weekly_hours": 40, "months": 6},
        "Trainee Engineer":         {"urgency": "High",     "weekly_hours": 15, "months": 9},
        "Junior Software Engineer": {"urgency": "Medium",   "weekly_hours": 12, "months": 12},
    }
    
    clean_name = qualification_name.strip()
    for k, v in baselines.items():
        if k.lower() == clean_name.lower():
            return v
            
    return {"urgency": "Medium", "weekly_hours": 15, "months": 12}

def extract_roadmap_skills_from_pdf(role_name: str) -> list:
    role_lower = role_name.lower().strip()
    filename = None
    if "ai" in role_lower or "artificial intelligence" in role_lower:
        filename = "ai_engineer_roadmap.pdf"
    elif "android" in role_lower:
        filename = "android_developer_roadmap.pdf"
    elif "backend" in role_lower:
        filename = "backend_developer_roadmap.pdf"
    elif "data analyst" in role_lower:
        filename = "data_analyst_roadmap.pdf"
    elif "data engineer" in role_lower:
        filename = "data_engineer_roadmap.pdf"
    elif "devops" in role_lower or "sre" in role_lower:
        filename = "devops_engineer_roadmap.pdf"
    elif "frontend" in role_lower or "ui" in role_lower:
        filename = "frontend_engineer_roadmap.pdf"
    elif "full stack" in role_lower or "fullstack" in role_lower:
        filename = "fullstack_developer_roadmap.pdf"
    elif "machine learning" in role_lower or "ml" in role_lower:
        filename = "ml_engineer_roadmap.pdf"
    else:
        filename = "backend_developer_roadmap.pdf"
        
    pdf_path = os.path.join(BASE_DIR, "raw_data", "roadmap_roles", filename)
    if not os.path.exists(pdf_path):
        return []
        
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
            
        skills_master = get_skills_master()
        found_skills = []
        for s in skills_master:
            s_name = s["name"]
            escaped_name = re.escape(s_name.lower().strip())
            pattern = r'\b' + escaped_name + r'\b'
            if "+" in s_name or "#" in s_name:
                pattern = escaped_name
            match = re.search(pattern, full_text.lower())
            if match:
                found_skills.append({
                    "skill": s,
                    "index": match.start()
                })
                
        found_skills.sort(key=lambda x: x["index"])
        return [f["skill"] for f in found_skills]
    except Exception as e:
        logger.error(f"Error parsing PDF roadmap {filename}: {e}")
        return []

def get_all_skills():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("SELECT skill_id, skill_name, category, difficulty FROM skills")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "name": r[1], "category": r[2], "difficulty": r[3]} for r in rows]
    except Exception:
        if conn: conn.close()
        return []

def get_skills_master():
    return get_all_skills()

def get_resources_by_skill_ids_db(skill_ids: list, future_skill_ids: list = None):
    if not skill_ids:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            query = f"""
                SELECT r.resource_id, r.title, r.resource_type, r.topic, rsm.skill_id, r.url, r.platform, r.difficulty, r.duration_hours
                FROM resources r
                JOIN resource_skill_mapping rsm ON r.resource_id = rsm.resource_id
                WHERE rsm.skill_id IN ({placeholders})
            """
            params = list(skill_ids)
            if future_skill_ids:
                future_placeholders = ",".join(["%s"] * len(future_skill_ids))
                query += f"""
                    AND r.resource_id NOT IN (
                        SELECT rsm2.resource_id
                        FROM resource_skill_mapping rsm2
                        WHERE rsm2.skill_id IN ({future_placeholders})
                    )
                """
                params.extend(future_skill_ids)
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [{
                "id": r[0],
                "title": r[1],
                "type": r[2],
                "topic": r[3],
                "skill_id": r[4],
                "url": r[5],
                "platform": r[6],
                "difficulty": r[7],
                "duration_hours": r[8] or 4.0
            } for r in rows]
        except Exception:
            if conn: conn.close()
    return []

def get_projects_by_skill_ids_db(skill_ids: list, future_skill_ids: list = None):
    if not skill_ids:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            query = f"""
                SELECT DISTINCT p.project_id, p.project_name, p.description, p.difficulty, p.skills_covered
                FROM projects p
                JOIN project_skill_mapping psm ON p.project_id = psm.project_id
                WHERE psm.skill_id IN ({placeholders})
            """
            params = list(skill_ids)
            if future_skill_ids:
                future_placeholders = ",".join(["%s"] * len(future_skill_ids))
                query += f"""
                    AND p.project_id NOT IN (
                        SELECT psm2.project_id
                        FROM project_skill_mapping psm2
                        WHERE psm2.skill_id IN ({future_placeholders})
                    )
                """
                params.extend(future_skill_ids)
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            import json
            res = []
            for r in rows:
                skills = r[4]
                if isinstance(skills, str):
                    try: skills = json.loads(skills)
                    except Exception: skills = []
                res.append({
                    "id": r[0],
                    "name": r[1],
                    "details": r[2],
                    "difficulty": r[3],
                    "skills": skills if isinstance(skills, list) else []
                })
            return res
        except Exception:
            if conn: conn.close()
    return []

def get_interview_questions_by_skill_ids_db(skill_ids: list, future_skill_ids: list = None):
    if not skill_ids:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            query = f"""
                SELECT DISTINCT q.question_id, q.question, q.answer, q.explanation, q.difficulty, q.category
                FROM interview_questions q
                JOIN interview_question_skill_mapping iqsm ON q.question_id = iqsm.question_id
                WHERE iqsm.skill_id IN ({placeholders})
            """
            params = list(skill_ids)
            if future_skill_ids:
                future_placeholders = ",".join(["%s"] * len(future_skill_ids))
                query += f"""
                    AND q.question_id NOT IN (
                        SELECT iqsm2.question_id
                        FROM interview_question_skill_mapping iqsm2
                        WHERE iqsm2.skill_id IN ({future_placeholders})
                    )
                """
                params.extend(future_skill_ids)
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [{
                "id": r[0],
                "question": r[1],
                "answer": r[2],
                "explanation": r[3],
                "difficulty": r[4],
                "category": r[5]
            } for r in rows]
        except Exception:
            if conn: conn.close()
    return []

def get_mcqs_by_skill_ids_db(skill_ids: list, future_skill_ids: list = None):
    if not skill_ids:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            query = f"""
                SELECT DISTINCT m.mcq_id, m.question, m.options, m.correct_option, m.explanation
                FROM mcqs m
                JOIN mcq_skill_mapping msm ON m.mcq_id = msm.mcq_id
                WHERE msm.skill_id IN ({placeholders})
            """
            params = list(skill_ids)
            if future_skill_ids:
                future_placeholders = ",".join(["%s"] * len(future_skill_ids))
                query += f"""
                    AND m.mcq_id NOT IN (
                        SELECT msm2.mcq_id
                        FROM mcq_skill_mapping msm2
                        WHERE msm2.skill_id IN ({future_placeholders})
                    )
                """
                params.extend(future_skill_ids)
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            import json
            res = []
            for r in rows:
                opts = r[2]
                if isinstance(opts, str):
                    try: opts = json.loads(opts)
                    except Exception: opts = []
                res.append({
                    "id": r[0],
                    "question": r[1],
                    "options": opts,
                    "correct": r[3],
                    "explanation": r[4]
                })
            return res
        except Exception:
            if conn: conn.close()
    return []

# ----------------------------------------------------------------
# Main Stage-Centric Timeline Generation
# ----------------------------------------------------------------

def generate_timeline(
    qualification: str, 
    missing_skills: dict, 
    dream_company: str = "Blinkit", 
    dream_sector: str = "Quick-Commerce", 
    fresh_passout: bool = False, 
    target_role: str = "Junior Software Engineer",
    similar_engineers: list = None,
    assessment_scores: dict = None,
    candidate_profile: dict = None
) -> dict:
    """
    Generates a stage-centric study timeline respecting skill prerequisites.
    Ties resources, projects, MCQs, and coding challenges strictly to the skills of each stage.
    """
    meta = get_qualification_metadata(qualification)
    months = meta["months"]
    weekly_hours = meta["weekly_hours"]
    urgency = meta["urgency"]
    
    # Apply Career Stage adjustments
    if assessment_scores and "career_stage" in assessment_scores:
        stage_eval = assessment_scores["career_stage"]
        weekly_hours = stage_eval.get("recommended_hours_weekly", weekly_hours)
        if stage_eval.get("track_status") == "Needs Acceleration":
            weekly_hours = min(int(weekly_hours * 1.2), 45)
            
    if fresh_passout:
        months = 3
        weekly_hours = max(weekly_hours * 1.5, 35)
        urgency = "Immediate / Fast-Track"

    pref_diffs = ["Intermediate", "Advanced", "Easy", "Beginner"]
    if qualification in ("1st Year Student", "2nd Year Student"):
        pref_diffs = ["Easy", "Beginner", "Intermediate", "Advanced"]
    elif qualification in ("3rd Year Student", "Trainee Engineer"):
        pref_diffs = ["Intermediate", "Advanced", "Easy", "Beginner"]
    else:
        pref_diffs = ["Advanced", "Intermediate", "Easy", "Beginner"]

    # Gather database master skills mapping
    skills_master = get_skills_master()
    skills_by_name = {s["name"].lower().strip(): s for s in skills_master}
    
    # Ingest missing skills
    missing_with_meta = []
    for prio, s_list in missing_skills.items():
        if not isinstance(s_list, list):
            continue
        for s_name in s_list:
            s_name_lower = s_name.lower().strip()
            if s_name_lower in skills_by_name:
                meta_s = skills_by_name[s_name_lower]
                missing_with_meta.append({
                    "name": meta_s["name"],
                    "id": meta_s["id"],
                    "category": meta_s["category"],
                    "difficulty": meta_s["difficulty"],
                    "priority": prio
                })
            else:
                category = "Programming"
                if any(k in s_name_lower for k in ["design", "architecture", "microservices", "kubernetes", "docker", "cloud", "aws", "grpc"]):
                    category = "Cloud"
                elif any(k in s_name_lower for k in ["dbms", "sql", "postgres", "mysql", "redis", "kafka", "mongo"]):
                    category = "Backend"
                missing_with_meta.append({
                    "name": s_name,
                    "id": None,
                    "category": category,
                    "difficulty": "Intermediate",
                    "priority": prio
                })

    # Filter skills based on qualification rules
    qual_lower = qualification.lower()
    if "1st year" in qual_lower:
        allowed_categories = ["Programming", "Core CS", "DevOps"]
        excluded_skills = {"system design", "high level design", "low level design", "microservices", "kubernetes", "kafka", "message queues (kafka)", "redis", "sre", "distributed systems", "grpc", "gcp", "aws basics", "spring boot", "nodejs", "elasticsearch", "django", "nextjs", "kotlin", "android"}
        missing_with_meta = [s for s in missing_with_meta if s["category"] in allowed_categories and s["name"].lower().strip() not in excluded_skills]
    elif "2nd year" in qual_lower:
        excluded_skills = {"system design", "high level design", "microservices", "kubernetes", "kafka", "message queues (kafka)", "redis", "sre", "distributed systems", "grpc", "gcp", "aws basics", "elasticsearch", "nextjs"}
        missing_with_meta = [s for s in missing_with_meta if s["name"].lower().strip() not in excluded_skills]
    elif "3rd year" in qual_lower:
        excluded_skills = {"kubernetes", "sre", "gcp"}
        missing_with_meta = [s for s in missing_with_meta if s["name"].lower().strip() not in excluded_skills]
    elif "4th year" in qual_lower or "graduate" in qual_lower:
        missing_with_meta = [s for s in missing_with_meta if s["priority"] in ("High", "Medium")]
    elif "trainee" in qual_lower or "junior" in qual_lower:
        missing_with_meta = [s for s in missing_with_meta if s["category"] not in ("Programming") or s["name"].lower().strip() in ("go", "java", "python")]

    def calculate_hours_needed(skills_list):
        hours = 0
        for s in skills_list:
            diff = s["difficulty"].lower()
            prio = s["priority"]
            factor = 1.0 if prio == "High" else (0.75 if prio == "Medium" else 0.5)
            base = 40 if "advanced" in diff else (20 if "beginner" in diff else 30)
            hours += base * factor
        return max(hours, 15)

    # Fetch SDE or target role stage skills from database stage_skills
    db_stage_skills = {}
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT role_id FROM roles WHERE LOWER(role_name) = %s;", (target_role.lower().strip(),))
            row_role = cur.fetchone()
            if row_role:
                role_id = row_role[0]
                cur.execute("""
                    SELECT cr.company_role_id FROM company_roles cr
                    JOIN companies c ON cr.company_id = c.company_id
                    WHERE LOWER(c.company_name) = %s AND cr.role_id = %s;
                """, (dream_company.lower().strip(), role_id))
                row_cr = cur.fetchone()
                if row_cr:
                    company_role_id = row_cr[0]
                    cur.execute("""
                        SELECT r.roadmap_id FROM roadmaps r
                        JOIN qualifications q ON r.qualification_id = q.qualification_id
                        WHERE LOWER(q.qualification_name) = %s AND r.company_role_id = %s;
                    """, (qualification.lower().strip(), company_role_id))
                    row_rm = cur.fetchone()
                    if row_rm:
                        roadmap_id = row_rm[0]
                        cur.execute("""
                            SELECT rs.stage_number, ss.skill_id 
                            FROM roadmap_stages rs
                            JOIN stage_skills ss ON rs.stage_id = ss.stage_id
                            WHERE rs.roadmap_id = %s;
                        """, (roadmap_id,))
                        for stg_num, skill_id in cur.fetchall():
                            db_stage_skills.setdefault(stg_num, []).append(skill_id)
            cur.close()
            conn.close()
        except Exception:
            if conn: conn.close()

    # 1. Respect prerequisites by mapping skills to exact stages
    for s in missing_with_meta:
        s_name_low = s["name"].lower().strip()
        assigned_stage = None
        
        # Check DB mappings first
        if s["id"] is not None:
            for stg_num, db_sids in db_stage_skills.items():
                if s["id"] in db_sids:
                    assigned_stage = stg_num
                    break
        
        if not assigned_stage:
            # Fallback to local STAGE_SKILL_MAPPING
            for stg_num, skills_list in STAGE_SKILL_MAPPING.items():
                if s_name_low in skills_list or any(kw in s_name_low for kw in skills_list):
                    assigned_stage = stg_num
                    break
        if not assigned_stage:
            cat = s["category"].lower()
            if "programming" in cat or "language" in cat:
                assigned_stage = 1
            elif "dsa" in cat or "core" in cat:
                assigned_stage = 2
            elif "database" in cat or "backend" in cat or "frontend" in cat:
                assigned_stage = 3
            else:
                assigned_stage = 4
        s["stage_num"] = assigned_stage

    # 2. Group missing skills
    stage_groups = {1: [], 2: [], 3: [], 4: []}
    for s in missing_with_meta:
        stage_groups[s["stage_num"]].append(s)

    # Build sequence prefixes
    custom_stage_prefix = "SDE Track"
    if "1st year" in qual_lower:
        custom_stage_prefix = "Spaced Foundation"
    elif "2nd year" in qual_lower:
        custom_stage_prefix = "Foundation Phase"
    elif "3rd year" in qual_lower:
        custom_stage_prefix = "Placement Prep"
    elif "4th year" in qual_lower or "graduate" in qual_lower:
        custom_stage_prefix = "Placement Sprint"
    elif "trainee" in qual_lower or "junior" in qual_lower:
        custom_stage_prefix = "Professional Track"

    stages = []
    stage_idx = 1
    global_projects = []
    global_resources = []

    # Map all database skill IDs to their stage for future skill calculation
    skills_db_stage_map = {}
    for s in skills_master:
        s_id = s["id"]
        s_name_low = s["name"].lower().strip()
        assigned = None
        if db_stage_skills:
            for stg_num, db_sids in db_stage_skills.items():
                if s_id in db_sids:
                    assigned = stg_num
                    break
        if not assigned:
            for stg_num, skills_list in STAGE_SKILL_MAPPING.items():
                if s_name_low in skills_list or any(kw in s_name_low for kw in skills_list):
                    assigned = stg_num
                    break
        if not assigned:
            cat = s["category"].lower()
            if "programming" in cat or "language" in cat:
                assigned = 1
            elif "dsa" in cat or "core" in cat:
                assigned = 2
            elif "database" in cat or "backend" in cat or "frontend" in cat:
                assigned = 3
            else:
                assigned = 4
        skills_db_stage_map[s_id] = assigned

    # 3. Create stages sequentially
    for stg_num in range(1, 5):
        band_skills = stage_groups[stg_num]
        if not band_skills:
            continue
            
        cluster_skill_ids = [s["id"] for s in band_skills if s["id"] is not None]
        
        # Calculate future stage skill IDs for exclusions
        future_skill_ids = [
            s_id for s_id, stage_val in skills_db_stage_map.items()
            if stage_val > stg_num
        ]
        
        # Weeks duration
        hours = calculate_hours_needed(band_skills)
        weeks = max(round(hours / weekly_hours), 2)
        
        # Load resources from database mapped strictly to current stage skill IDs and excluding future skills
        db_res = get_resources_by_skill_ids_db(cluster_skill_ids, future_skill_ids)
        videos = []
        materials = []
        for r in db_res:
            r_item = {
                "id": r["id"],
                "title": r["title"],
                "platform": r["platform"],
                "type": r["type"],
                "url": r["url"],
                "embed": r["url"],
                "topic": r["topic"],
                "difficulty": r["difficulty"],
                "duration_hours": r["duration_hours"],
                "duration": f"{int(r['duration_hours'])} hrs" if r['duration_hours'] else "4 hrs"
            }
            if r["type"] in ("Video", "Playlist") or r["platform"] == "YouTube":
                # Ensure we transform embed url format
                if "youtube" in r["url"] and "embed" not in r["url"]:
                    m = re.search(r'(?:v=|\/)([\w\-]{11})(?:\?|&|$)', r["url"])
                    if m:
                        r_item["embed"] = f"https://www.youtube.com/embed/{m.group(1)}"
                videos.append(r_item)
            else:
                materials.append(r_item)

        # Apply stage-centric fallback resources to guarantee internal consistency
        stage_meta = STAGE_FALLBACKS[stg_num]
        
        while len(videos) < 2:
            fb = stage_meta["videos"][len(videos) % len(stage_meta["videos"])]
            videos.append(dict(fb))
        while len(materials) < 1:
            fb = stage_meta["materials"][len(materials) % len(stage_meta["materials"])]
            materials.append(dict(fb))

        # Dedup and sort resources by preference
        videos = sorted(videos, key=lambda r: pref_diffs.index(r["difficulty"]) if r.get("difficulty") in pref_diffs else 999)
        materials = sorted(materials, key=lambda r: pref_diffs.index(r["difficulty"]) if r.get("difficulty") in pref_diffs else 999)

        # Project Selection
        db_projs = get_projects_by_skill_ids_db(cluster_skill_ids, future_skill_ids)
        best_proj = None
        if db_projs:
            db_projs = sorted(db_projs, key=lambda p: pref_diffs.index(p["difficulty"]) if p.get("difficulty") in pref_diffs else 999)
            best_proj = db_projs[0]
        else:
            best_proj = stage_meta["project"]

        global_projects.append({
            "id": best_proj.get("id"),
            "name": best_proj["name"],
            "difficulty": best_proj["difficulty"],
            "details": best_proj.get("details", best_proj.get("description", ""))
        })

        # MCQ Selection
        db_mcqs = get_mcqs_by_skill_ids_db(cluster_skill_ids, future_skill_ids)
        if len(db_mcqs) < 3:
            db_mcqs = list(stage_meta["mcqs"])

        # Coding challenge template selection
        coding_challenge = stage_meta["coding"]
        if best_proj and best_proj.get("name") != stage_meta["project"]["name"]:
            coding_challenge = {
                "title": best_proj["name"],
                "desc": best_proj.get("details", best_proj.get("description", "")),
                "template": "function solve() {\n    // write SDE solution\n    return true;\n}"
            }

        # Interview questions selection
        db_questions = get_interview_questions_by_skill_ids_db(cluster_skill_ids, future_skill_ids)
        if len(db_questions) < 2:
            db_questions = list(stage_meta["interview_questions"])

        # Stage formatting strings
        skills_names = [s["name"] for s in band_skills]
        stage_skills_str = ", ".join(skills_names[:3]) + ", etc." if len(skills_names) > 3 else ", ".join(skills_names)

        focus = f"{stage_meta['objective']} Focus on SDE competencies in: {', '.join(skills_names)}."
        focus += f" Recommended Project: {best_proj['name']}."
        
        learning_goals = [f"Understand core paradigms of {', '.join(skills_names)}."]
        for r in videos[:2]:
            learning_goals.append(f"Learn {r['topic'] or 'Skill'}: {r['title']} ({r['platform']}) - {r['embed']}")

        # Track global resources
        for r in videos[:2] + materials[:1]:
            global_resources.append({
                "id": r.get("id"),
                "title": r["title"],
                "platform": r["platform"],
                "type": r["type"],
                "url": r["url"]
            })

        stages.append({
            "stage": stage_idx,
            "title": f"Stage {stage_idx} ({custom_stage_prefix}): {stage_meta['name']} ({stage_skills_str}) - {weeks} weeks",
            "duration_weeks": weeks,
            "focus": focus,
            "milestone": f"[{qualification} Goal] {stage_meta['objective']} Validate checkpoints.",
            "learning_goals": learning_goals,
            "videos": videos[:3],
            "materials": materials[:3],
            "mcqs": db_mcqs[:10],
            "coding": coding_challenge,
            "interview_questions": db_questions[:3],
            "_stage_skill_ids": cluster_skill_ids  # Hidden field to pass to validator
        })
        stage_idx += 1

    # Fallback placement review if no stages mapped
    if not stages:
        stage_meta = STAGE_FALLBACKS[4]
        duration_weeks = max(round(30 / weekly_hours), 2)
        stages.append({
            "stage": 1,
            "title": f"Stage 1 (Mock Prep): Placement Review & Mock Interviews - {duration_weeks} weeks",
            "duration_weeks": duration_weeks,
            "focus": f"Mock interview and coding review targeting SDE roles.",
            "milestone": f"[{qualification} Goal] Pass mock interview technical loops.",
            "learning_goals": ["Final mock practice", "Resume tuning"],
            "videos": stage_meta["videos"],
            "materials": stage_meta["materials"],
            "mcqs": stage_meta["mcqs"],
            "coding": stage_meta["coding"],
            "interview_questions": stage_meta["interview_questions"],
            "_stage_skill_ids": []
        })

    # Scaling weeks according to typical timeline constraints
    target_months = meta["months"]
    if "1st year" in qual_lower:
        target_months = max(target_months, 36)
    elif "2nd year" in qual_lower:
        target_months = max(target_months, 24)
    elif "3rd year" in qual_lower:
        target_months = max(target_months, 12)
    elif "4th year" in qual_lower:
        target_months = max(target_months, 6)

    target_weeks = target_months * 4.3
    current_total_weeks = sum(s["duration_weeks"] for s in stages)
    if current_total_weeks > 0 and target_weeks > current_total_weeks:
        scale_factor = target_weeks / current_total_weeks
        for s in stages:
            s["duration_weeks"] = max(round(s["duration_weeks"] * scale_factor), 2)
            s["title"] = re.sub(r' - \d+ weeks$', f' - {s["duration_weeks"]} weeks', s["title"])

    total_weeks = sum(s["duration_weeks"] for s in stages)
    months = max(round(total_weeks / 4.3), 1)

    timeline_res = {
        "qualification": qualification,
        "months_remaining": months,
        "weekly_hours_recommended": weekly_hours,
        "urgency": urgency,
        "stages": stages,
        "projects": global_projects[:2],
        "resources": global_resources[:4]
    }

    # Run roadmap consistency validation
    known_skills = candidate_profile.get("skills", []) if candidate_profile else []
    validated_res = validate_roadmap_consistency(timeline_res, known_skills, get_db_connection())
    return validated_res

def validate_roadmap_consistency(roadmap_data: dict, student_known_skills: list, db_conn) -> dict:
    """
    Validates every recommended item in each stage of the roadmap.
    Checks:
      1. Every content item must map to at least one skill in the current stage (Positive Filtering).
      2. No content item can require skills that belong to future stages (Prerequisite Validation).
      3. Content mapped only at role level (no skill mappings at all) is rejected.
    Filters out invalid content, records rejected items, and updates the decision_trace.
    """
    if not db_conn:
        return roadmap_data

    try:
        cur = db_conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        
        # Load all content-skill mappings
        cur.execute("SELECT resource_id, skill_id FROM resource_skill_mapping;")
        resource_skills = {}
        for rid, sid in cur.fetchall():
            resource_skills.setdefault(rid, set()).add(sid)

        cur.execute("SELECT project_id, skill_id FROM project_skill_mapping;")
        project_skills = {}
        for pid, sid in cur.fetchall():
            project_skills.setdefault(pid, set()).add(sid)

        cur.execute("SELECT mcq_id, skill_id FROM mcq_skill_mapping;")
        mcq_skills = {}
        for mid, sid in cur.fetchall():
            mcq_skills.setdefault(mid, set()).add(sid)

        cur.execute("SELECT question_id, skill_id FROM interview_question_skill_mapping;")
        iq_skills = {}
        for qid, sid in cur.fetchall():
            iq_skills.setdefault(qid, set()).add(sid)

        cur.execute("SELECT skill_id, skill_name FROM skills;")
        skills_db = cur.fetchall()
        skills_by_name = {row[1].lower().strip(): row[0] for row in skills_db}
        
        cur.close()
    except Exception as e:
        logger.error(f"Error loading content-skill mappings in validator: {e}")
        return roadmap_data

    # Map student known skills to skill IDs
    known_skill_ids = set()
    for sname in student_known_skills:
        s_low = sname.lower().strip()
        if s_low in skills_by_name:
            known_skill_ids.add(skills_by_name[s_low])

    validation_evidence = []
    learned_skills = set(known_skill_ids)

    # First pass: collect all stage skill IDs
    stages = roadmap_data.get("stages", [])
    for stg in stages:
        stage_skills = set(stg.get("_stage_skill_ids", []))
        learned_skills = learned_skills.union(stage_skills)

        stg_num = stg["stage"]
        
        # Validation helper
        def validate_item(item_id, item_skills_dict):
            if item_id is None:
                return True, set(), set(), "Implicitly valid fallback"
            
            m_skills = item_skills_dict.get(item_id, set())
            if not m_skills:
                return False, set(), set(), "Rejected: Mapped only at role level (no skill mappings)"
                
            has_current = bool(m_skills & stage_skills)
            if not has_current:
                return False, m_skills & stage_skills, m_skills - learned_skills, "Rejected: No matching current-stage skill mapping"
                
            is_subset = m_skills.issubset(learned_skills)
            if not is_subset:
                return False, m_skills & stage_skills, m_skills - learned_skills, "Rejected: Unsatisfied future prerequisites"
                
            return True, m_skills & stage_skills, m_skills - learned_skills, "Passes validation"

        # Validate videos
        valid_videos = []
        for v in stg.get("videos", []):
            v_id = v.get("id")
            is_ok, matched, rejected, reason = validate_item(v_id, resource_skills)
            validation_evidence.append({
                "stage_id": stg_num,
                "content_type": "video",
                "content_id": v_id,
                "matched_skill_ids": list(matched),
                "rejected_skill_ids": list(rejected),
                "prerequisite_status": "satisfied" if is_ok else "unsatisfied",
                "selection_reason": reason
            })
            if is_ok:
                valid_videos.append(v)
        stg["videos"] = valid_videos

        # Validate materials
        valid_materials = []
        for m in stg.get("materials", []):
            m_id = m.get("id")
            is_ok, matched, rejected, reason = validate_item(m_id, resource_skills)
            validation_evidence.append({
                "stage_id": stg_num,
                "content_type": "material",
                "content_id": m_id,
                "matched_skill_ids": list(matched),
                "rejected_skill_ids": list(rejected),
                "prerequisite_status": "satisfied" if is_ok else "unsatisfied",
                "selection_reason": reason
            })
            if is_ok:
                valid_materials.append(m)
        stg["materials"] = valid_materials

        # Validate MCQs
        valid_mcqs = []
        for mq in stg.get("mcqs", []):
            mq_id = mq.get("id")
            is_ok, matched, rejected, reason = validate_item(mq_id, mcq_skills)
            validation_evidence.append({
                "stage_id": stg_num,
                "content_type": "mcq",
                "content_id": mq_id,
                "matched_skill_ids": list(matched),
                "rejected_skill_ids": list(rejected),
                "prerequisite_status": "satisfied" if is_ok else "unsatisfied",
                "selection_reason": reason
            })
            if is_ok:
                valid_mcqs.append(mq)
        stg["mcqs"] = valid_mcqs

        # Validate Interview Questions
        valid_questions = []
        for q in stg.get("interview_questions", []):
            q_id = q.get("id")
            is_ok, matched, rejected, reason = validate_item(q_id, iq_skills)
            validation_evidence.append({
                "stage_id": stg_num,
                "content_type": "interview_question",
                "content_id": q_id,
                "matched_skill_ids": list(matched),
                "rejected_skill_ids": list(rejected),
                "prerequisite_status": "satisfied" if is_ok else "unsatisfied",
                "selection_reason": reason
            })
            if is_ok:
                valid_questions.append(q)
        stg["interview_questions"] = valid_questions

        # Clean up hidden field
        stg.pop("_stage_skill_ids", None)

    # Attach validation evidence to the result dict for decision tracing/audits
    roadmap_data["_validation_evidence"] = validation_evidence
    return roadmap_data
