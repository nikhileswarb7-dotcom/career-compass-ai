# Readiness Score Engine - CareerCompass AI

SKILL_WEIGHTS = {
    "Java": 10,
    "DSA (Combined)": 10,
    "DBMS": 10,
    "Operating Systems": 10,
    "Computer Networks": 10,
    "Spring Boot": 10,
    "System Design": 10,
    "SQL": 5,
    "MySQL": 5,
    "Git & GitHub": 5,
    "Low Level Design": 5,
    "High Level Design": 5,
    "Object Oriented Programming": 5,
    "REST APIs": 5,
    "Docker": 2,
    "Redis": 2,
    "Microservices": 2
}

TOTAL_WEIGHT = sum(SKILL_WEIGHTS.values())

def calculate_readiness(matched_skills: list[str]) -> int:
    """
    Calculates the readiness score out of 100 based on matched skills.
    """
    matched_set = {s.lower() for s in matched_skills}
    score_weight = sum(w for s, w in SKILL_WEIGHTS.items() if s.lower() in matched_set)
    
    return int((score_weight / TOTAL_WEIGHT) * 100)
