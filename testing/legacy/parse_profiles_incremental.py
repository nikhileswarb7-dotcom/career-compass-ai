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
DB_DIR = os.path.join(BASE_DIR, "database")

# Layer Directories
INDUSTRY_DIR = os.path.join(DB_DIR, "industry_layer")
CAREER_DIR = os.path.join(DB_DIR, "career_layer")

RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")

# ----------------------------------------------------------------
# 1. Database Connection Config loader
# ----------------------------------------------------------------
def load_db_config():
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from api.database_connector import DB_CONFIG
    return DB_CONFIG

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
    lines = [line for line in lines if line]
    
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
# 3. CSV Append Helper
# ----------------------------------------------------------------
def append_to_csv(filename, headers, rows):
    filepath = os.path.join(INDUSTRY_DIR, filename)
    file_exists = os.path.exists(filepath)
    with open(filepath, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)

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

def run_pdf_incremental_parser():
    print("\nCareerCompass AI — Incremental PDF Profile Parser")
    print("=" * 60)
    
    # Scan raw_data for PDFs
    pdf_files = []
    for root, dirs, files in os.walk(RAW_DATA_DIR):
        for f in files:
            if f.endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))
                
    if not pdf_files:
        print("No PDF files found in raw_data/. Please add profiles and try again.")
        return
        
    print(f"Found {len(pdf_files)} PDF profiles to parse. Extracting...")
    
    # Load existing profile names to prevent duplicate parsing
    existing_profiles_path = os.path.join(INDUSTRY_DIR, "employee_profiles.csv")
    existing_names = set()
    next_profile_id = 1
    
    if os.path.exists(existing_profiles_path):
        with open(existing_profiles_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_names.add(row['name'].strip().lower())
                next_profile_id = max(next_profile_id, int(row['profile_id']) + 1)
                
    # Load skills master to map parsed skills
    skills_csv_path = os.path.join(CAREER_DIR, "skills_master.csv")
    skills_master = {}
    if os.path.exists(skills_csv_path):
        with open(skills_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skills_master[row['skill_name'].lower()] = int(row['skill_id'])
                
    new_profiles = []
    new_skills = []
    
    for filepath in pdf_files:
        try:
            profile = parse_profile_pdf(filepath)
            if profile["name"] and profile["name"].strip().lower() not in existing_names:
                profile_id = next_profile_id
                next_profile_id += 1
                
                # Determine target company based on folder
                folder_name = os.path.basename(os.path.dirname(filepath)).upper()
                target_company = "Blinkit"
                if "AMAZON" in folder_name:
                    target_company = "Amazon"
                elif "MICROSOFT" in folder_name:
                    target_company = "Microsoft"
                
                # Find current role and experience years
                exp_list = profile["experience"]
                total_months = sum(e["duration_months"] for e in exp_list)
                exp_years = round(total_months / 12.0, 1)
                
                role = "SDE"
                if exp_list:
                    role = exp_list[-1]["role"]
                    
                prev_comp = exp_list[-2]["company"] if len(exp_list) > 1 else ""
                c_path = f"{prev_comp}->{target_company}" if prev_comp else f"Campus->{target_company}"
                
                college = profile["education"][0]["college"] if profile["education"] else ""
                degree = profile["education"][0]["degree"] if profile["education"] else ""
                
                # Determine career_stage based on experience_years
                if exp_years == 0.0:
                    career_stage = "Foundational"
                elif exp_years < 2.0:
                    career_stage = "Entry"
                elif exp_years < 5.0:
                    career_stage = "Mid"
                else:
                    career_stage = "Senior"

                # Determine company_tier based on target_company
                comp_clean = target_company.lower().strip() if target_company else ""
                tier_1 = ["google", "microsoft", "meta", "amazon", "blinkit", "zomato", "swiggy", "phonepe"]
                tier_3 = ["tcs", "infosys", "wipro", "cognizant", "accenture"]
                
                if any(x in comp_clean for x in tier_1):
                    company_tier = 1
                elif any(x in comp_clean for x in tier_3):
                    company_tier = 3
                else:
                    company_tier = 2

                # Retrieve linkedin_url and github_url from profile if available
                linkedin_url_val = profile.get("linkedin_url") or ""
                github_url_val = profile.get("github_url") or ""

                new_profiles.append({
                    "profile_id": profile_id,
                    "name": profile["name"],
                    "role_id": map_role_to_id(role),
                    "current_company": target_company,
                    "experience_years": exp_years,
                    "college": college,
                    "degree": degree,
                    "previous_company": prev_comp,
                    "career_path": c_path,
                    "linkedin_url": linkedin_url_val,
                    "github_url": github_url_val,
                    "career_stage": career_stage,
                    "company_tier": company_tier
                })
                
                # Map skills
                for s in profile["skills"]:
                    s_low = s.lower()
                    if s_low in skills_master:
                        new_skills.append({
                            "profile_id": profile_id,
                            "skill_id": skills_master[s_low]
                        })
                
                existing_names.add(profile["name"].strip().lower())
                print(f"  Parsed & Added: {profile['name']}")
        except Exception as e:
            print(f"  Error parsing {os.path.basename(filepath)}: {e}")
            
    if new_profiles:
        append_to_csv("employee_profiles.csv", 
                      ["profile_id", "name", "role_id", "current_company", "experience_years", "college", "degree", "previous_company", "career_path", "linkedin_url", "github_url", "career_stage", "company_tier"], 
                      new_profiles)
        append_to_csv("employee_skills.csv", ["profile_id", "skill_id"], new_skills)
        print(f"\nSuccessfully added {len(new_profiles)} new profiles to the CSV datasets!")
    else:
        print("\nNo new unique profiles found to append.")

if __name__ == "__main__":
    run_pdf_incremental_parser()
