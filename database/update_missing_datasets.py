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
# 2. employee_skills.csv Expansion
# ====================================================================
def expand_employee_skills():
    profiles_path = os.path.join(INDUSTRY_DIR, "employee_profiles.csv")
    skills_path = os.path.join(INDUSTRY_DIR, "employee_skills.csv")
    roles_path = os.path.join(INDUSTRY_DIR, "roles.csv")
    
    # Load roles map to find role names
    roles_map = {}
    with open(roles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            roles_map[int(r["role_id"])] = r["role_name"]
            
    # Define role-specific skill pools from skills_master (IDs 1-26)
    role_skills_map = {
        "SDE Intern": [1, 2, 3, 6, 7, 25, 26],
        "SDE I": [1, 2, 3, 6, 7, 13, 25, 26, 10, 16],
        "SDE II": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 25, 26],
        "SDE III": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 25, 26],
        "Senior Software Engineer": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 25, 26],
        "Tech Lead": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 24, 25, 26],
        "Engineering Manager": [1, 2, 3, 4, 5, 6, 7, 8, 10, 13, 24, 25, 26],
        "Backend Engineer": [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 15, 16, 17, 18, 25, 26],
        "Frontend Engineer": [12, 19, 20, 21, 7, 13, 25, 26, 3, 6],
        "SRE / DevOps Engineer": [1, 3, 7, 8, 13, 14, 24, 25, 26, 6],
        "Mobile Engineer": [2, 3, 22, 23, 7, 13, 25, 26, 6],
        "AI / ML Engineer": [3, 17, 25, 26, 1, 6, 7, 13, 14, 15]
    }
    
    all_skills = list(range(1, 27))
    rows = []
    
    with open(profiles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for profile in reader:
            p_id = int(profile["profile_id"])
            role_id = int(profile["role_id"]) if profile["role_id"] else 2
            role_name = roles_map.get(role_id, "SDE I")
            
            # Pool skills
            pool = role_skills_map.get(role_name, [1, 2, 3, 6, 25, 26])
            
            # Determine number of skills (8-15)
            num_skills = random.randint(8, 15)
            
            # Ensure unique selection by mixing with general skills
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
    
    role_skills_matrix = {
        1: [2, 1, 6, 7, 25, 26, 3, 16], # SDE Intern
        2: [2, 1, 6, 7, 13, 25, 26, 10, 16, 3], # SDE I
        3: [2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 13, 25, 26, 17], # SDE II
        4: [2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 25, 26], # SDE III
        5: [2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 25, 26], # Senior SDE
        6: [2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 24, 25, 26], # Tech Lead
        7: [2, 1, 4, 5, 6, 7, 8, 10, 13, 24, 25, 26], # Engineering Manager
        8: [2, 1, 3, 4, 5, 6, 9, 10, 11, 12, 13, 15, 16, 17, 18, 25, 26], # Backend Engineer
        9: [12, 19, 20, 21, 7, 13, 25, 26, 3, 6], # Frontend Engineer
        10: [1, 3, 7, 8, 13, 14, 24, 25, 26, 6], # SRE / DevOps Engineer
        11: [2, 3, 22, 23, 7, 13, 25, 26, 6], # Mobile Engineer
        12: [3, 17, 25, 26, 1, 6, 7, 13, 14, 15] # AI / ML Engineer
    }
    
    rows = []
    rs_id = 1
    
    # Map each company_role_id (1 to 12) to relevant skills
    for company_role_id, skills in role_skills_matrix.items():
        for s_idx, s_id in enumerate(skills):
            # First few skills are High priority, middle are Medium, rest are Low
            if s_idx < len(skills) // 3:
                priority = "High"
            elif s_idx < 2 * len(skills) // 3:
                priority = "Medium"
            else:
                priority = "Low"
                
            rows.append({
                "role_skill_id": rs_id,
                "company_role_id": company_role_id,
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
    
    # Load companies from companies.csv
    companies = []
    with open(companies_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            companies.append((int(r["company_id"]), r["company_name"]))
            
    # Target Roles (IDs: 1 = Intern, 2 = SDE I, 3 = SDE II, 8 = Backend, 9 = Frontend)
    target_roles = [
        (1, "Intern", 3, 5),
        (2, "SDE I", 4, 7),
        (3, "SDE II", 5, 9),
        (8, "Backend Engineer", 4, 8),
        (9, "Frontend Engineer", 4, 8)
    ]
    
    interview_topics = ["DSA", "System Design", "Database Design", "Concurrency", "OOP", "Caching", "Queues", "Leadership Principles"]
    
    rows = []
    pattern_id = 1
    
    # Generate patterns combining companies and target roles
    for comp_id, comp_name in companies:
        # Each company gets 2 to 3 role pattern profiles
        roles_to_generate = random.sample(target_roles, k=random.randint(2, 3))
        for role_id, role_name, base_rounds, base_diff in roles_to_generate:
            rounds = base_rounds + random.choice([-1, 0, 1])
            diff = base_diff + random.choice([-1, 0, 1])
            diff = max(1, min(10, diff))
            
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
    
    # Qualifications mapping
    qualifications = [
        (1, 48, "1st Year Student"),
        (2, 36, "2nd Year Student"),
        (3, 18, "3rd Year Student"),
        (4, 6, "4th Year Student"),
        (5, 6, "Fresh Graduate"),
        (6, 9, "Trainee Engineer"),
        (7, 12, "Junior Software Engineer")
    ]
    
    # SDE Roles
    roles = [
        (2, "SDE I"),
        (8, "Backend Engineer"),
        (9, "Frontend Engineer"),
        (10, "SRE / DevOps Engineer"),
        (11, "Mobile Engineer"),
        (12, "AI / ML Engineer")
    ]
    
    rows = []
    template_id = 1
    
    # Map all combinations
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
