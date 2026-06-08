import os
import csv
import random
import re

# ----------------------------------------------------------------
# Configurations & Paths
# ----------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

# Subdirectories for layers
INDUSTRY_DIR = os.path.join(DB_DIR, "industry_layer")
CAREER_DIR = os.path.join(DB_DIR, "career_layer")
HIRING_DIR = os.path.join(DB_DIR, "hiring_layer")
LEARNING_DIR = os.path.join(DB_DIR, "learning_layer")
STUDENT_DIR = os.path.join(DB_DIR, "student_layer")

# Ensure all directories exist
for d in [INDUSTRY_DIR, CAREER_DIR, HIRING_DIR, LEARNING_DIR, STUDENT_DIR]:
    os.makedirs(d, exist_ok=True)

# ----------------------------------------------------------------
# Constants & Seed Lists for Generation
# ----------------------------------------------------------------
FIRST_NAMES = [
    "Amit", "Rahul", "Sneha", "Priyank", "Sathish", "Taitiksh", "Ashok", "Divya", "Satyam", "Syed",
    "Vineela", "Nishitha", "Revant", "Srishti", "Srilekha", "Nizam", "Akhil", "Apoorv", "Paidipala", "Utkarsh",
    "Pranav", "Anjali", "Karan", "Pooja", "Vikram", "Rohan", "Neha", "Manish", "Deepak", "Aayush",
    "Aditya", "Ishita", "Siddharth", "Gaurav", "Swati", "Rajat", "Megha", "Shubham", "Tanvi", "Abhishek",
    "Harsha", "Sai", "Teja", "Krishna", "Venkatesh", "Ram", "Sita", "Kavya", "Arjun", "Kunal"
]

LAST_NAMES = [
    "Sharma", "Patel", "Reddy", "Mehta", "Bijjam", "Verma", "Zaidi", "Tiwari", "Ranjan", "Mohammed",
    "Singh", "Garg", "Supraja", "Pandey", "Joshi", "Gupta", "Kumar", "Iyer", "Nair", "Rao",
    "Choudhury", "Bose", "Sen", "Das", "Mishra", "Dubey", "Dwivedi", "Saxena", "Deshmukh", "Patil",
    "Jadhav", "Kulkarni", "Shetty", "Pillai", "Menon", "Prasad", "Sinha", "Mundhra", "Goel", "Bansal",
    "Agarwal", "Jain", "Shah", "Kaur", "Gill", "Bhat", "Dhar", "Rathore", "Solanki", "Yadav"
]

COLLEGES = [
    "IIT Kharagpur", "IIT Bombay", "IIT Delhi", "IIT Roorkee", "IIT Ropar", "IIT Bhilai", "IIT BHU",
    "IIIT Allahabad", "IIIT Kota", "IIIT Sri City", "IIIT Delhi", "IIIT Guwahati", "IIIT Dharwad", "IIIT Gwalior",
    "NIT Trichy", "NIT Surathkal", "NIT Warangal", "NIT Calicut", "NIT Rourkela", "NIT Kurukshetra",
    "VIT Vellore", "BITS Pilani", "Delhi Technological University", "College of Engineering Pune",
    "Netaji Subhash Engineering College", "Techno India University", "BMS Institute of Technology",
    "PES University", "SRM University", "KIET Group of Institutions", "Amity School of Engineering"
]

DEGREES = ["BTech", "MTech", "MCA", "BE", "Dual Degree"]
FIELDS = ["Computer Science", "Information Technology", "Computer Engineering", "Mathematics and Computing", "Software Engineering", "Computer Applications"]

COMPANIES = [
    # target company
    ("Blinkit", "E-Commerce", "Product"),
    # product companies
    ("Zomato", "FoodTech", "Product"),
    ("Swiggy", "FoodTech", "Product"),
    ("Paytm", "FinTech", "Product"),
    ("PhonePe", "FinTech", "Product"),
    ("Flipkart", "E-Commerce", "Product"),
    ("Amazon", "E-Commerce", "MNC"),
    ("Google", "Technology", "MNC"),
    ("Microsoft", "Technology", "MNC"),
    ("Meta", "SocialMedia", "MNC"),
    # startups
    ("Pocket FM", "MediaTech", "Startup"),
    ("Probo", "GamingTech", "Startup"),
    ("e3NexT Solutions", "IT Services", "Startup"),
    ("Rippling", "HRTech", "Startup"),
    ("Alltius", "AI/ML", "Startup"),
    ("FRND", "SocialTech", "Startup"),
    ("FinRep AI", "AI/ML", "Startup"),
    ("Toddle", "EdTech", "Startup"),
    # service companies / MNCs
    ("TCS", "IT Services", "MNC"),
    ("Wipro", "IT Services", "MNC"),
    ("Accenture", "IT Services", "MNC"),
    ("Cognizant", "IT Services", "MNC"),
    ("Infosys", "IT Services", "MNC")
]

SKILLS_MASTER = [
    (1, "Go", "Programming", "Intermediate"),
    (2, "Java", "Programming", "Intermediate"),
    (3, "Python", "Programming", "Beginner"),
    (4, "Kafka", "Backend", "Advanced"),
    (5, "Redis", "Backend", "Intermediate"),
    (6, "PostgreSQL", "Database", "Intermediate"),
    (7, "Docker", "DevOps", "Intermediate"),
    (8, "Kubernetes", "DevOps", "Advanced"),
    (9, "gRPC", "Backend", "Advanced"),
    (10, "Microservices", "Backend", "Advanced"),
    (11, "Spring Boot", "Backend", "Intermediate"),
    (12, "NodeJS", "Backend", "Intermediate"),
    (13, "AWS", "Cloud", "Intermediate"),
    (14, "GCP", "Cloud", "Intermediate"),
    (15, "DynamoDB", "Database", "Intermediate"),
    (16, "MySQL", "Database", "Intermediate"),
    (17, "ElasticSearch", "Database", "Advanced"),
    (18, "Django", "Backend", "Intermediate"),
    (19, "React", "Frontend", "Intermediate"),
    (20, "TypeScript", "Frontend", "Intermediate"),
    (21, "NextJS", "Frontend", "Advanced"),
    (22, "Kotlin", "Programming", "Intermediate"),
    (23, "Android", "Mobile", "Intermediate"),
    (24, "SRE", "DevOps", "Advanced"),
    (25, "System Design", "System Design", "Advanced"),
    (26, "Distributed Systems", "System Design", "Advanced")
]

# ----------------------------------------------------------------
# Main Generation Function
# ----------------------------------------------------------------
def generate_all_datasets():
    print("Generating thousands of records for CareerCompass AI...")
    
    # 1. Generate companies.csv
    companies_data = []
    company_map = {}
    for idx, (name, ind, ctype) in enumerate(COMPANIES):
        comp_id = idx + 1
        companies_data.append({
            "company_id": comp_id,
            "company_name": name,
            "industry": ind,
            "company_type": ctype
        })
        company_map[name] = comp_id
        
    # Write companies
    write_csv(os.path.join(INDUSTRY_DIR, "companies.csv"), 
              ["company_id", "company_name", "industry", "company_type"], 
              companies_data)

    # 2. Generate skills_master.csv
    skills_data = []
    for s_id, s_name, cat, diff in SKILLS_MASTER:
        skills_data.append({
            "skill_id": s_id,
            "skill_name": s_name
        })
    write_csv(os.path.join(CAREER_DIR, "skills_master.csv"), 
              ["skill_id", "skill_name"], 
              skills_data)

    # 3. Generate role_skill_requirements.csv (Blinkit SDE SDE-1, SDE-2 weights)
    # Blinkit SDE role company_role_id = 1
    role_skills = [
        (1, 1, 2, "High"),  # Java
        (2, 1, 1, "High"),  # Go
        (3, 1, 4, "High"),  # Kafka
        (4, 1, 5, "High"),  # Redis
        (5, 1, 6, "High"),  # PostgreSQL
        (6, 1, 10, "High"), # Microservices
        (7, 1, 11, "High"), # Spring Boot
        (8, 1, 25, "High"), # System Design
        (9, 1, 26, "High"), # Distributed Systems
        (10, 1, 3, "Medium"), # Python
        (11, 1, 7, "Medium"), # Docker
        (12, 1, 13, "Medium"), # AWS
        (13, 1, 16, "Medium"), # MySQL
        (14, 1, 17, "Medium"), # ElasticSearch
        (15, 1, 8, "Low"),   # Kubernetes
        (16, 1, 9, "Low"),   # gRPC
        (17, 1, 12, "Low")   # NodeJS
    ]
    write_csv(os.path.join(CAREER_DIR, "role_skill_requirements.csv"),
              ["role_skill_id", "company_role_id", "skill_id", "priority"],
              [{"role_skill_id": rs[0], "company_role_id": rs[1], "skill_id": rs[2], "priority": rs[3]} for rs in role_skills])

    # 4. Generate employee_profiles.csv & education_profiles.csv & employee_skills.csv & career_transitions.csv & role_specializations.csv
    employee_profiles = []
    education_profiles = []
    employee_skills = []
    career_transitions = []
    
    role_specializations = [
        {"role_id": 1, "role_name": "SDE Intern", "career_level": "Intern"},
        {"role_id": 2, "role_name": "SDE I", "career_level": "Entry"},
        {"role_id": 3, "role_name": "SDE II", "career_level": "Mid"},
        {"role_id": 4, "role_name": "SDE III", "career_level": "Senior"},
        {"role_id": 5, "role_name": "Senior Software Engineer", "career_level": "Senior"},
        {"role_id": 6, "role_name": "Tech Lead", "career_level": "Lead"},
        {"role_id": 7, "role_name": "Engineering Manager", "career_level": "Management"},
        {"role_id": 8, "role_name": "Backend Engineer", "career_level": "Mid"},
        {"role_id": 9, "role_name": "Frontend Engineer", "career_level": "Mid"},
        {"role_id": 10, "role_name": "SRE / DevOps Engineer", "career_level": "Mid"},
        {"role_id": 11, "role_name": "Mobile Engineer", "career_level": "Mid"},
        {"role_id": 12, "role_name": "AI / ML Engineer", "career_level": "Mid"}
    ]
    
    num_profiles = 1200 # Generating 1200 realistic SDE profiles!
    
    next_education_id = 1
    next_transition_id = 1
    
    # Generate unique names
    generated_names = set()
    while len(generated_names) < num_profiles:
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        generated_names.add(f"{fn} {ln}")
    generated_names = list(generated_names)

    # Predefined specializations mapping (kept for mapping skills based on random choice)
    specialization_options = [
        ("Backend Engineer", "Software Development"),
        ("Backend Engineer", "Distributed Systems"),
        ("SRE / DevOps Engineer", "SRE"),
        ("Frontend Engineer", "Web Development"),
        ("Mobile Engineer", "Android Development"),
        ("AI / ML Engineer", "Generative AI")
    ]
    
    # Career paths categories
    career_path_categories = [
        "Startup->Blinkit", "ProductCompany->Blinkit", "Amazon->Blinkit", "Flipkart->Blinkit",
        "Jio->Blinkit", "PocketFM->Blinkit", "Campus->Blinkit", "Intern->SDE1->SDE2"
    ]
    
    for i in range(num_profiles):
        profile_id = i + 1
        name = generated_names[i]
        
        # Experiences
        exp_years = round(random.uniform(0.5, 12.0), 1)
        
        # Decide college and degree
        college = random.choice(COLLEGES)
        degree = random.choice(DEGREES)
        field = random.choice(FIELDS)
        
        # Current company
        # 80% of profiles are at Blinkit, rest at Amazon/Microsoft/etc. to simulate real market data
        current_comp = "Blinkit" if random.random() < 0.85 else random.choice(["Amazon", "Microsoft", "Zomato", "Google"])
        
        # Determine previous company
        if exp_years < 1.5:
            prev_comp = ""
            c_path = "Intern->SDE1->SDE2" if random.random() < 0.4 else f"Campus->{current_comp}"
        else:
            prev_comps = [c[0] for c in COMPANIES if c[0] != current_comp]
            prev_comp = random.choice(prev_comps)
            c_path = f"{prev_comp}->{current_comp}"
            
        # Role titles and role_id mapping
        if exp_years < 1.0:
            role_id = 1 # SDE Intern
        elif exp_years < 2.0:
            role_id = 2 # SDE I
        elif exp_years < 5.0:
            role_id = 3 # SDE II
        elif exp_years < 8.0:
            role_id = 4 # SDE III
        else:
            role_id = random.choice([5, 6, 7]) # Senior SDE, Tech Lead, Engineering Manager
            
        employee_profiles.append({
            "profile_id": profile_id,
            "name": name,
            "role_id": role_id,
            "current_company": current_comp,
            "experience_years": exp_years,
            "college": college,
            "degree": degree,
            "previous_company": prev_comp,
            "career_path": c_path
        })
        
        # Add Education (1 to 2 entries, e.g. BTech + High School, or BTech + MTech)
        education_profiles.append({
            "education_id": next_education_id,
            "profile_id": profile_id,
            "college": college,
            "degree": degree,
            "field": field
        })
        next_education_id += 1
        
        if random.random() < 0.3: # 30% have high school or previous degree
            education_profiles.append({
                "education_id": next_education_id,
                "profile_id": profile_id,
                "college": f"School in {random.choice(['Delhi', 'Hyderabad', 'Bengaluru', 'Mumbai'])}",
                "degree": "High School",
                "field": "General Science"
            })
            next_education_id += 1

        # Determine skill selection based on a random spec choice
        spec, dom = random.choice(specialization_options)
        
        # Add Transitions
        if prev_comp:
            source_c_id = company_map.get(prev_comp, 1)
            target_c_id = company_map.get(current_comp, 1)
            career_transitions.append({
                "transition_id": next_transition_id,
                "profile_id": profile_id,
                "source_company_id": source_c_id,
                "target_company_id": target_c_id
            })
            next_transition_id += 1
            
            # 30% have an older transition
            if exp_years > 5.0:
                old_comp = random.choice([c[0] for c in COMPANIES if c[0] not in [current_comp, prev_comp]])
                old_c_id = company_map.get(old_comp, 1)
                career_transitions.append({
                    "transition_id": next_transition_id,
                    "profile_id": profile_id,
                    "source_company_id": old_c_id,
                    "target_company_id": source_c_id
                })
                next_transition_id += 1
                
        # Add Skills mapping (randomly pick 4-8 matching skills based on specialization)
        # SDEs always have Java/Go + DSA/System Design
        core_skills = [2, 1, 25, 26, 6] # Java, Go, System Design, Distributed Systems, PostgreSQL
        spec_skills_map = {
            "Backend Engineer": [4, 5, 10, 11, 13, 16], # Kafka, Redis, Microservices, Spring Boot, AWS, MySQL
            "SRE / DevOps Engineer": [7, 8, 13, 14, 24], # Docker, Kubernetes, AWS, GCP, SRE
            "Frontend Engineer": [12, 19, 20, 21], # NodeJS, React, TypeScript, NextJS
            "Mobile Engineer": [22, 23], # Kotlin, Android
            "AI / ML Engineer": [3, 17] # Python, ElasticSearch
        }
        
        # Choose 3 from core
        selected_skills = random.sample(core_skills, k=3)
        # Choose 2-4 from spec
        spec_pool = spec_skills_map.get(spec, [3, 12])
        selected_skills += random.sample(spec_pool, k=min(len(spec_pool), random.randint(2, 4)))
        
        for s_id in selected_skills:
            employee_skills.append({
                "profile_id": profile_id,
                "skill_id": s_id
            })

    # Write industry layer CSVs
    write_csv(os.path.join(INDUSTRY_DIR, "employee_profiles.csv"), 
              ["profile_id", "name", "role_id", "current_company", "experience_years", "college", "degree", "previous_company", "career_path"], 
              employee_profiles)
              
    write_csv(os.path.join(INDUSTRY_DIR, "education_profiles.csv"), 
              ["education_id", "profile_id", "college", "degree", "field"], 
              education_profiles)
              
    write_csv(os.path.join(INDUSTRY_DIR, "employee_skills.csv"), 
              ["profile_id", "skill_id"], 
              employee_skills)
              
    write_csv(os.path.join(INDUSTRY_DIR, "career_transitions.csv"), 
              ["transition_id", "profile_id", "source_company_id", "target_company_id"], 
              career_transitions)
              
    write_csv(os.path.join(INDUSTRY_DIR, "role_specializations.csv"), 
              ["role_id", "role_name", "career_level"], 
              role_specializations)

    # 5. Generate career_patterns.csv
    # Count frequencies of career paths
    path_counts = {}
    for p in employee_profiles:
        cp = p["career_path"]
        path_counts[cp] = path_counts.get(cp, 0) + 1
        
    career_patterns = []
    pattern_id = 1
    for path, count in sorted(path_counts.items(), key=lambda x: x[1], reverse=True):
        career_patterns.append({
            "pattern_id": pattern_id,
            "pattern_name": path,
            "frequency": count,
            "description": f"Observed career transition path: {path}"
        })
        pattern_id += 1
    write_csv(os.path.join(CAREER_DIR, "career_patterns.csv"),
              ["pattern_id", "pattern_name", "frequency", "description"],
              career_patterns)

    # 6. Generate skill_frequency.csv
    skill_counts = {}
    for es in employee_skills:
        s_id = es["skill_id"]
        skill_counts[s_id] = skill_counts.get(s_id, 0) + 1
        
    skills_frequency = []
    max_f = max(skill_counts.values()) if skill_counts else 1
    for s_id, s_name, cat, diff in SKILLS_MASTER:
        freq = skill_counts.get(s_id, 0)
        score = max(3, int((freq / max_f) * 10))
        skills_frequency.append({
            "skill_id": s_id,
            "skill_name": s_name,
            "frequency": freq,
            "importance_score": score
        })
    write_csv(os.path.join(CAREER_DIR, "skill_frequency.csv"),
              ["skill_id", "skill_name", "frequency", "importance_score"],
              skills_frequency)

    # 7. Generate hiring_signals.csv
    hiring_signals = []
    sig_id = 1
    # Add top skills
    for sf in sorted(skills_frequency, key=lambda x: x["frequency"], reverse=True)[:8]:
        hiring_signals.append({
            "signal_id": sig_id,
            "signal_name": sf["skill_name"],
            "signal_type": "Skill",
            "weight": sf["importance_score"],
            "description": f"Highly sought-after backend engineering skill ({sf['frequency']} profiles)"
        })
        sig_id += 1
    # Add top colleges
    college_counts = {}
    for p in employee_profiles:
        college_counts[p["college"]] = college_counts.get(p["college"], 0) + 1
    for col, count in sorted(college_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        hiring_signals.append({
            "signal_id": sig_id,
            "signal_name": col,
            "signal_type": "Education",
            "weight": min(10, 5 + int(count / 10)),
            "description": f"Strong representation of graduates from {col} ({count} profiles)"
        })
        sig_id += 1
    # Add top previous companies
    prev_comp_counts = {}
    for p in employee_profiles:
        if p["previous_company"]:
            prev_comp_counts[p["previous_company"]] = prev_comp_counts.get(p["previous_company"], 0) + 1
    for pc, count in sorted(prev_comp_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        hiring_signals.append({
            "signal_id": sig_id,
            "signal_name": f"{pc}Experience",
            "signal_type": "Career",
            "weight": min(10, 6 + int(count / 10)),
            "description": f"Observed transition trend from {pc} ({count} profiles)"
        })
        sig_id += 1
    write_csv(os.path.join(CAREER_DIR, "hiring_signals.csv"),
              ["signal_id", "signal_name", "signal_type", "weight", "description"],
              hiring_signals)

    # 8. Generate hiring_layer CSVs
    # A. interview_rounds.csv
    rounds_data = [
        {"round_id": 1, "company_role_id": 1, "round_number": 1, "round_name": "Online Assessment", "focus": "DSA & Coding", "duration_minutes": 90, "platform": "HackerRank", "description": "2-3 coding problems, arrays, strings, basic trees"},
        {"round_id": 2, "company_role_id": 1, "round_number": 2, "round_name": "Technical DSA Round", "focus": "Data Structures", "duration_minutes": 60, "platform": "Google Meet", "description": "Medium-Hard LeetCode problems on graphs, DP"},
        {"round_id": 3, "company_role_id": 1, "round_number": 3, "round_name": "Low Level Design (LLD)", "focus": "Object Oriented Design", "duration_minutes": 60, "platform": "CoderPad", "description": "Design a parking lot, movie booking system, or splitwise"},
        {"round_id": 4, "company_role_id": 1, "round_number": 4, "round_name": "High Level Design (HLD)", "focus": "System Design", "duration_minutes": 60, "platform": "Miro/Whiteboard", "description": "Design Blinkit delivery routing, notification system at scale"},
        {"round_id": 5, "company_role_id": 1, "round_number": 5, "round_name": "HR & Managerial", "focus": "Behavioral & Culture Fit", "duration_minutes": 45, "platform": "Zoom", "description": "Situational, teamwork, leadership questions"}
    ]
    write_csv(os.path.join(HIRING_DIR, "interview_rounds.csv"),
              ["round_id", "company_role_id", "round_number", "round_name", "focus", "duration_minutes", "platform", "description"],
              rounds_data)
              
    # B. interview_questions.csv
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from expand_datasets import generate_interview_questions
        generate_interview_questions()
    except Exception as e:
        print(f"Error expanding interview questions: {e}")
        questions_data = [
            {"question_id": 1, "company_role_id": 1, "category": "DSA", "difficulty": "Medium", "question": "Merge Intervals", "answer": "Sort and merge overlapping intervals", "explanation": "Sort by start time, keep track of merged intervals.", "tags": "['Arrays', 'Sorting']", "frequency": "Very Common"},
            {"question_id": 2, "company_role_id": 1, "category": "DSA", "difficulty": "Hard", "question": "Sliding Window Maximum", "answer": "Use a Deque to store indices of elements in window", "explanation": "Maintain monotonically decreasing elements in deque.", "tags": "['Sliding Window', 'Deque']", "frequency": "Common"},
            {"question_id": 3, "company_role_id": 1, "category": "System Design", "difficulty": "Hard", "question": "Design a Quick-Commerce Delivery system", "answer": "Use microservices, spatial indexing (H3), WebSockets for real-time tracking.", "explanation": "Explain store management, runner assignment algorithms, geo-hashing.", "tags": "['System Design', 'HLD', 'Geo-Hashing']", "frequency": "Very Common"},
            {"question_id": 4, "company_role_id": 1, "category": "DBMS", "difficulty": "Medium", "question": "Explain Database Transactions and ACID properties", "answer": "ACID stands for Atomicity, Consistency, Isolation, Durability", "explanation": "Explain concurrency control, read committed vs serializable levels.", "tags": "['DBMS', 'Transactions']", "frequency": "Common"},
            {"question_id": 5, "company_role_id": 1, "category": "OS", "difficulty": "Medium", "question": "Process vs Thread", "answer": "Process is executing program, thread is execution unit inside process", "explanation": "Process has its own memory space, threads share process memory.", "tags": "['OS', 'Multithreading']", "frequency": "Common"},
            {"question_id": 6, "company_role_id": 1, "category": "System Design", "difficulty": "Medium", "question": "Design a URL Shortener", "answer": "Generate hash using Base62, store mapping in database with Redis cache.", "explanation": "Detail scaling read operations, caching strategies, and base62 encoding.", "tags": "['System Design', 'HLD', 'Base62']", "frequency": "Common"},
            {"question_id": 7, "company_role_id": 1, "category": "Java", "difficulty": "Medium", "question": "How does HashMap work internally?", "answer": "Uses an array of buckets, hashing, and linkedlist/red-black tree for collision resolution.", "explanation": "Explain hashCode(), equals(), bucket collision, and bucket treeification.", "tags": "['Java', 'Collections']", "frequency": "Very Common"}
        ]
        write_csv(os.path.join(HIRING_DIR, "interview_questions.csv"),
                  ["question_id", "company_role_id", "category", "difficulty", "question", "answer", "explanation", "tags", "frequency"],
                  questions_data)
              
    # C. company_interview_patterns.csv
    company_patterns = [
        {"pattern_id": 1, "company_id": 1, "role_id": 1, "typical_rounds_count": 5, "difficulty_rating": 8, "notes": "Blinkit values speed in coding, optimization of SQL queries, and solid concurrency logic."},
        {"pattern_id": 2, "company_id": 7, "role_id": 1, "typical_rounds_count": 4, "difficulty_rating": 9, "notes": "Amazon focuses heavily on Leadership Principles and scale system design."}
    ]
    write_csv(os.path.join(HIRING_DIR, "company_interview_patterns.csv"),
              ["pattern_id", "company_id", "role_id", "typical_rounds_count", "difficulty_rating", "notes"],
              company_patterns)
              
    # D. hiring_criteria.csv
    hiring_criteria = [
        {"criteria_id": 1, "company_role_id": 1, "min_experience_years": 0.0, "cgpa_cutoff": 6.5, "backlogs_allowed": "False", "notes": "For freshers, solid DSA, OS, DBMS and Java/Go skills. No backlogs allowed."}
    ]
    write_csv(os.path.join(HIRING_DIR, "hiring_criteria.csv"),
              ["criteria_id", "company_role_id", "min_experience_years", "cgpa_cutoff", "backlogs_allowed", "notes"],
              hiring_criteria)

    # 9. Generate learning_layer CSVs
    try:
        from expand_datasets import generate_learning_resources, generate_projects
        generate_learning_resources()
        generate_projects()
    except Exception as e:
        print(f"Error expanding learning resources and projects: {e}")
        resources = [
            {"resource_id": 1, "title": "Striver's A2Z DSA Sheet", "resource_type": "Practice Platform", "topic": "DSA (Combined)", "skill_id": 25, "url": "https://takeuforward.org", "platform": "TakeUForward", "difficulty": "Intermediate", "duration_hours": 120.0, "is_free": "True", "rating": 4.9, "notes": "Best structured resource for DSA preparation"},
            {"resource_id": 2, "title": "Gate Smashers DBMS Playlist", "resource_type": "Playlist", "topic": "DBMS", "skill_id": 6, "url": "https://youtube.com/playlist?list=PLxCzCOWd7aiFAN6I81C9gzqhVJ_E3u5JH", "platform": "YouTube", "difficulty": "Beginner", "duration_hours": 30.0, "is_free": "True", "rating": 4.8, "notes": "Clear, concise DBMS exam and interview basics"},
            {"resource_id": 3, "title": "System Design Primer by Donne Martin", "resource_type": "Documentation", "topic": "System Design", "skill_id": 25, "url": "https://github.com/donnemartin/system-design-primer", "platform": "GitHub", "difficulty": "Advanced", "duration_hours": 40.0, "is_free": "True", "rating": 4.9, "notes": "Essential GitHub repository for scalable HLD concepts"},
            {"resource_id": 4, "title": "Java Brains Spring Boot Tutorial", "resource_type": "Playlist", "topic": "Spring Boot", "skill_id": 11, "url": "https://youtube.com/playlist?list=PLqq-7n6Y5lkXn5i-QpL7vY7K7g1xIu4U5", "platform": "YouTube", "difficulty": "Intermediate", "duration_hours": 15.0, "is_free": "True", "rating": 4.7, "notes": "Comprehensive backend development tutorial"},
            {"resource_id": 5, "title": "Gaurav Sen System Design HLD", "resource_type": "Playlist", "topic": "System Design", "skill_id": 25, "url": "https://youtube.com/playlist?list=PLMCXHnjXnTRjf4g94N86d8Xk6hPnt1Z2S", "platform": "YouTube", "difficulty": "Intermediate", "duration_hours": 12.0, "is_free": "True", "rating": 4.8, "notes": "Visual breakdowns of real-world system architectures"}
        ]
        write_csv(os.path.join(LEARNING_DIR, "learning_resources.csv"),
                  ["resource_id", "title", "resource_type", "topic", "skill_id", "url", "platform", "difficulty", "duration_hours", "is_free", "rating", "notes"],
                  resources)
                  
        projects = [
            {"project_id": 1, "project_name": "Food Delivery Backend", "description": "Build a scalable microservices backend for food ordering, cart, and driver assignments using Spring Boot and Kafka.", "difficulty": "Advanced", "estimated_days": 30, "outcome": "Demonstrates event-driven architecture, API gateway, caching, and database design."},
            {"project_id": 2, "project_name": "URL Shortener at Scale", "description": "Create a high-performance URL shortening service with Go, Redis, and PostgreSQL.", "difficulty": "Intermediate", "estimated_days": 14, "outcome": "Demonstrates caching, database indexing, short link hashing, and load balancing."},
            {"project_id": 3, "project_name": "Student Database Management", "description": "Build a simple CRUD dashboard for managing student grades and schedules using Node and MySQL.", "difficulty": "Beginner", "estimated_days": 7, "outcome": "Demonstrates relational database schema design and basic REST APIs."}
        ]
        write_csv(os.path.join(LEARNING_DIR, "projects_master.csv"),
                  ["project_id", "project_name", "description", "difficulty", "estimated_days", "outcome"],
                  projects)
                  
        project_skills = [
            {"id": 1, "project_id": 1, "skill_id": 2}, # Java
            {"id": 2, "project_id": 1, "skill_id": 11}, # Spring Boot
            {"id": 3, "project_id": 1, "skill_id": 4}, # Kafka
            {"id": 4, "project_id": 2, "skill_id": 1}, # Go
            {"id": 5, "project_id": 2, "skill_id": 5}, # Redis
            {"id": 6, "project_id": 2, "skill_id": 6}, # PostgreSQL
            {"id": 7, "project_id": 3, "skill_id": 12}, # NodeJS
            {"id": 8, "project_id": 3, "skill_id": 16}  # MySQL
        ]
        write_csv(os.path.join(LEARNING_DIR, "project_skill_mapping.csv"),
                  ["id", "project_id", "skill_id"],
                  project_skills)

    # B. roadmap_templates.csv
    roadmaps = [
        {"template_id": 1, "qualification_id": 1, "total_duration_months": 48, "overview": "Long term developmental path focused on fundamental programming, data structures, and computer science basics."},
        {"template_id": 2, "qualification_id": 2, "total_duration_months": 36, "overview": "Mid-term preparation road map starting core DSA, basic databases and minor projects."},
        {"template_id": 3, "qualification_id": 3, "total_duration_months": 18, "overview": "Placement sprint. High focus on advanced DSA, core CS (OS, DBMS, CN), and backend development with Spring Boot."},
        {"template_id": 4, "qualification_id": 4, "total_duration_months": 6, "overview": "Critical sprint. Maximum interview practice, mock interviews, system design and resume polish."}
    ]
    write_csv(os.path.join(LEARNING_DIR, "roadmap_templates.csv"),
              ["template_id", "qualification_id", "total_duration_months", "overview"],
              roadmaps)

    # 10. Generate student_layer CSVs
    # A. student_profiles.csv
    students = []
    for i in range(120): # 120 sample students
        std_id = i + 1
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        students.append({
            "student_id": std_id,
            "name": f"{fn} {ln}",
            "email": f"{fn.lower()}.{ln.lower()}{std_id}@gmail.com",
            "qualification_id": random.randint(1, 4), # 1st to 4th year
            "branch": random.choice(["Computer Science", "Information Technology", "Electronics"]),
            "cgpa": round(random.uniform(6.0, 9.8), 2),
            "college": random.choice(COLLEGES)
        })
    write_csv(os.path.join(STUDENT_DIR, "student_profiles.csv"),
              ["student_id", "name", "email", "qualification_id", "branch", "cgpa", "college"],
              students)
              
    # B. student_skills.csv
    student_skills = []
    row_id = 1
    for s in students:
        std_id = s["student_id"]
        # Assign 2-5 random skills
        known = random.sample([sk[0] for sk in SKILLS_MASTER], k=random.randint(2, 5))
        for sk_id in known:
            student_skills.append({
                "id": row_id,
                "student_id": std_id,
                "skill_id": sk_id,
                "proficiency": random.choice(["Beginner", "Intermediate", "Advanced"])
            })
            row_id += 1
    write_csv(os.path.join(STUDENT_DIR, "student_skills.csv"),
              ["id", "student_id", "skill_id", "proficiency"],
              student_skills)
              
    # C. student_targets.csv
    student_targets = []
    for idx, s in enumerate(students):
        student_targets.append({
            "id": idx + 1,
            "student_id": s["student_id"],
            "company_role_id": 1 # Target SDE at Blinkit
        })
    write_csv(os.path.join(STUDENT_DIR, "student_targets.csv"),
              ["id", "student_id", "company_role_id"],
              student_targets)
              
    # D. student_projects.csv
    student_projects = []
    row_id = 1
    for s in students:
        if random.random() < 0.6: # 60% have built a project
            student_projects.append({
                "id": row_id,
                "student_id": s["student_id"],
                "project_id": random.randint(1, 3),
                "status": random.choice(["In Progress", "Completed"])
            })
            row_id += 1
    write_csv(os.path.join(STUDENT_DIR, "student_projects.csv"),
              ["id", "student_id", "project_id", "status"],
              student_projects)
              
    # E. skill_gaps.csv & generated_roadmaps.csv (Empty placeholders or mock entries)
    write_csv(os.path.join(STUDENT_DIR, "skill_gaps.csv"),
              ["id", "student_id", "skill_id", "priority"],
              [])
              
    write_csv(os.path.join(STUDENT_DIR, "generated_roadmaps.csv"),
              ["id", "student_id", "roadmap_json"],
              [])

    print("CSV dataset generation complete!")

def write_csv(filepath, headers, data):
    with open(filepath, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    generate_all_datasets()
