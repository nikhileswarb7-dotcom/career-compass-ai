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

def generate_timeline(
    qualification: str, 
    missing_skills: dict, 
    dream_company: str = "Blinkit", 
    dream_sector: str = "Quick-Commerce", 
    fresh_passout: bool = False, 
    target_role: str = "Junior Software Engineer",
    similar_engineers: list = None,
    assessment_scores: dict = None
) -> dict:
    """
    Generates a personalized, stage-by-stage study timeline tailored to the student's
    college year/qualification and specific missing skills.
    """
    meta = QUALIFICATION_META.get(qualification, {"urgency": "Medium", "weekly_hours": 15, "months": 12})
    months = meta["months"]
    weekly_hours = meta["weekly_hours"]
    urgency = meta["urgency"]
    
    # 1. Apply Career Stage intelligence adjustments
    stage_eval = None
    if assessment_scores and "career_stage" in assessment_scores:
        stage_eval = assessment_scores["career_stage"]
        # Use stage recommended hours as baseline
        weekly_hours = stage_eval.get("recommended_hours_weekly", weekly_hours)
        # If student track status is Needs Acceleration, scale prep intensity by 1.2x
        if stage_eval.get("track_status") == "Needs Acceleration":
            weekly_hours = min(int(weekly_hours * 1.2), 45)
            urgency = "Critical (Needs Acceleration)"
            
    # Compress duration if student is a fresh passout looking for immediate jobs
    if fresh_passout:
        months = 3
        weekly_hours = max(weekly_hours * 1.5, 35)
        urgency = "Immediate / Fast-Track"

    # Define skill categories for smart AI focus injections
    LANG_SKILLS = ["Java", "Go", "Python", "NodeJS", "Spring Boot"]
    DB_SKILLS = ["PostgreSQL", "MySQL", "Redis", "Kafka", "ElasticSearch"]
    SYS_SKILLS = ["System Design", "Distributed Systems", "Docker", "Kubernetes", "AWS", "gRPC", "Microservices"]

    def get_focus_phrase(skills_list):
        prio_missing = []
        for p in ["High", "Medium", "Low"]:
            prio_missing += [s for s in missing_skills.get(p, []) if s in skills_list]
        if prio_missing:
            return "Focus on closing skill gaps: " + ", ".join(prio_missing)
        return "Review advanced SDE patterns and optimizations"

    # 1. Try to load stages and duration dynamically from the PostgreSQL database
    db_roadmap = load_roadmap_from_db(qualification, dream_company, target_role)
    if db_roadmap:
        months = db_roadmap["months"]
        if fresh_passout:
            months = 3
        stages = []
        for s in db_roadmap["stages"]:
            # Inject dynamic skill focuses based on stage index/type
            stage_idx = s["stage"]
            focus_text = s["focus"]
            if stage_idx == 1:
                focus_text += f" {get_focus_phrase(LANG_SKILLS)}."
            elif stage_idx == 2:
                focus_text += f" {get_focus_phrase(DB_SKILLS)}."
            elif stage_idx == 3:
                focus_text += f" {get_focus_phrase(SYS_SKILLS)}."
            else:
                focus_text += f" {get_focus_phrase(LANG_SKILLS + DB_SKILLS + SYS_SKILLS)}."
                
            stages.append({
                "stage": s["stage"],
                "title": s["title"],
                "duration_weeks": s["duration_weeks"],
                "focus": focus_text,
                "milestone": s["milestone"],
                "learning_goals": list(s["learning_goals"]) if s["learning_goals"] else []
            })
    else:
        raise RuntimeError(f"Database roadmap unavailable or not seeded. Could not load SDE timeline for target: {dream_company} ({target_role})")

    # Recommended Projects based on Dream Sector and Missing Skills
    flat_missing = []
    for priority, skills in missing_skills.items():
        flat_missing += [s.lower() for s in skills]

    all_projects = load_dynamic_projects()
    projects = []
    
    if all_projects:
        # Score and sort projects
        scored_projects = []
        for p in all_projects:
            score = 0
            for s in p["skills"]:
                if s.lower() in flat_missing:
                    score += 2
            
            # Align project difficulty with candidate qualification/stage to personalize recommendations
            p_diff = p.get("difficulty", "Intermediate")
            if p_diff == "Easy":
                p_diff = "Beginner"
            if qualification in ["1st Year Student", "2nd Year Student"]:
                if p_diff == "Beginner":
                    score += 5
                elif p_diff == "Intermediate":
                    score += 0
                else:
                    score -= 5
            elif qualification in ["3rd Year Student", "4th Year Student", "Fresh Graduate"]:
                if p_diff == "Intermediate":
                    score += 5
                elif p_diff == "Advanced":
                    score += 2
                else:
                    score -= 2
            else: # Trainee or Junior SDE
                if p_diff == "Advanced":
                    score += 5
                elif p_diff == "Intermediate":
                    score += 2
                else:
                    score -= 5
                    
            # Add small weight for difficulty matches
            if urgency in ["Critical", "Immediate / Fast-Track"] and p["difficulty"] == "Advanced":
                score += 1
            scored_projects.append((score, p))
            
        scored_projects.sort(key=lambda x: x[0], reverse=True)
        projects = [{"name": p["name"], "difficulty": p["difficulty"], "details": p["details"]} for score, p in scored_projects[:2]]
        
    if not projects:
        if dream_sector.lower() in ["quick-commerce", "e-commerce"]:
            projects = [
                {
                    "name": f"High-Concurrency {dream_company}-Style Delivery Engine",
                    "difficulty": "Advanced" if not fresh_passout else "Intermediate",
                    "details": f"Scalable order dispatching system using Go/Java, Redis for geo-indexing riders, and Kafka for real-time delivery status broadcasts."
                },
                {
                    "name": "Distributed Shopping Cart Cache",
                    "difficulty": "Intermediate",
                    "details": "Cart session management system utilizing Redis clustered databases, ensuring <5ms latency under peak e-commerce search traffic."
                }
            ]
        elif dream_sector.lower() == "fintech":
            projects = [
                {
                    "name": "Idempotent Transaction Ledger API",
                    "difficulty": "Advanced",
                    "details": "Double-entry bookkeeping system with PostgreSQL transactions, Spring Boot, and Kafka logs to guarantee zero-data-loss payment operations."
                },
                {
                    "name": "Fraud Detection Pipeline",
                    "difficulty": "Intermediate",
                    "details": "Real-time payment event stream analyzer using Python, Apache Kafka, and a rule engine to block fraudulent checkouts instantly."
                }
            ]
        elif dream_sector.lower() == "saas":
            projects = [
                {
                    "name": "Multi-Tenant Event Logging Framework",
                    "difficulty": "Advanced",
                    "details": "SaaS metrics collection daemon written in Go, exposing gRPC endpoints and utilizing Elasticsearch to query system logs across tenants."
                },
                {
                    "name": "JWT-Based Role Based Access Control",
                    "difficulty": "Intermediate",
                    "details": "Secure authentication microservice with Node.js/TypeScript, Redis token revocation, and middleware security checks."
                }
            ]
        else: # Default Service-based/General SDE
            projects = [
                {
                    "name": "Distributed URL Shortener Service",
                    "difficulty": "Advanced",
                    "details": "Go & Redis backend with unique slug generation, rate limiting, and write-through cache architecture."
                },
                {
                    "name": "Collaborative Task Manager API",
                    "difficulty": "Intermediate",
                    "details": "REST API with WebSockets for real-time board updates, built using Express, PostgreSQL, and Docker containerization."
                }
            ]
            
    # Recommended Resources based on Target Company and Missing Skills
    all_resources = load_dynamic_resources()
    resources = []
    
    if all_resources:
        scored_resources = []
        for r in all_resources:
            score = 0
            if r["topic"].lower() in flat_missing:
                score += 2
            if r.get("title") and dream_company.lower() in r["title"].lower():
                score += 1
                
            # Align learning resource difficulty with candidate qualification/stage to personalize recommendations
            r_diff = r.get("difficulty", "Intermediate")
            if qualification in ["1st Year Student", "2nd Year Student"]:
                if r_diff == "Beginner":
                    score += 5
                elif r_diff == "Intermediate":
                    score += 2
                else:
                    score -= 5
            elif qualification in ["3rd Year Student", "4th Year Student", "Fresh Graduate"]:
                if r_diff == "Intermediate":
                    score += 5
                elif r_diff == "Advanced":
                    score += 2
                else:
                    score -= 2
            else: # Trainee or Junior SDE
                if r_diff == "Advanced":
                    score += 5
                elif r_diff == "Intermediate":
                    score += 2
                else:
                    score -= 5
                    
            scored_resources.append((score, r))
            
        scored_resources.sort(key=lambda x: x[0], reverse=True)
        resources = [{"title": r["title"], "platform": r["platform"], "type": r["type"], "url": r["url"]} for score, r in scored_resources[:3]]
        
    if len(resources) < 3:
        # Fallback/Append standard resources
        standard_res = [
            {"title": "Striver's A2Z DSA Sheet", "platform": "TakeUForward", "type": "Practice", "url": "https://takeuforward.org"},
            {"title": f"{dream_company} Interview Experience Archives", "platform": "GeeksforGeeks", "type": "Mock Prep", "url": "https://geeksforgeeks.org"},
            {"title": "System Design Primer by Donne Martin", "platform": "GitHub", "type": "Documentation", "url": "https://github.com/donnemartin/system-design-primer"}
        ]
        for sr in standard_res:
            if sr["title"] not in [r["title"] for r in resources]:
                resources.append(sr)
                
    if dream_company.lower() == "amazon" and "Amazon SDE Leadership Principles Prep" not in [r["title"] for r in resources]:
        resources.append({"title": "Amazon SDE Leadership Principles Prep", "platform": "Medium", "type": "Behavioral", "url": "https://medium.com"})
    elif dream_company.lower() in ["blinkit", "flipkart"] and "System Design of E-Commerce Quick-Commerce" not in [r["title"] for r in resources]:
        resources.append({"title": "System Design of E-Commerce Quick-Commerce", "platform": "YouTube", "type": "Video Guide", "url": "https://youtube.com"})
        
    resources = resources[:4]
    
    # Calculate missing skills frequencies if similar_engineers is provided
    missing_freqs = {}
    if similar_engineers:
        try:
            from ai_engine.similarity.career_path_analyzer import analyze_career_paths
            flat_missing = list(missing_skills.get("High", [])) + list(missing_skills.get("Medium", [])) + list(missing_skills.get("Low", []))
            paths_analysis = analyze_career_paths(similar_engineers, flat_missing)
            missing_freqs = paths_analysis.get("missing_skills_frequency", {})
        except Exception:
            pass

    def get_coach_explanation(stage_idx: int) -> str:
        # Determine relevant skills for this stage
        if stage_idx == 1:
            stage_skills = ["Java", "Go", "Python", "NodeJS", "Spring Boot"]
            default_gap = "Programming Foundations"
        elif stage_idx == 2:
            stage_skills = ["PostgreSQL", "MySQL", "Redis", "Kafka", "ElasticSearch", "SQL"]
            default_gap = "Databases & Caching"
        elif stage_idx == 3:
            stage_skills = ["System Design", "Distributed Systems", "Docker", "Kubernetes", "AWS", "gRPC", "Microservices", "Low Level Design", "High Level Design"]
            default_gap = "System Design"
        else:
            stage_skills = ["DSA (Combined)", "Object Oriented Programming", "REST APIs"]
            default_gap = "DSA & Algorithms"

        # Find if any of these are in the student's missing skills
        matched_gap = None
        for skill in stage_skills:
            for cat in ["High", "Medium", "Low"]:
                if skill.lower() in [s.lower() for s in missing_skills.get(cat, [])]:
                    matched_gap = skill
                    break
            if matched_gap:
                break

        if matched_gap:
            freq = missing_freqs.get(matched_gap, 0.0)
            impact = "High" if matched_gap in missing_skills.get("High", []) else ("Medium" if matched_gap in missing_skills.get("Medium", []) else "Low")
            if freq > 0:
                why = f"{int(freq * 100)}% of matched SDE peers at {dream_company} mastered this"
            else:
                why = f"Core prerequisite matching target role specifications"
            return f" (Coach Coach-Explanation: Why: {why} | Addresses Gap: {matched_gap} | Expected Impact: {impact})"
        else:
            return f" (Coach Coach-Explanation: Why: Reinforces core engineering competency | Addresses Gap: {default_gap} (Review) | Expected Impact: Medium)"

    # Inject learning resources and annotate stages with coach-explanations
    for s in stages:
        stage_idx = s.get("stage", 1)
        s["focus"] = s.get("focus", "") + get_coach_explanation(stage_idx)
        
        # Inject Gap-Based dynamic learning resources
        if stage_idx == 1:
            stage_skills = ["Java", "Go", "Python", "NodeJS", "Spring Boot"]
        elif stage_idx == 2:
            stage_skills = ["PostgreSQL", "MySQL", "Redis", "Kafka", "ElasticSearch", "SQL"]
        elif stage_idx == 3:
            stage_skills = ["System Design", "Distributed Systems", "Docker", "Kubernetes", "AWS", "gRPC", "Microservices", "Low Level Design", "High Level Design"]
        else:
            stage_skills = ["DSA (Combined)", "Object Oriented Programming", "REST APIs"]
            
        stage_gaps = []
        for skill in stage_skills:
            for cat in ["High", "Medium", "Low"]:
                if skill.lower() in [ms.lower() for ms in missing_skills.get(cat, [])]:
                    stage_gaps.append(skill)
                    
        # Match resources for these stage gaps
        if stage_gaps and all_resources:
            stage_resources = []
            for r in all_resources:
                topic = r.get("topic") or ""
                title = r.get("title") or ""
                if topic.lower().strip() in {sg.lower().strip() for sg in stage_gaps}:
                    res_str = f"Learn {topic}: {r.get('title')} ({r.get('platform')})"
                    if res_str not in stage_resources:
                        stage_resources.append(res_str)
            
            # Append resources to the learning_goals list
            if "learning_goals" not in s or not isinstance(s["learning_goals"], list):
                s["learning_goals"] = []
            s["learning_goals"].extend(stage_resources[:2])

    return {
        "qualification": qualification,
        "months_remaining": months,
        "weekly_hours_recommended": weekly_hours,
        "urgency": urgency,
        "stages": stages,
        "projects": projects,
        "resources": resources
    }
