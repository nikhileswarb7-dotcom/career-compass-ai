import os
import csv
import json
import random

# Set random seed for reproducibility
random.seed(42)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

INDUSTRY_DIR = os.path.join(DB_DIR, "industry_layer")
CAREER_DIR = os.path.join(DB_DIR, "career_layer")
HIRING_DIR = os.path.join(DB_DIR, "hiring_layer")
LEARNING_DIR = os.path.join(DB_DIR, "learning_layer")

def write_csv(filepath, headers, rows):
    with open(filepath, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Written {len(rows)} rows to {os.path.basename(filepath)}")

# ====================================================================
# 1. stage_assessments.csv Fix
# ====================================================================
def fix_stage_assessments():
    json_path = os.path.join(LEARNING_DIR, "stage_assessments.json")
    csv_path = os.path.join(LEARNING_DIR, "stage_assessments.csv")
    
    with open(json_path, "r", encoding="utf-8") as f:
        stages = json.load(f)
        
    rows = []
    for stage in stages:
        rows.append({
            "stage_id": stage["stage_id"],
            "mcqs": json.dumps(stage["mcqs"]),
            "coding_challenge": json.dumps(stage["coding_challenge"])
        })
        
    write_csv(csv_path, ["stage_id", "mcqs", "coding_challenge"], rows)

# ====================================================================
# Helper function to classify role names dynamically to skills
# ====================================================================
def get_skills_for_role_name(role_name: str) -> list:
    name_low = role_name.lower()
    if any(k in name_low for k in ["devops", "sre", "cloud", "reliability", "infrastructure"]):
        return [1, 3, 7, 8, 13, 14, 24, 25, 26, 6]
    elif any(k in name_low for k in ["frontend", "ui", "ux", "design"]):
        return [12, 19, 20, 21, 7, 13, 25, 26, 3, 6]
    elif any(k in name_low for k in ["mobile", "android", "ios", "flutter", "native"]):
        return [2, 3, 22, 23, 7, 13, 25, 26, 6]
    elif any(k in name_low for k in ["ai", "ml", "machine", "deep", "nlp", "vision", "scientist", "analyst", "data"]):
        return [3, 17, 25, 26, 1, 6, 7, 13, 14, 15]
    elif "security" in name_low:
        return [1, 3, 7, 8, 13, 24, 25, 26, 6]
    else:
        return [2, 1, 3, 4, 5, 6, 9, 10, 11, 12, 13, 15, 16, 17, 18, 25, 26]

# ====================================================================
# 2. employee_skills.csv Expansion
# ====================================================================
def expand_employee_skills():
    profiles_path = os.path.join(INDUSTRY_DIR, "employee_profiles.csv")
    skills_path = os.path.join(INDUSTRY_DIR, "employee_skills.csv")
    roles_path = os.path.join(INDUSTRY_DIR, "roles.csv")
    
    roles_map = {}
    with open(roles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            roles_map[int(r["role_id"])] = r["role_name"]
            
    all_skills = list(range(1, 27))
    rows = []
    
    with open(profiles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for profile in reader:
            p_id = int(profile["profile_id"])
            role_id = int(profile["role_id"]) if profile["role_id"] else 1
            role_name = roles_map.get(role_id, "Software Development Engineer (SDE)")
            
            pool = get_skills_for_role_name(role_name)
            num_skills = random.randint(8, 15)
            
            selected = list(pool)
            while len(selected) < num_skills:
                extra = random.choice(all_skills)
                if extra not in selected:
                    selected.append(extra)
            selected = random.sample(selected, num_skills)
            
            for s_id in selected:
                rows.append({
                    "profile_id": p_id,
                    "skill_id": s_id
                })
                
    write_csv(skills_path, ["profile_id", "skill_id"], rows)

# ====================================================================
# 3. role_skill_requirements.csv Expansion
# ====================================================================
def expand_role_skill_requirements():
    csv_path = os.path.join(CAREER_DIR, "role_skill_requirements.csv")
    roles_path = os.path.join(INDUSTRY_DIR, "roles.csv")
    
    roles = []
    with open(roles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            roles.append((int(r["role_id"]), r["role_name"]))
            
    rows = []
    rs_id = 1
    
    for role_id, role_name in roles:
        skills = get_skills_for_role_name(role_name)
        for s_idx, s_id in enumerate(skills):
            if s_idx < len(skills) // 3:
                priority = "High"
            elif s_idx < 2 * len(skills) // 3:
                priority = "Medium"
            else:
                priority = "Low"
                
            rows.append({
                "role_skill_id": rs_id,
                "company_role_id": role_id,
                "skill_id": s_id,
                "priority": priority
            })
            rs_id += 1
            
    write_csv(csv_path, ["role_skill_id", "company_role_id", "skill_id", "priority"], rows)

# ====================================================================
# 4. company_interview_patterns.csv Expansion
# ====================================================================
def expand_company_interview_patterns():
    csv_path = os.path.join(HIRING_DIR, "company_interview_patterns.csv")
    companies_path = os.path.join(INDUSTRY_DIR, "companies.csv")
    roles_path = os.path.join(INDUSTRY_DIR, "roles.csv")
    
    companies = []
    with open(companies_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            companies.append((int(r["company_id"]), r["company_name"]))
            
    roles_map = {}
    with open(roles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            roles_map[int(r["role_id"])] = r["role_name"]
            
    interview_topics = ["DSA", "System Design", "Database Design", "Concurrency", "OOP", "Caching", "Queues", "Leadership Principles"]
    
    rows = []
    pattern_id = 1
    
    for comp_id, comp_name in companies:
        available_role_ids = list(roles_map.keys())
        roles_to_generate = random.sample(available_role_ids, k=random.randint(2, 3))
        for role_id in roles_to_generate:
            role_name = roles_map[role_id]
            rounds = random.randint(3, 6)
            diff = random.randint(5, 9)
            
            topics = random.sample(interview_topics, k=random.randint(2, 3))
            topics_str = " and ".join(topics)
            
            notes = f"{comp_name} {role_name} interview process covers {topics_str}. Candidates are evaluated on real-world problem solving."
            
            rows.append({
                "pattern_id": pattern_id,
                "company_id": comp_id,
                "role_id": role_id,
                "typical_rounds_count": rounds,
                "difficulty_rating": diff,
                "notes": notes
            })
            pattern_id += 1
            
    write_csv(csv_path, ["pattern_id", "company_id", "role_id", "typical_rounds_count", "difficulty_rating", "notes"], rows)

# ====================================================================
# 5. roadmap_templates.csv Expansion
# ====================================================================
def expand_roadmap_templates():
    csv_path = os.path.join(LEARNING_DIR, "roadmap_templates.csv")
    roles_path = os.path.join(INDUSTRY_DIR, "roles.csv")
    
    qualifications = [
        (1, 48, "1st Year Student"),
        (2, 36, "2nd Year Student"),
        (3, 18, "3rd Year Student"),
        (4, 6, "4th Year Student"),
        (5, 6, "Fresh Graduate"),
        (6, 9, "Trainee Engineer"),
        (7, 12, "Junior Software Engineer")
    ]
    
    roles = []
    with open(roles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            roles.append((int(r["role_id"]), r["role_name"]))
            
    rows = []
    template_id = 1
    
    for qual_id, duration, qual_name in qualifications:
        for role_id, role_name in roles:
            overview = f"{qual_name} custom roadmap template targeting {role_name} over {duration} months. Covers essential programming, specialization skills, system design, and placement prep milestones."
            rows.append({
                "template_id": template_id,
                "qualification_id": qual_id,
                "role_id": role_id,
                "total_duration_months": duration,
                "overview": overview
            })
            template_id += 1
            
    write_csv(csv_path, ["template_id", "qualification_id", "role_id", "total_duration_months", "overview"], rows)

def main():
    print("Starting dataset expansion and CSV fixes...")
    print("=" * 60)
    fix_stage_assessments()
    expand_employee_skills()
    expand_role_skill_requirements()
    expand_company_interview_patterns()
    expand_roadmap_templates()
    print("=" * 60)
    print("All datasets expanded and CSV files fixed successfully!")

if __name__ == "__main__":
    main()
