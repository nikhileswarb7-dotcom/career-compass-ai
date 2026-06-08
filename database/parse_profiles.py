import os
import re
import csv
import json
import psycopg2
from pypdf import PdfReader

# ----------------------------------------------------------------
# Configurations & Paths
# ----------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMPLOYEES_DIR = os.path.join(os.path.dirname(__file__), "industry_layer")
CAREER_DIR = os.path.join(os.path.dirname(__file__), "career_layer")
PROFILES_DIR = os.path.join(BASE_DIR, "raw_data", "Profiles(Linkedin)")
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
IMPORT_DATA_PATH = os.path.join(os.path.dirname(__file__), "import_data.py")

# ----------------------------------------------------------------
# 1. Database Connection Config loader
# ----------------------------------------------------------------
def load_db_config():
    config = {
        "host":     "localhost",
        "port":     5432,
        "dbname":   "career_compass_ai",
        "user":     "postgres",
        "password": "Nikhil@2824"
    }
    if os.path.exists(IMPORT_DATA_PATH):
        try:
            with open(IMPORT_DATA_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            for key in config.keys():
                match = re.search(r'"' + key + r'"\s*:\s*"(.*?)"', content)
                if not match:
                    match = re.search(r"'" + key + r"'\s*:\s*'(.*?)'", content)
                if match:
                    config[key] = match.group(1)
        except Exception as e:
            print(f"Error loading DB config from import_data.py: {e}")
    return config

# ----------------------------------------------------------------
# 2. LinkedIn PDF Heuristic Parser
# ----------------------------------------------------------------
def clean_text(text):
    return text.replace('\xa0', ' ').replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-').strip()

def parse_profile_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    
    lines = [clean_text(line) for line in text.split('\n')]
    lines = [line for line in lines if line] # remove empty lines
    
    # Extract Name & Headline via LinkedIn handle match
    name = None
    headline = None
    location = None
    linkedin_url = None
    github_url = None
    handle = ""
    
    for line in lines:
        match = re.search(r'www\.linkedin\.com/in/([a-zA-Z0-9\-\_]+)', line)
        if match:
            linkedin_url = line.strip()
            handle = match.group(1).lower()
            break
            
    for line in lines:
        match = re.search(r'github\.com/([a-zA-Z0-9\-\_]+)', line)
        if match:
            github_url = line.strip()
            break
            
    if handle:
        handle_tokens = set(re.findall(r'[a-z0-9]+', handle.replace('-', ' ')))
        best_overlap = 0
        best_line = None
        name_idx = -1
        
        intro_headers = ["Contact", "Top Skills", "Languages", "Certifications", "Publications", "Summary", "Experience", "Education"]
        
        for i, line in enumerate(lines[:40]):
            line_strip = line.strip()
            if any(h in line_strip for h in ["www.linkedin.com", "LinkedIn", "Top Skills", "Certifications", "Languages", "@"]):
                continue
            if line_strip in intro_headers or line_strip.startswith("Page ") or line_strip.startswith("Contact"):
                continue
            
            line_tokens = set(re.findall(r'[a-z0-9]+', line_strip.lower()))
            overlap = len(handle_tokens.intersection(line_tokens))
            
            words = line_strip.split()
            if 1 < len(words) <= 5 and re.match(r'^[A-Z][a-zA-Z\s\.\-\u00C0-\u00FF]+$', line_strip):
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_line = line_strip
                    name_idx = i
                    
        if best_line:
            name = best_line
            if name_idx + 1 < len(lines):
                headline = lines[name_idx + 1].strip()
                if name_idx + 2 < len(lines):
                    loc_candidate = lines[name_idx + 2].strip()
                    if "," in loc_candidate or any(k in loc_candidate for k in ["India", "USA", "Bengaluru", "Hyderabad", "Delhi", "Gurugram"]):
                        location = loc_candidate
                        
    if not name:
        # Fallback regex search
        for i, line in enumerate(lines[:30]):
            line_strip = line.strip()
            if any(h in line_strip for h in ["www.linkedin.com", "LinkedIn", "Top Skills", "Certifications", "@"]):
                continue
            words = line_strip.split()
            if 1 < len(words) <= 5 and re.match(r'^[A-Z][a-zA-Z\s\.\-\u00C0-\u00FF]+$', line_strip):
                name = line_strip
                name_idx = i
                if i + 1 < len(lines):
                    headline = lines[i + 1].strip()
                if i + 2 < len(lines):
                    loc_candidate = lines[i + 2].strip()
                    if "," in loc_candidate or any(k in loc_candidate for k in ["India", "USA"]):
                        location = loc_candidate
                break

    # Extract Top Skills & Certifications
    skills = []
    in_skills = False
    for line in lines:
        if "Top Skills" in line:
            in_skills = True
            continue
        if in_skills:
            if any(h in line for h in ["Languages", "Certifications", "Publications", "Summary", "Experience", name or "---"]):
                in_skills = False
            else:
                cleaned_skill = re.sub(r'\(.*\)', '', line).strip()
                if cleaned_skill and cleaned_skill != "" and len(cleaned_skill) < 50:
                    skills.append(cleaned_skill)

    # Extract Experience
    experiences = []
    section = None
    current_company = None
    
    date_range_regex = r'^[A-Za-z]+\s+\d{4}\s*-\s*([A-Za-z]+\s+\d{4}|Present)\s*\(.*\)$'
    duration_regex = r'^(\d+\s+years?\s*)?(\d+\s+months?)?$'

    for i, line in enumerate(lines):
        line_strip = line.strip()
        if line_strip == "Experience":
            section = "experience"
            continue
        elif line_strip in ["Education", "Projects", "Honors-Awards", "Languages", "Certifications"]:
            if section == "experience":
                section = None
        
        if section == "experience":
            if re.match(date_range_regex, line_strip):
                role = lines[i-1].strip() if i-1 >= 0 else ""
                prev_line = lines[i-2].strip() if i-2 >= 0 else ""
                
                is_new_company = False
                company_name = None
                
                if re.match(duration_regex, prev_line):
                    is_new_company = True
                    company_name = lines[i-3].strip() if i-3 >= 0 else ""
                else:
                    is_location = "," in prev_line or any(k in prev_line for k in ["India", "USA", "Bengaluru", "Hyderabad", "Delhi", "Gurugram"])
                    is_bullet = (prev_line.startswith("\uf0b7") or prev_line.startswith("o ") or 
                                 prev_line.startswith("-") or prev_line.startswith("*") or 
                                 prev_line.startswith("•") or prev_line.startswith(" ") or 
                                 prev_line.startswith("\u2022"))
                    is_page = prev_line.startswith("Page ")
                    is_date = re.match(date_range_regex, prev_line) or "(" in prev_line
                    
                    if not (is_location or is_bullet or is_page or is_date or prev_line == ""):
                        is_new_company = True
                        company_name = prev_line
                
                if is_new_company and company_name:
                    current_company = company_name
                
                if current_company:
                    current_company = re.sub(r'\d+$', '', current_company).strip()
                    current_company = re.sub(r'\(.*\)', '', current_company).strip()
                
                duration_match = re.search(r'\((.*?)\)', line_strip)
                duration_str = duration_match.group(1) if duration_match else ""
                months = 0
                if duration_str:
                    years_m = re.search(r'(\d+)\s*year', duration_str)
                    months_m = re.search(r'(\d+)\s*month', duration_str)
                    if years_m:
                        months += int(years_m.group(1)) * 12
                    if months_m:
                        months += int(months_m.group(1))
                
                date_parts = line_strip.split(' - ')
                start_date = date_parts[0].strip()
                end_part = date_parts[1].split('(')[0].strip()
                
                experiences.append({
                    "company": current_company,
                    "role": role,
                    "start_date": start_date,
                    "end_date": end_part,
                    "duration_months": months
                })

    # Extract Education (Block-based)
    education = []
    section = None
    edu_lines = []
    
    for line in lines:
        line_strip = line.strip()
        if line_strip == "Education":
            section = "education"
            continue
        elif line_strip in ["Experience", "Projects", "Honors-Awards", "Languages", "Certifications"]:
            if section == "education":
                section = None
                
        if section == "education":
            edu_lines.append(line_strip)
            
    block_start_idx = 0
    for idx, line in enumerate(edu_lines):
        year_match = re.search(r'\((\d{4})\s*-\s*(\d{4})\)', line)
        if year_match:
            block = edu_lines[block_start_idx : idx + 1]
            block_start_idx = idx + 1
            
            if block:
                college = block[0]
                college = re.sub(r'\d+$', '', college).strip()
                college = re.sub(r'\(.*\)', '', college).strip()
                
                degree_text = " ".join(block[1:])
                degree_text = re.sub(r'\((\d{4})\s*-\s*(\d{4})\)', '', degree_text).strip()
                
                degree = ""
                field = ""
                if "," in degree_text:
                    parts = degree_text.split(',', 1)
                    degree = parts[0].strip()
                    field = parts[1].strip()
                else:
                    degree = degree_text
                
                education.append({
                    "college": college,
                    "degree": degree,
                    "field": field,
                    "start_year": year_match.group(1),
                    "end_year": year_match.group(2)
                })

    return {
        "name": name,
        "headline": headline,
        "location": location,
        "skills": skills,
        "experience": experiences,
        "education": education,
        "linkedin_url": linkedin_url,
        "github_url": github_url
    }

# ----------------------------------------------------------------
# 3. Normalization & Loading Existing Master Data
# ----------------------------------------------------------------
def load_existing_csv(filename):
    filepath = os.path.join(EMPLOYEES_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(CAREER_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def normalize_company_name(name):
    if not name:
        return ""
    name_lower = name.lower()
    # Normalize common companies
    if "blinkit" in name_lower:
        return "Blinkit"
    if "amazon" in name_lower:
        return "Amazon"
    if "microsoft" in name_lower:
        return "Microsoft"
    if "google" in name_lower:
        return "Google"
    if "zomato" in name_lower:
        return "Zomato"
    if "pocket fm" in name_lower or "pocketfm" in name_lower:
        return "Pocket FM"
    if "flipkart" in name_lower:
        return "Flipkart"
    if "meesho" in name_lower:
        return "Meesho"
    if "jio" in name_lower:
        return "Jio Platforms"
    if "accenture" in name_lower:
        return "Accenture"
    if "morgan stanley" in name_lower or "morganstanley" in name_lower:
        return "Morgan Stanley"
    if "red hat" in name_lower or "redhat" in name_lower:
        return "Red Hat"
    if "yubi" in name_lower:
        return "Yubi"
    if "probo" in name_lower:
        return "Probo"
    if "urban company" in name_lower or "urbancompany" in name_lower:
        return "Urban Company"
    return name.strip()

def normalize_college_name(name):
    if not name:
        return ""
    name_lower = name.lower()
    if "iiit" in name_lower:
        # Keep specific IIIT names
        for city in ["allahabad", "kota", "sri city", "delhi", "guwahati", "dharwad", "gwalior", "pune", "bangalore"]:
            if city in name_lower:
                return f"IIIT {city.title()}"
        return "IIIT"
    if "iit" in name_lower:
        for city in ["kharagpur", "bhilai", "ropar", "delhi", "bombay", "madras", "kanpur", "guwahati", "roorkee", "bhu"]:
            if city in name_lower:
                return f"IIT {city.upper()}"
        return "IIT"
    if "vellore institute" in name_lower or "vit vellore" in name_lower or "vit university" in name_lower:
        return "VIT Vellore"
    if "techno india" in name_lower:
        return "Techno India University"
    if "netaji subhash" in name_lower or "nsec" in name_lower:
        return "Netaji Subhash Engineering College"
    if "bms" in name_lower:
        return "BMS Institute of Technology"
    if "pes university" in name_lower or "pesit" in name_lower:
        return "PES University"
    return name.strip()

def normalize_degree(degree):
    if not degree:
        return ""
    deg_lower = degree.lower()
    if "b.tech" in deg_lower or "btech" in deg_lower or "bachelor of technology" in deg_lower:
        return "BTech"
    if "m.tech" in deg_lower or "mtech" in deg_lower or "master of technology" in deg_lower:
        return "MTech"
    if "mca" in deg_lower or "master of computer applications" in deg_lower:
        return "MCA"
    if "b.e" in deg_lower or "be" in deg_lower or "bachelor of engineering" in deg_lower:
        return "BE"
    if "dual degree" in deg_lower:
        return "Dual Degree"
    if "high school" in deg_lower or "12th" in deg_lower:
        return "High School"
    if "10th" in deg_lower or "matric" in deg_lower:
        return "10th"
    return degree.strip()

# ----------------------------------------------------------------
# 4. Main Processing Pipeline
# ----------------------------------------------------------------
def process_pipeline():
    print("\nCareerCompass AI — Data Processing Pipeline")
    print("=" * 60)
    
    # Try opening DB connection early to load live skills
    print("Connecting early to database to load skills...")
    db_config = load_db_config()
    conn_early = None
    skills_master = {}
    try:
        conn_early = psycopg2.connect(**db_config)
        cur = conn_early.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        cur.execute("SELECT skill_id, skill_name FROM skills;")
        rows = cur.fetchall()
        skills_csv = []
        for r in rows:
            skills_master[r[1].lower()] = int(r[0])
            skills_csv.append({"skill_id": str(r[0]), "skill_name": r[1]})
        cur.close()
        conn_early.close()
        print(f"Loaded {len(skills_master)} skills from live PostgreSQL database.")
    except Exception as e:
        print(f"Failed to connect early to PostgreSQL ({e}), falling back to CSV.")
        
    if not skills_master:
        print("Loading skills master from CSV...")
        skills_csv = load_existing_csv("skills_master.csv")
        skills_master = {row['skill_name'].lower(): int(row['skill_id']) for row in skills_csv}
        if not skills_master:
            # Fallback predefined skills if CSV empty
            predefined = ["Go", "Java", "Python", "Kafka", "Redis", "PostgreSQL", "Docker", "Kubernetes", "gRPC", "Microservices", 
                          "Spring Boot", "NodeJS", "AWS", "GCP", "DynamoDB", "MySQL", "ElasticSearch", "Django", "React", "TypeScript", 
                          "NextJS", "Kotlin", "Android", "SRE", "System Design", "Distributed Systems"]
            skills_master = {name.lower(): i+1 for i, name in enumerate(predefined)}
            skills_csv = [{"skill_id": str(i+1), "skill_name": name} for i, name in enumerate(predefined)]
    
    # Load existing companies
    print("Loading existing companies...")
    companies_csv = load_existing_csv("companies.csv")
    companies_by_name = {row['company_name'].lower(): row for row in companies_csv}
    
    # Find all PDFs to parse
    print("Scanning profiles directories...")
    pdf_files = []
    for s_dir in [PROFILES_DIR, RAW_DATA_DIR]:
        if os.path.exists(s_dir):
            for root, dirs, files in os.walk(s_dir):
                for f in files:
                    if f.endswith(".pdf"):
                        pdf_files.append(os.path.join(root, f))
                        
    print(f"Found {len(pdf_files)} PDF profile files. Parsing...")
    
    parsed_profiles = []
    seen_names = set()
    for filepath in pdf_files:
        try:
            profile = parse_profile_pdf(filepath)
            # Determine target company based on folder
            folder_name = os.path.basename(os.path.dirname(filepath)).upper()
            if "BLINKIT" in folder_name:
                profile["target_company"] = "Blinkit"
            elif "AMAZON" in folder_name:
                profile["target_company"] = "Amazon"
            elif "MICROSOFT" in folder_name:
                profile["target_company"] = "Microsoft"
            else:
                profile["target_company"] = "Blinkit"
                
            if profile["name"]:
                name_low = profile["name"].strip().lower()
                if name_low not in seen_names:
                    seen_names.add(name_low)
                    parsed_profiles.append(profile)
        except Exception as e:
            print(f"  Error parsing {os.path.basename(filepath)}: {e}")
            
    print(f"Successfully parsed {len(parsed_profiles)} unique profiles.")
    
    # Resolve and structure data
    structured_companies = {}
    # Seed companies from companies_by_name
    for name, c_row in companies_by_name.items():
        c_id = int(c_row['company_id'])
        structured_companies[c_row['company_name']] = {
            "company_id": c_id,
            "company_name": c_row['company_name'],
            "industry": c_row['industry'],
            "company_type": c_row['company_type']
        }
        
    next_company_id = max([c["company_id"] for c in structured_companies.values()]) + 1 if structured_companies else 1
    
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
    
    next_profile_id = 1
    next_education_id = 1
    next_transition_id = 1
    
    for p in parsed_profiles:
        profile_id = next_profile_id
        next_profile_id += 1
        
        name = p["name"]
        headline = p["headline"] or ""
        location = p["location"] or ""
        
        # Sort experiences chronologically
        exp_list = p["experience"]
        # Filter and normalize companies
        for exp in exp_list:
            exp["company"] = normalize_company_name(exp["company"])
            
        # Chronological experiences: oldest first
        # We parse start dates. e.g. "January 2020". Let's convert to sortable key.
        def parse_date_key(d_str):
            if not d_str or d_str == "Present":
                return 999912 # Future
            parts = d_str.split()
            year = 2000
            month = 1
            months = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
                      "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
            for p in parts:
                if p.isdigit() and len(p) == 4:
                    year = int(p)
                elif p.lower() in months:
                    month = months[p.lower()]
            return year * 100 + month
            
        exp_list.sort(key=lambda x: parse_date_key(x["start_date"]))
        
        # Determine current company, current role, previous company, experience years, career path
        current_company = p["target_company"] # default to folder target
        current_role = "Software Development Engineer"
        
        # Let's find their most recent experience at their target/current company
        target_exps = [e for e in exp_list if e["company"] == p["target_company"]]
        if target_exps:
            current_role = target_exps[-1]["role"]
            current_company = target_exps[-1]["company"]
        elif exp_list:
            current_role = exp_list[-1]["role"]
            current_company = exp_list[-1]["company"]
            
        # Experience Years
        total_months = sum(e["duration_months"] for e in exp_list)
        experience_years = round(total_months / 12.0, 1)
        
        # Companies tracking
        for e in exp_list:
            comp_name = e["company"]
            if comp_name and comp_name not in structured_companies:
                # Add new company
                comp_type = "Startup"
                if any(x in comp_name.lower() for x in ["university", "college", "institute", "school"]):
                    comp_type = "Academic"
                elif comp_name in ["Google", "Amazon", "Microsoft", "Meta", "Netflix", "Apple", "Oracle", "Salesforce", "Accenture", "Infosys", "TCS", "Wipro", "Cognizant"]:
                    comp_type = "MNC"
                elif comp_name == "Blinkit Intern Program" or comp_name == "Blinkit Internal":
                    comp_type = "Internal"
                elif comp_name in ["Blinkit", "Zomato", "Flipkart", "Meesho", "Jio Platforms", "Swiggy", "Paytm", "Ola", "Uber", "PhonePe"]:
                    comp_type = "Product"
                    
                structured_companies[comp_name] = {
                    "company_id": next_company_id,
                    "company_name": comp_name,
                    "industry": "Quick Commerce" if comp_name == "Blinkit" else "Technology",
                    "company_type": comp_type
                }
                next_company_id += 1
                
        # Previous Company & Career Path
        # Previous company is the last company they worked at that is NOT the current target company
        prev_comp = ""
        career_path = ""
        
        # Find index of first target company experience
        target_idx = -1
        for idx, e in enumerate(exp_list):
            if e["company"] == current_company:
                target_idx = idx
                break
                
        if target_idx > 0:
            prev_comp = exp_list[target_idx - 1]["company"]
            career_path = f"{prev_comp}->{current_company}"
        elif target_idx == 0:
            # Check if their first role was an intern
            first_role = exp_list[target_idx]["role"].lower()
            if "intern" in first_role:
                prev_comp = ""
                career_path = "Intern->SDE1->SDE2" if "ii" in headline.lower() or "2" in headline else "Intern->SDE"
            else:
                prev_comp = ""
                career_path = f"Campus->{current_company}"
        else:
            # If no target company found in experiences, but folder was Blinkit/etc
            if exp_list:
                prev_comp = exp_list[-2]["company"] if len(exp_list) > 1 else ""
                career_path = f"{prev_comp}->{current_company}" if prev_comp else f"Campus->{current_company}"
            else:
                prev_comp = ""
                career_path = f"Campus->{current_company}"
                
        # Education details (highest degree)
        edu_list = p["education"]
        college_val = ""
        degree_val = ""
        
        if edu_list:
            # Sort by end year descending to get most recent/highest
            edu_list.sort(key=lambda x: int(x["start_year"]) if x["start_year"].isdigit() else 0, reverse=True)
            # Find first degree that is BTech/MTech/MCA/BE
            highest_edu = None
            for edu in edu_list:
                deg_norm = normalize_degree(edu["degree"])
                if deg_norm in ["BTech", "MTech", "MCA", "BE", "Dual Degree"]:
                    highest_edu = edu
                    break
            if not highest_edu:
                highest_edu = edu_list[0]
                
            college_val = normalize_college_name(highest_edu["college"])
            degree_val = normalize_degree(highest_edu["degree"])
            
            # Save education profiles
            for edu in edu_list:
                c_name = normalize_college_name(edu["college"])
                d_name = normalize_degree(edu["degree"])
                f_name = edu["field"].replace("\u00b7", "").strip()
                
                education_profiles.append({
                    "education_id": next_education_id,
                    "profile_id": profile_id,
                    "college": c_name,
                    "degree": d_name,
                    "field": f_name
                })
                next_education_id += 1
                
        # Map current role to role_id
        def map_role_to_id(role_name):
            role_lower = role_name.lower() if role_name else ""
            if "intern" in role_lower:
                return 1
            elif "sde-i" in role_lower or "sde i" in role_lower or "software development engineer i" in role_lower or "entry" in role_lower:
                return 2
            elif "sde-ii" in role_lower or "sde ii" in role_lower or "software development engineer ii" in role_lower or "sde2" in role_lower:
                return 3
            elif "sde-iii" in role_lower or "sde iii" in role_lower or "software development engineer iii" in role_lower or "sde3" in role_lower:
                return 4
            elif "senior" in role_lower:
                return 5
            elif "lead" in role_lower:
                return 6
            elif "manager" in role_lower:
                return 7
            elif "frontend" in role_lower:
                return 9
            elif "sre" in role_lower or "devops" in role_lower or "reliability" in role_lower:
                return 10
            elif "android" in role_lower or "ios" in role_lower or "mobile" in role_lower:
                return 11
            elif "ai" in role_lower or "machine learning" in role_lower or "ml" in role_lower:
                return 12
            else:
                return 8 # Backend Engineer default
                
        role_id = map_role_to_id(current_role)

        # Determine career_stage based on experience_years
        if experience_years == 0.0:
            career_stage = "Foundational"
        elif experience_years < 2.0:
            career_stage = "Entry"
        elif experience_years < 5.0:
            career_stage = "Mid"
        else:
            career_stage = "Senior"

        # Determine company_tier based on current_company
        comp_clean = current_company.lower().strip() if current_company else ""
        tier_1 = ["google", "microsoft", "meta", "amazon", "blinkit", "zomato", "swiggy", "phonepe"]
        tier_3 = ["tcs", "infosys", "wipro", "cognizant", "accenture"]
        
        if any(x in comp_clean for x in tier_1):
            company_tier = 1
        elif any(x in comp_clean for x in tier_3):
            company_tier = 3
        else:
            company_tier = 2

        employee_profiles.append({
            "profile_id": profile_id,
            "name": name,
            "role_id": role_id,
            "current_company": current_company,
            "experience_years": experience_years,
            "college": college_val,
            "degree": degree_val,
            "previous_company": prev_comp,
            "career_path": career_path,
            "linkedin_url": p.get("linkedin_url") or "",
            "github_url": p.get("github_url") or "",
            "career_stage": career_stage,
            "company_tier": company_tier
        })
        
        # Skills mapping
        for s_name in p["skills"]:
            s_name_lower = s_name.lower()
            # Match against master list
            matched_id = None
            if s_name_lower in skills_master:
                matched_id = skills_master[s_name_lower]
            else:
                # Check substring match
                for skill_m, s_id in skills_master.items():
                    if skill_m in s_name_lower or s_name_lower in skill_m:
                        matched_id = s_id
                        break
            if matched_id:
                employee_skills.append({
                    "profile_id": profile_id,
                    "skill_id": matched_id
                })
                
        # Also check experience description/headline for additional skills if none matched
        matched_profile_skills = {es["skill_id"] for es in employee_skills if es["profile_id"] == profile_id}
        if not matched_profile_skills:
            full_profile_text = (headline + " " + " ".join([e["role"] for e in exp_list]) + " " + " ".join(p["skills"])).lower()
            for skill_m, s_id in skills_master.items():
                if skill_m in full_profile_text:
                    employee_skills.append({
                        "profile_id": profile_id,
                        "skill_id": s_id
                    })
                    
        # Transitions
        # Unique list of company sequence (adjacent duplicate companies removed)
        comp_seq = []
        for e in exp_list:
            c = e["company"]
            if c and (not comp_seq or comp_seq[-1] != c):
                comp_seq.append(c)
                
        for idx in range(len(comp_seq) - 1):
            source_c = comp_seq[idx]
            target_c = comp_seq[idx+1]
            source_id = structured_companies[source_c]["company_id"]
            target_id = structured_companies[target_c]["company_id"]
            
            career_transitions.append({
                "transition_id": next_transition_id,
                "profile_id": profile_id,
                "source_company_id": source_id,
                "target_company_id": target_id
            })
            next_transition_id += 1

    # Deduplicate employee_skills
    unique_emp_skills = []
    seen_emp_skills = set()
    for es in employee_skills:
        key = (es["profile_id"], es["skill_id"])
        if key not in seen_emp_skills:
            seen_emp_skills.add(key)
            unique_emp_skills.append(es)
    employee_skills = unique_emp_skills

    # ----------------------------------------------------------------
    # 5. Calculate Aggregations & Analytics
    # ----------------------------------------------------------------
    print("\nRecalculating statistics...")
    
    # A. Skills Frequency & Importance
    skill_counts = {}
    for es in employee_skills:
        s_id = es["skill_id"]
        skill_counts[s_id] = skill_counts.get(s_id, 0) + 1
        
    skills_frequency = []
    # Find max frequency for normalization
    max_freq = max(skill_counts.values()) if skill_counts else 1
    
    # Sort skills by skill_id
    skills_csv_sorted = sorted(skills_csv, key=lambda x: int(x['skill_id']))
    for row in skills_csv_sorted:
        s_id = int(row['skill_id'])
        s_name = row['skill_name']
        freq = skill_counts.get(s_id, 0)
        # Score out of 10
        imp_score = max(4, int((freq / max_freq) * 10)) if max_freq else 4
        skills_frequency.append({
            "skill_id": s_id,
            "skill_name": s_name,
            "frequency": freq,
            "importance_score": imp_score
        })
        
    # B. Career Patterns
    pattern_counts = {}
    for p in employee_profiles:
        cp = p["career_path"]
        if cp:
            pattern_counts[cp] = pattern_counts.get(cp, 0) + 1
            
    # Also add IIT -> Target, IIIT -> Target patterns
    iit_targets = {}
    iiit_targets = {}
    noncs_targets = {}
    for p in employee_profiles:
        target = p["current_company"]
        if p["college"] and p["college"].startswith("IIT"):
            key = f"IIT->{target}"
            iit_targets[key] = iit_targets.get(key, 0) + 1
        elif p["college"] and p["college"].startswith("IIIT"):
            key = f"IIIT->{target}"
            iiit_targets[key] = iiit_targets.get(key, 0) + 1
        if p["degree"] and p["degree"] not in ["BTech", "MTech", "MCA", "BE", "Dual Degree"]:
            key = "NonCSE->SDE"
            noncs_targets[key] = noncs_targets.get(key, 0) + 1
            
    career_patterns = []
    next_pattern_id = 1
    
    # Merge patterns
    merged_patterns = {}
    for k, v in pattern_counts.items():
        merged_patterns[k] = (v, f"Observed transition path: {k}")
    for k, v in iit_targets.items():
        merged_patterns[k] = (v, f"IIT graduates joining {k.split('->')[1]}")
    for k, v in iiit_targets.items():
        merged_patterns[k] = (v, f"IIIT graduates joining {k.split('->')[1]}")
    for k, v in noncs_targets.items():
        merged_patterns[k] = (v, "Engineers from non-CSE backgrounds transitioning into software engineering")
        
    # Sort patterns by frequency descending
    for pattern_name, (freq, desc) in sorted(merged_patterns.items(), key=lambda x: x[1][0], reverse=True):
        career_patterns.append({
            "pattern_id": next_pattern_id,
            "pattern_name": pattern_name,
            "frequency": freq,
            "description": desc
        })
        next_pattern_id += 1

    # C. Hiring Signals
    hiring_signals = []
    next_signal_id = 1
    
    # Skills signals
    for sf in sorted(skills_frequency, key=lambda x: x["frequency"], reverse=True):
        if sf["frequency"] > 0:
            hiring_signals.append({
                "signal_id": next_signal_id,
                "signal_name": sf["skill_name"],
                "signal_type": "Skill",
                "weight": sf["importance_score"],
                "description": f"Frequently occurring skill in engineering profiles ({sf['frequency']} count)"
            })
            next_signal_id += 1
            
    # Education signals
    colleges = [p["college"] for p in employee_profiles if p["college"]]
    college_counts = {}
    for c in colleges:
        college_counts[c] = college_counts.get(c, 0) + 1
        
    for col, count in sorted(college_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:
            hiring_signals.append({
                "signal_id": next_signal_id,
                "signal_name": col,
                "signal_type": "Education",
                "weight": min(10, 5 + count),
                "description": f"Strong representation of graduates from {col} ({count} profiles)"
            })
            next_signal_id += 1
            
    # Career transitions signals
    prev_companies = [p["previous_company"] for p in employee_profiles if p["previous_company"]]
    prev_comp_counts = {}
    for pc in prev_companies:
        prev_comp_counts[pc] = prev_comp_counts.get(pc, 0) + 1
        
    for pc, count in sorted(prev_comp_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:
            hiring_signals.append({
                "signal_id": next_signal_id,
                "signal_name": f"{pc}Experience",
                "signal_type": "Career",
                "weight": min(10, 6 + count),
                "description": f"Observed transition pattern from {pc} ({count} profiles)"
            })
            next_signal_id += 1

    # ----------------------------------------------------------------
    # 6. Database Update
    # ----------------------------------------------------------------
    print("\nAttempting to connect to PostgreSQL...")
    db_config = load_db_config()
    db_connected = False
    conn = None
    
    try:
        conn = psycopg2.connect(**db_config)
        print("Connected to PostgreSQL successfully.")
        db_connected = True
    except Exception as e:
        print(f"\n[WARNING] Database connection failed: {e}")
        print("Check DB_CONFIG password in backend/api/import_data.py.")
        print("Pipeline will proceed to write CSV files directly.\n")
        
    if db_connected and conn:
        try:
            cur = conn.cursor()
            
            print("Creating/Resetting employee tables in DB...")
            
            # Drop tables to recreate with clean IDs
            cur.execute("DROP TABLE IF EXISTS employee_skills CASCADE;")
            cur.execute("DROP TABLE IF EXISTS career_transitions CASCADE;")
            cur.execute("DROP TABLE IF EXISTS education_profiles CASCADE;")
            cur.execute("DROP TABLE IF EXISTS employee_profiles CASCADE;")
            cur.execute("DROP TABLE IF EXISTS skills_frequency CASCADE;")
            cur.execute("DROP TABLE IF EXISTS career_patterns CASCADE;")
            cur.execute("DROP TABLE IF EXISTS hiring_signals CASCADE;")
            
            cur.execute("""
                CREATE TABLE employee_profiles (
                    profile_id INT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    role_id INT REFERENCES roles(role_id) ON DELETE SET NULL,
                    current_company VARCHAR(100),
                    experience_years FLOAT,
                    college VARCHAR(200),
                    degree VARCHAR(200),
                    previous_company VARCHAR(100),
                    career_path TEXT,
                    linkedin_url VARCHAR(500),
                    github_url VARCHAR(500),
                    career_stage VARCHAR(100),
                    company_tier INT
                );
                
                CREATE TABLE education_profiles (
                    education_id INT PRIMARY KEY,
                    profile_id INT REFERENCES employee_profiles(profile_id) ON DELETE CASCADE,
                    college VARCHAR(200),
                    degree VARCHAR(200),
                    field VARCHAR(255)
                );
                
                CREATE TABLE employee_skills (
                    profile_id INT REFERENCES employee_profiles(profile_id) ON DELETE CASCADE,
                    skill_id INT REFERENCES skills(skill_id) ON DELETE CASCADE,
                    PRIMARY KEY (profile_id, skill_id)
                );
                
                CREATE TABLE career_transitions (
                    transition_id INT PRIMARY KEY,
                    profile_id INT REFERENCES employee_profiles(profile_id) ON DELETE CASCADE,
                    source_company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,
                    target_company_id INT REFERENCES companies(company_id) ON DELETE CASCADE
                );
                
                CREATE TABLE skills_frequency (
                    skill_id INT PRIMARY KEY REFERENCES skills(skill_id) ON DELETE CASCADE,
                    skill_name VARCHAR(100),
                    frequency INT,
                    importance_score INT
                );
                
                CREATE TABLE career_patterns (
                    pattern_id INT PRIMARY KEY,
                    pattern_name VARCHAR(200),
                    frequency INT,
                    description TEXT
                );
                
                CREATE TABLE hiring_signals (
                    signal_id INT PRIMARY KEY,
                    signal_name VARCHAR(200),
                    signal_type VARCHAR(50),
                    weight INT,
                    description TEXT
                );
            """)
            
            # Insert Companies
            for c in structured_companies.values():
                cur.execute("""
                    INSERT INTO companies (company_id, company_name, industry, company_type)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (company_name) DO UPDATE 
                    SET industry = EXCLUDED.industry, company_type = EXCLUDED.company_type;
                """, (c["company_id"], c["company_name"], c["industry"], c["company_type"]))
                
            # Insert Roles
            for rs in role_specializations:
                cur.execute("""
                    INSERT INTO roles (role_id, role_name, career_level)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (role_name) DO UPDATE
                    SET career_level = EXCLUDED.career_level;
                """, (rs["role_id"], rs["role_name"], rs["career_level"]))
                
            # Insert Profiles
            for p in employee_profiles:
                cur.execute("""
                    INSERT INTO employee_profiles (profile_id, name, role_id, current_company, experience_years, college, degree, previous_company, career_path, linkedin_url, github_url, career_stage, company_tier)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (p["profile_id"], p["name"], p["role_id"], p["current_company"], p["experience_years"], p["college"], p["degree"], p["previous_company"], p["career_path"], p["linkedin_url"], p["github_url"], p["career_stage"], p["company_tier"]))
                
            # Insert Education
            for edu in education_profiles:
                cur.execute("""
                    INSERT INTO education_profiles (education_id, profile_id, college, degree, field)
                    VALUES (%s, %s, %s, %s, %s)
                """, (edu["education_id"], edu["profile_id"], edu["college"], edu["degree"], edu["field"]))
                
            # Insert Skills mapping
            for es in employee_skills:
                cur.execute("""
                    INSERT INTO employee_skills (profile_id, skill_id)
                    VALUES (%s, %s)
                """, (es["profile_id"], es["skill_id"]))
                
            # Insert Transitions
            for ct in career_transitions:
                cur.execute("""
                    INSERT INTO career_transitions (transition_id, profile_id, source_company_id, target_company_id)
                    VALUES (%s, %s, %s, %s)
                """, (ct["transition_id"], ct["profile_id"], ct["source_company_id"], ct["target_company_id"]))
                
            # Insert Skill Freqs
            for sf in skills_frequency:
                cur.execute("""
                    INSERT INTO skills_frequency (skill_id, skill_name, frequency, importance_score)
                    VALUES (%s, %s, %s, %s)
                """, (sf["skill_id"], sf["skill_name"], sf["frequency"], sf["importance_score"]))
                
            # Insert Career Patterns
            for cp in career_patterns:
                cur.execute("""
                    INSERT INTO career_patterns (pattern_id, pattern_name, frequency, description)
                    VALUES (%s, %s, %s, %s)
                """, (cp["pattern_id"], cp["pattern_name"], cp["frequency"], cp["description"]))
                
            # Insert Hiring Signals
            for hs in hiring_signals:
                cur.execute("""
                    INSERT INTO hiring_signals (signal_id, signal_name, signal_type, weight, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (hs["signal_id"], hs["signal_name"], hs["signal_type"], hs["weight"], hs["description"]))
                
            conn.commit()
            cur.close()
            print("PostgreSQL tables successfully updated and seed data loaded.")
        except Exception as e:
            print(f"Error executing database transactions: {e}")
            conn.rollback()
        finally:
            conn.close()

    # ----------------------------------------------------------------
    # 7. Write Structured Data to CSV Files
    # ----------------------------------------------------------------
    print("\nWriting updated data to CSV files...")
    
    csv_configs = [
        (os.path.join(EMPLOYEES_DIR, "companies.csv"),           ["company_id", "company_name", "industry", "company_type"],                     list(structured_companies.values())),
        (os.path.join(EMPLOYEES_DIR, "employee_profiles.csv"),   ["profile_id", "name", "role_id", "current_company", "experience_years", "college", "degree", "previous_company", "career_path", "linkedin_url", "github_url", "career_stage", "company_tier"], employee_profiles),
        (os.path.join(EMPLOYEES_DIR, "education_profiles.csv"),  ["education_id", "profile_id", "college", "degree", "field"],                   education_profiles),
        (os.path.join(EMPLOYEES_DIR, "employee_skills.csv"),     ["profile_id", "skill_id"],                                                     employee_skills),
        (os.path.join(EMPLOYEES_DIR, "career_transitions.csv"),  ["transition_id", "profile_id", "source_company_id", "target_company_id"],       career_transitions),
        (os.path.join(EMPLOYEES_DIR, "roles.csv"),               ["role_id", "role_name", "career_level"],                                       role_specializations),
        (os.path.join(CAREER_DIR, "skill_frequency.csv"),        ["skill_id", "skill_name", "frequency", "importance_score"],                     skills_frequency),
        (os.path.join(CAREER_DIR, "career_patterns.csv"),        ["pattern_id", "pattern_name", "frequency", "description"],                     career_patterns),
        (os.path.join(CAREER_DIR, "hiring_signals.csv"),         ["signal_id", "signal_name", "signal_type", "weight", "description"],             hiring_signals)
    ]
    
    for filepath, headers, data in csv_configs:
        try:
            with open(filepath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in data:
                    # Filter only columns defined in headers
                    filtered_row = {k: v for k, v in row.items() if k in headers}
                    writer.writerow(filtered_row)
            print(f"  Saved: {os.path.basename(filepath)} ({len(data)} rows)")
        except Exception as e:
            print(f"  Error saving {os.path.basename(filepath)}: {e}")
            
    print("\nPipeline complete. All CSV files are updated with real-world parsed data.")

if __name__ == "__main__":
    process_pipeline()
