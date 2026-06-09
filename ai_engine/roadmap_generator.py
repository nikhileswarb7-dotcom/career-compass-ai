# Roadmap Generator - CareerCompass AI

QUALIFICATION_META = {
    "1st Year Student":         {"urgency": "Low",      "weekly_hours": 10, "months": 48},
    "2nd Year Student":         {"urgency": "Low",      "weekly_hours": 15, "months": 36},
    "3rd Year Student":         {"urgency": "High",     "weekly_hours": 25, "months": 18},
    "4th Year Student":         {"urgency": "Critical", "weekly_hours": 35, "months": 6},
    "Fresh Graduate":           {"urgency": "Critical", "weekly_hours": 40, "months": 6},
    "Trainee Engineer":         {"urgency": "High",     "weekly_hours": 15, "months": 9},
    "Junior Software Engineer": {"urgency": "Medium",   "weekly_hours": 12, "months": 12},
}

def load_dynamic_resources():
    import json
    import os
    import csv
    
    resources = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Try JSON
    json_path = os.path.join(base_dir, "database", "datasets", "resources", "learning_resources.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for r in data:
                    resources.append({
                        "title": r.get("title"),
                        "platform": r.get("platform"),
                        "type": r.get("resource_type"),
                        "url": r.get("url"),
                        "topic": r.get("topic"),
                        "difficulty": r.get("difficulty", "Intermediate")
                    })
                return resources
        except Exception:
            pass
            
    # Try CSV
    csv_path = os.path.join(base_dir, "database", "learning_layer", "learning_resources.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    resources.append({
                        "title": row.get("title"),
                        "platform": row.get("platform"),
                        "type": row.get("resource_type"),
                        "url": row.get("url"),
                        "topic": row.get("topic"),
                        "difficulty": row.get("difficulty", "Intermediate")
                    })
                return resources
        except Exception:
            pass
            
    return []

def load_dynamic_projects():
    import json
    import os
    import csv
    
    projects = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Try JSON
    json_path = os.path.join(base_dir, "database", "datasets", "projects", "projects.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for p in data:
                    projects.append({
                        "name": p.get("project_name"),
                        "difficulty": p.get("difficulty"),
                        "details": p.get("description"),
                        "skills": p.get("skills_covered", [])
                    })
                return projects
        except Exception:
            pass
            
    # Try CSV
    csv_path = os.path.join(base_dir, "database", "learning_layer", "projects_master.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    projects.append({
                        "name": row.get("project_name"),
                        "difficulty": row.get("difficulty"),
                        "details": row.get("description"),
                        "skills": []
                    })
                # Load mappings
                map_path = os.path.join(base_dir, "database", "learning_layer", "project_skill_mapping.csv")
                skills_path = os.path.join(base_dir, "database", "career_layer", "skills_master.csv")
                if os.path.exists(map_path) and os.path.exists(skills_path):
                    skills_map = {}
                    with open(skills_path, "r", encoding="utf-8") as sf:
                        s_reader = csv.DictReader(sf)
                        for s_row in s_reader:
                            skills_map[int(s_row["skill_id"])] = s_row["skill_name"]
                            
                    project_skills = {}
                    with open(map_path, "r", encoding="utf-8") as mf:
                        m_reader = csv.DictReader(mf)
                        for m_row in m_reader:
                            p_id = int(m_row["project_id"])
                            s_id = int(m_row["skill_id"])
                            if s_id in skills_map:
                                if p_id not in project_skills:
                                    project_skills[p_id] = []
                                project_skills[p_id].append(skills_map[s_id])
                    
                    for idx, p in enumerate(projects):
                        p_id = idx + 1
                        if p_id in project_skills:
                            p["skills"] = project_skills[p_id]
                            
                return projects
        except Exception:
            pass
            
    return []

def load_roadmap_from_db(qualification: str, dream_company: str, target_role: str):
    import os, sys
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from api.database_connector import get_db_connection
    except Exception:
        return None
        
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        
        # 1. Normalize Inputs
        q_mapped = qualification
        for q_key in ["1st Year Student", "2nd Year Student", "3rd Year Student", "4th Year Student", "Fresh Graduate", "Trainee Engineer", "Junior Software Engineer"]:
            if q_key.lower() == qualification.lower():
                q_mapped = q_key
                break

        c_mapped = dream_company
        for c_key in ["Blinkit", "Zomato", "Swiggy", "Paytm", "PhonePe", "Flipkart", "Amazon", "Google", "Microsoft", "Meta", "TCS", "Infosys"]:
            if c_key.lower() == dream_company.lower():
                c_mapped = c_key
                break
                
        r_mapped = target_role
        r_low = target_role.lower()
        if "frontend" in r_low:
            r_mapped = "Frontend Engineer"
        elif "backend" in r_low:
            r_mapped = "Backend Engineer"
        elif "devops" in r_low or "sre" in r_low:
            r_mapped = "SRE / DevOps Engineer"
        elif "ai" in r_low or "ml" in r_low or "machine learning" in r_low:
            r_mapped = "AI / ML Engineer"
        elif "mobile" in r_low or "android" in r_low or "ios" in r_low:
            r_mapped = "Mobile Engineer"
        elif "qa" in r_low or "test" in r_low:
            r_mapped = "QA Automation Engineer"
        elif "trainee" in r_low:
            r_mapped = "Trainee Engineer"
        elif "junior" in r_low:
            r_mapped = "Junior Software Engineer"
        elif "sde-1" in r_low or "sde 1" in r_low or "sde i" in r_low:
            r_mapped = "Software Development Engineer I (SDE-1)"
        else:
            r_mapped = "Software Development Engineer"

        # 2. Search exact match (case-insensitive)
        query = """
            SELECT r.roadmap_id, r.total_duration_months, r.overview
            FROM roadmaps r
            JOIN qualifications q ON r.qualification_id = q.qualification_id
            JOIN company_roles cr ON r.company_role_id = cr.company_role_id
            JOIN companies c ON cr.company_id = c.company_id
            JOIN roles ro ON cr.role_id = ro.role_id
            WHERE LOWER(q.qualification_name) = %s 
              AND LOWER(c.company_name) = %s 
              AND LOWER(ro.role_name) = %s;
        """
        cur.execute(query, (q_mapped.lower(), c_mapped.lower(), r_mapped.lower()))
        row = cur.fetchone()
        
        # 3. Try fallback to Blinkit SDE for this qualification if exact match not found
        if not row:
            cur.execute(query, (q_mapped.lower(), "blinkit", "software development engineer"))
            row = cur.fetchone()
            
        # 4. Try fallback to any Blinkit SDE roadmap
        if not row:
            cur.execute(query, ("3rd Year Student", "blinkit", "software development engineer"))
            row = cur.fetchone()
            
        if row:
            roadmap_id, total_months, overview = row
            cur.execute("""
                SELECT stage_number, stage_title, duration_weeks, focus_area, milestone, learning_goals
                FROM roadmap_stages
                WHERE roadmap_id = %s
                ORDER BY stage_number ASC;
            """, (roadmap_id,))
            stages_rows = cur.fetchall()
            
            stages = []
            for r in stages_rows:
                goals = r[5]
                if isinstance(goals, str):
                    try:
                        import json
                        goals = json.loads(goals)
                    except Exception:
                        goals = [goals]
                elif not isinstance(goals, list):
                    goals = []
                    
                stages.append({
                    "stage": r[0],
                    "title": r[1],
                    "duration_weeks": r[2],
                    "focus": r[3],
                    "milestone": r[4],
                    "learning_goals": goals
                })
            cur.close()
            conn.close()
            return {
                "months": total_months,
                "stages": stages,
                "overview": overview
            }
        cur.close()
        conn.close()
    except Exception as e:
        if conn:
            conn.close()
    return None

def get_all_skills():
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
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
    skills = get_all_skills()
    if skills:
        return skills
    # Fallback to CSV
    import csv, os
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(base_dir, "database", "career_layer", "skills_master.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [{
                    "id": int(row["skill_id"]),
                    "name": row["skill_name"],
                    "category": row.get("category", "General"),
                    "difficulty": row.get("difficulty", "Intermediate")
                } for row in reader]
        except Exception:
            pass
    return []

def get_resources_by_skill_ids(skill_ids: list):
    if not skill_ids:
        return []
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT resource_id, title, resource_type, topic, skill_id, url, platform, difficulty
                FROM resources
                WHERE skill_id IN ({placeholders})
            """, tuple(skill_ids))
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
                "difficulty": r[7]
            } for r in rows]
        except Exception:
            if conn: conn.close()
    
    # Fallback to CSV
    import csv, os
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(base_dir, "database", "learning_layer", "learning_resources.csv")
    res_list = []
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    s_id_str = row.get("skill_id")
                    if s_id_str:
                        try:
                            s_id = int(s_id_str)
                            if s_id in skill_ids:
                                res_list.append({
                                    "id": int(row.get("resource_id", 0) or 0),
                                    "title": row.get("title"),
                                    "type": row.get("resource_type"),
                                    "topic": row.get("topic"),
                                    "skill_id": s_id,
                                    "url": row.get("url"),
                                    "platform": row.get("platform"),
                                    "difficulty": row.get("difficulty", "Intermediate")
                                })
                        except ValueError:
                            pass
            return res_list
        except Exception:
            pass
    return []

def get_all_db_projects():
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT project_id, project_name, description, difficulty, skills_covered FROM projects")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            import json
            res = []
            for r in rows:
                skills = r[4]
                if isinstance(skills, str):
                    try:
                        skills = json.loads(skills)
                    except Exception:
                        skills = []
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

def get_db_skill_clusters():
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("""
            SELECT c.cluster_id, c.cluster_name, c.default_milestone, c.display_order, s.skill_name
            FROM skill_clusters c
            JOIN skill_cluster_skills cs ON c.cluster_id = cs.cluster_id
            JOIN skills s ON cs.skill_id = s.skill_id
            ORDER BY c.display_order ASC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        clusters = {}
        for r_id, name, milestone, display_order, skill_name in rows:
            if name not in clusters:
                clusters[name] = {
                    "id": name.lower().replace(" ", "_"),
                    "title": name,
                    "skills": [],
                    "default_milestone": milestone
                }
            clusters[name]["skills"].append(skill_name.lower().strip())
        return list(clusters.values())
    except Exception as e:
        if conn: conn.close()
        print("Error loading clusters from DB:", e)
        return []

def get_resources_by_skill_ids_db(skill_ids: list):
    if not skill_ids:
        return []
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT r.resource_id, r.title, r.resource_type, r.topic, rsm.skill_id, r.url, r.platform, r.difficulty, r.duration_hours
                FROM resources r
                JOIN resource_skill_mapping rsm ON r.resource_id = rsm.resource_id
                WHERE rsm.skill_id IN ({placeholders})
            """, tuple(skill_ids))
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

def get_projects_by_skill_ids_db(skill_ids: list):
    if not skill_ids:
        return []
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT DISTINCT p.project_id, p.project_name, p.description, p.difficulty, p.skills_covered
                FROM projects p
                JOIN project_skill_mapping psm ON p.project_id = psm.project_id
                WHERE psm.skill_id IN ({placeholders})
            """, tuple(skill_ids))
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

def get_interview_questions_by_skill_ids_db(skill_ids: list):
    if not skill_ids:
        return []
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT DISTINCT q.question_id, q.question, q.answer, q.explanation, q.difficulty, q.category
                FROM interview_questions q
                JOIN interview_question_skill_mapping iqsm ON q.question_id = iqsm.question_id
                WHERE iqsm.skill_id IN ({placeholders})
            """, tuple(skill_ids))
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

def get_mcqs_by_skill_ids_db(skill_ids: list):
    if not skill_ids:
        return []
    try:
        from api.database_connector import get_db_connection
    except ImportError:
        return []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT DISTINCT m.mcq_id, m.question, m.options, m.correct_option, m.explanation
                FROM mcqs m
                JOIN mcq_skill_mapping msm ON m.mcq_id = msm.mcq_id
                WHERE msm.skill_id IN ({placeholders})
            """, tuple(skill_ids))
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
                    "question": r[1],
                    "options": opts,
                    "correct": r[3],
                    "explanation": r[4]
                })
            return res
        except Exception:
            if conn: conn.close()
    return []


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
    Generates a personalized, stage-by-stage study timeline dynamically tailored to the student's
    college year/qualification and specific missing skills.
    """
    meta = QUALIFICATION_META.get(qualification, {"urgency": "Medium", "weekly_hours": 15, "months": 12})
    months = meta["months"]
    weekly_hours = meta["weekly_hours"]
    urgency = meta["urgency"]
    
    # Apply Career Stage intelligence adjustments
    stage_eval = None
    if assessment_scores and "career_stage" in assessment_scores:
        stage_eval = assessment_scores["career_stage"]
        weekly_hours = stage_eval.get("recommended_hours_weekly", weekly_hours)
        if stage_eval.get("track_status") == "Needs Acceleration":
            weekly_hours = min(int(weekly_hours * 1.2), 45)
            urgency = "Critical (Needs Acceleration)"
            
    # Compress duration if student is a fresh passout looking for immediate jobs
    if fresh_passout:
        months = 3
        weekly_hours = max(weekly_hours * 1.5, 35)
        urgency = "Immediate / Fast-Track"

    # Determine preferred difficulty order based on qualification/level
    pref_diffs = ["Intermediate", "Advanced", "Easy", "Beginner"]
    if qualification in ("1st Year Student", "2nd Year Student"):
        pref_diffs = ["Easy", "Beginner", "Intermediate", "Advanced"]
    elif qualification in ("3rd Year Student", "Trainee Engineer"):
        pref_diffs = ["Intermediate", "Advanced", "Easy", "Beginner"]
    else:
        pref_diffs = ["Advanced", "Intermediate", "Easy", "Beginner"]

    # Fetch master list of skills
    skills_master = get_skills_master()
    skills_by_name = {s["name"].lower().strip(): s for s in skills_master}
    
    # Flatten missing skills with their priority
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
                # Fallback category mapping based on keywords
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

    def calculate_hours_needed(skills_list):
        hours = 0
        for s in skills_list:
            diff = s["difficulty"].lower()
            prio = s["priority"]
            if prio == "High":
                factor = 1.0
            elif prio == "Medium":
                factor = 0.75
            else:
                factor = 0.5
                
            if "advanced" in diff:
                base = 40
            elif "beginner" in diff:
                base = 20
            else:
                base = 30
            hours += base * factor
        return max(hours, 15)

    # Load skill clusters from database
    db_clusters = get_db_skill_clusters()
    
    # Fallback to local hardcoded clusters if DB is empty
    if not db_clusters:
        db_clusters = [
            {
                "id": "languages_foundations",
                "title": "Languages & Foundations",
                "skills": ["java", "python", "go", "c programming", "c++", "object oriented programming", "oop", "git & github"],
                "default_milestone": "Demonstrate language familiarity, OOP concepts, and basic git workspace setup."
            },
            {
                "id": "dsa_algorithms",
                "title": "Data Structures & Algorithms",
                "skills": ["dsa (combined)", "data structures", "algorithms"],
                "default_milestone": "Master time complexities and solve medium-level algorithmic challenges on array/linked lists/trees."
            },
            {
                "id": "databases_core_cs",
                "title": "Databases & Core CS",
                "skills": ["dbms", "sql", "mysql", "postgresql", "operating systems", "computer networks", "linux basics"],
                "default_milestone": "Design relational database schemas, write complex queries, and explain core OS/network protocols."
            },
            {
                "id": "backend_api_foundations",
                "title": "Backend API Foundations",
                "skills": ["spring boot", "rest apis", "nodejs"],
                "default_milestone": "Develop and deploy robust CRUD API endpoints with error handling and validations."
            },
            {
                "id": "distributed_systems_caching",
                "title": "Distributed Systems & Caching",
                "skills": ["redis", "kafka", "microservices", "docker", "message queues (kafka)", "aws basics", "kubernetes"],
                "default_milestone": "Configure Redis caches, process real-time Kafka event streams, and dockerize backend services."
            },
            {
                "id": "system_design_architecture",
                "title": "System Design & Architecture",
                "skills": ["system design", "low level design", "high level design"],
                "default_milestone": "Create low-level class structural models and high-level architectural designs for scaling traffic."
            }
        ]

    stages = []
    stage_idx = 1
    
    seen_skills = set()
    global_projects = []
    global_resources = []

    # Map missing skills into clusters
    for c in db_clusters:
        cluster_skills = []
        cluster_skill_ids = []
        for s in missing_with_meta:
            s_low = s["name"].lower().strip()
            # Match if skill name matches cluster skill list
            if s_low in c["skills"] and s_low not in seen_skills:
                cluster_skills.append(s)
                seen_skills.add(s_low)
                if s["id"] is not None:
                    cluster_skill_ids.append(s["id"])

        if cluster_skills:
            # Calculate duration
            hours = calculate_hours_needed(cluster_skills)
            weeks = max(round(hours / weekly_hours), 2)
            
            # Fetch resources
            db_res = get_resources_by_skill_ids_db(cluster_skill_ids)
            if db_res:
                db_res = sorted(db_res, key=lambda r: pref_diffs.index(r["difficulty"]) if r.get("difficulty") in pref_diffs else 999)

            videos = []
            materials = []
            for r in db_res:
                r_item = {
                    "title": r["title"],
                    "platform": r["platform"],
                    "type": r["type"],
                    "url": r["url"],
                    "topic": r["topic"],
                    "difficulty": r["difficulty"],
                    "duration_hours": r["duration_hours"],
                    "duration": f"{int(r['duration_hours'])} hrs"
                }
                if r["type"] in ("Video", "Playlist"):
                    videos.append(r_item)
                else:
                    materials.append(r_item)
                
                # Collect for overall recommendations
                global_resources.append({
                    "title": r["title"],
                    "platform": r["platform"],
                    "type": r["type"],
                    "url": r["url"],
                    "difficulty": r["difficulty"]
                })

            # Fetch project
            db_projs = get_projects_by_skill_ids_db(cluster_skill_ids)
            best_proj = None
            if db_projs:
                db_projs = sorted(db_projs, key=lambda p: pref_diffs.index(p["difficulty"]) if p.get("difficulty") in pref_diffs else 999)
                best_proj = db_projs[0]
                global_projects.append({
                    "name": best_proj["name"],
                    "difficulty": best_proj["difficulty"],
                    "details": best_proj["details"]
                })

            # Fetch MCQs
            db_mcqs = get_mcqs_by_skill_ids_db(cluster_skill_ids)

            # Fetch interview questions
            db_questions = get_interview_questions_by_skill_ids_db(cluster_skill_ids)

            focus = f"Acquire SDE competencies in: {', '.join([s['name'] for s in cluster_skills])}"
            if best_proj:
                focus += f". Recommended Project: {best_proj['name']}"

            learning_goals = [f"Understand core paradigms of {', '.join([s['name'] for s in cluster_skills])}."]
            for r in db_res[:2]:
                learning_goals.append(f"Learn {r['topic'] or 'Skill'}: {r['title']} ({r['platform']}) - {r['url']}")

            # Dynamic stage title reflecting covered skills
            skills_names = [s["name"] for s in cluster_skills]
            if len(skills_names) > 3:
                stage_skills_str = ", ".join(skills_names[:3]) + ", etc."
            else:
                stage_skills_str = ", ".join(skills_names)

            stages.append({
                "stage": stage_idx,
                "title": f"Stage {stage_idx}: {c['title']} ({stage_skills_str}) - {weeks} weeks",
                "duration_weeks": weeks,
                "focus": focus,
                "milestone": c.get("default_milestone", "Complete dynamic milestone checkpoints."),
                "learning_goals": learning_goals,
                "videos": videos[:3],
                "materials": materials[:3],
                "mcqs": db_mcqs[:3],
                "coding": {
                    "title": best_proj["name"] if best_proj else f"SDE Sandbox coding challenge for {c['title']}",
                    "desc": best_proj["details"] if best_proj else "Write and execute SDE modular test logic matching the topic.",
                    "template": "function solve() {\n    // write your logic here\n    return true;\n}"
                },
                "interview_questions": db_questions[:3]
            })
            stage_idx += 1

    # Add default "Interview Prep & Review" stage if not already present, or if stages list is empty
    if not stages or len(stages) < 3:
        # Create final interview prep stage
        duration_weeks = max(round(30 / weekly_hours), 2)
        stage_goals = [
            f"Solve {dream_company}-specific coding questions.",
            f"Prepare for {dream_company} core values and SDE behavioral questions.",
            "Conduct mock technical interview sessions."
        ]
        
        stages.append({
            "stage": stage_idx,
            "title": f"Stage {stage_idx}: SDE Placement Review & Mocks",
            "duration_weeks": duration_weeks,
            "focus": f"Final preparation targeting {dream_company} interview rounds.",
            "milestone": "Pass mock technical loops and finalize ATS-optimized resume.",
            "learning_goals": stage_goals,
            "videos": [
                { "title": "Cracking SDE Interview Coding Rounds", "duration": "40 mins", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/V8V_vH2Sj9w" },
                { "title": "STAR Behavioral Template for SDEs", "duration": "15 mins", "platform": "YouTube", "type": "Video", "url": "https://www.youtube.com/embed/w7mko_X4kO8" }
            ],
            "materials": [
                { "title": "Leetcode Prep Cheatsheet.md", "platform": "Markdown Guide", "type": "Documentation", "url": "#", "duration_hours": 2.0 },
                { "title": "STAR Method Guide.pdf", "platform": "PDF Resource", "type": "Article", "url": "#", "duration_hours": 1.0 }
            ],
            "mcqs": [
                {
                    "question": "In behavioral SDE rounds, what does the 'A' represent in the STAR template?",
                    "options": ["Assessment", "Allocation", "Action taken", "Algorithmic score"],
                    "correct": 2,
                    "explanation": "STAR stands for Situation, Task, Action, Result. The A represents Action taken."
                }
            ],
            "coding": {
                "title": "Two Sum Optimal O(N)",
                "desc": "Write a function twoSum(nums, target) returning indices of the two elements adding up to target in linear time complexity.",
                "template": """function twoSum(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (map.has(complement)) {
            return [map.get(complement), i];
        }
        map.set(nums[i], i);
    }
    return [];
}"""
            },
            "interview_questions": [
                { "question": "Explain CAP theorem and how it applies to databases.", "answer": "Consistency, Availability, Partition Tolerance - choose 2." }
            ]
        })

    # Overall timeline duration in months
    total_weeks = sum(s["duration_weeks"] for s in stages)
    months = max(round(total_weeks / 4.3), 1)

    # Fallbacks for overall projects recommendations
    if not global_projects:
        global_projects = [
            {
                "name": f"High-Concurrency {dream_company}-Style Delivery Engine",
                "difficulty": "Advanced",
                "details": f"Scalable order dispatching system using Go/Java, Redis for geo-indexing riders, and Kafka for real-time delivery status broadcasts."
            },
            {
                "name": "Distributed Shopping Cart Cache",
                "difficulty": "Intermediate",
                "details": "Cart session management system utilizing Redis clustered databases, ensuring <5ms latency under peak e-commerce search traffic."
            }
        ]

    # Fallbacks for overall resources recommendations
    if len(global_resources) < 3:
        global_resources = [
            {"title": "Striver's A2Z DSA Sheet", "platform": "TakeUForward", "type": "Practice", "url": "https://takeuforward.org"},
            {"title": f"{dream_company} Interview Experience Archives", "platform": "GeeksforGeeks", "type": "Mock Prep", "url": "https://geeksforgeeks.org"},
            {"title": "System Design Primer by Donne Martin", "platform": "GitHub", "type": "Documentation", "url": "https://github.com/donnemartin/system-design-primer"}
        ]

    # Format resources to match schema list structure
    if global_resources:
        global_resources = sorted(global_resources, key=lambda r: pref_diffs.index(r["difficulty"]) if r.get("difficulty") in pref_diffs else 999)
        formatted_resources = []
        seen_titles = set()
        for r in global_resources:
            title = r["title"]
            if title not in seen_titles:
                seen_titles.add(title)
                formatted_resources.append({
                    "title": r["title"],
                    "platform": r["platform"],
                    "type": r["type"],
                    "url": r["url"]
                })
        global_resources = formatted_resources[:4]

    return {
        "qualification": qualification,
        "months_remaining": months,
        "weekly_hours_recommended": weekly_hours,
        "urgency": urgency,
        "stages": stages,
        "projects": global_projects,
        "resources": global_resources
    }

