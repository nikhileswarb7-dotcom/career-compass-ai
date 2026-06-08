# Profile Vectorizer - CareerCompass AI

import math
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ai_engine.assessment.career_stage_assessor import classify_career_stage

MASTER_SKILLS = [
    "Java", "Go", "Python", "Kafka", "Redis", "PostgreSQL", "Docker", "Kubernetes",
    "gRPC", "Microservices", "Spring Boot", "NodeJS", "AWS", "GCP", "DynamoDB",
    "MySQL", "ElasticSearch", "Django", "React", "TypeScript", "NextJS", "Kotlin",
    "Android", "SRE", "System Design", "Distributed Systems"
]

MASTER_COMPANIES = [
    "Blinkit", "Zomato", "Swiggy", "Paytm", "PhonePe", "Flipkart", 
    "Amazon", "Google", "Microsoft", "Meta", "TCS", "Infosys"
]

MASTER_ROLES = [
    "Software Development Engineer", "Software Development Engineer I (SDE-1)", 
    "Junior Software Engineer", "Trainee Engineer", "QA Automation Engineer", 
    "Backend Engineer", "Frontend Engineer", "SRE / DevOps Engineer", 
    "Mobile Engineer", "AI / ML Engineer"
]

STAGES_LIST = [
    "Foundational / Early Explorer",
    "Core Developer / Intermediate",
    "Advanced / Pre-Placement",
    "Placement Ready / Bootloader",
    "Transitioning Professional"
]

SPECIALIZATIONS = [
    "backend", "frontend", "sre", "ai_ml", "mobile", "qa", "general"
]

def get_specialization(role: str) -> str:
    """
    Classifies a role name into a standard SDE specialization.
    """
    r_low = role.lower().strip() if role else ""
    if "frontend" in r_low:
        return "frontend"
    elif "backend" in r_low:
        return "backend"
    elif "devops" in r_low or "sre" in r_low or "reliability" in r_low:
        return "sre"
    elif "ai" in r_low or "ml" in r_low or "machine learning" in r_low or "intelligence" in r_low:
        return "ai_ml"
    elif "mobile" in r_low or "android" in r_low or "ios" in r_low:
        return "mobile"
    elif "qa" in r_low or "test" in r_low or "automation" in r_low:
        return "qa"
    else:
        return "general"

def vectorize_profile(
    skills: list, 
    company: str, 
    role: str,
    experience_years: float = 0.0,
    gpa: float = 0.0,
    qualification: str = ""
) -> list:
    """
    Transforms profile characteristics (skills list, target company, target role,
    experience, GPA, qualification) into an expanded numerical vector space.
    """
    vector = []
    
    # 1. Skill dimensions (Weight: 2.0)
    skills_set = {s.lower().strip() for s in skills}
    for s in MASTER_SKILLS:
        if s.lower().strip() in skills_set:
            vector.append(2.0)
        else:
            vector.append(0.0)
            
    # 2. Company dimensions (Weight: 1.0)
    company_lower = company.lower().strip() if company else ""
    for c in MASTER_COMPANIES:
        if c.lower().strip() == company_lower:
            vector.append(1.0)
        else:
            vector.append(0.0)
            
    # 3. Role dimensions (Weight: 1.0)
    role_lower = role.lower().strip() if role else ""
    for r in MASTER_ROLES:
        if r.lower().strip() == role_lower or (role_lower in r.lower()) or (r.lower() in role_lower):
            vector.append(1.0)
        else:
            vector.append(0.0)
            
    # 4. Experience Years dimension (Weight: 1.5)
    # Scale: Min 0, Max 1.0 (for 10+ years)
    norm_exp = min(experience_years / 10.0, 1.0)
    vector.append(norm_exp * 1.5)
    
    # 5. GPA dimension (Weight: 1.0)
    # Scale: Min 0, Max 1.0 (for GPA 10 or equivalent)
    norm_gpa = min(gpa / 10.0, 1.0)
    vector.append(norm_gpa * 1.0)
    
    # 6. Career Stage dimensions (Weight: 1.5)
    # One-hot encoding for the 5 career stages
    stage = classify_career_stage(qualification, experience_years)
    for st in STAGES_LIST:
        if st == stage:
            vector.append(1.5)
        else:
            vector.append(0.0)
            
    # 7. Specialization Category dimensions (Weight: 1.5)
    # One-hot encoding for the 7 specializations
    spec = get_specialization(role)
    for sp in SPECIALIZATIONS:
        if sp == spec:
            vector.append(1.5)
        else:
            vector.append(0.0)
            
    return vector

def compute_cosine_similarity(v1: list, v2: list) -> float:
    """
    Calculates the cosine similarity metric between two vector lists.
    """
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(b * b for b in v2))
    
    if magnitude_v1 == 0.0 or magnitude_v2 == 0.0:
        return 0.0
        
    similarity = dot_product / (magnitude_v1 * magnitude_v2)
    return round(float(similarity), 4)
