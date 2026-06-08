# Project Strength Assessor - CareerCompass AI

import re

PROJECT_KEYWORDS = [
    r"projects?", r"applications?", r"systems?", r"engines?", r"platforms?", 
    r"tools?", r"services?", r"microservices?", r"pipelines?", r"apis?"
]

ACTION_VERBS = [
    r"built", r"developed", r"implemented", r"designed", r"optimized", 
    r"created", r"architected", r"integrated", r"deployed", r"wrote",
    r"building", r"developing", r"implementing", r"designing", r"optimizing", 
    r"creating", r"architecting", r"integrating", r"deploying"
]

ADVANCED_KEYWORDS = [
    r"concurrency", r"distributed", r"scale", r"scalable", r"scalability", r"scaling",
    r"latency", r"threads?", r"asynchronous", r"redis", r"kafka", r"grpc",
    r"docker", r"kubernetes", r"aws", r"cloud", r"database tuning", r"indexing",
    r"orchestration", r"containerization"
]

def assess_projects(resume_text: str, student_skills: list) -> float:
    """
    Computes a score (0 to 100) representing Project Strength.
    Scans the resume_text for project indicators, verbs, and technology depth.
    """
    if not resume_text or not resume_text.strip():
        # Fallback if no resume text is provided. Base score on known skills count.
        base_score = 30.0 + min(len(student_skills) * 2.5, 20.0)
        return round(base_score, 1)

    text_lower = resume_text.lower()
    
    # 1. Look for SDE Action Verbs (tells us if they built something)
    verb_matches = 0
    for verb in ACTION_VERBS:
        matches = len(re.findall(r"\b" + verb + r"\b", text_lower))
        verb_matches += matches

    # 2. Look for project identifiers
    proj_matches = 0
    for keyword in PROJECT_KEYWORDS:
        matches = len(re.findall(r"\b" + keyword + r"\b", text_lower))
        proj_matches += matches

    # 3. Look for advanced system engineering keywords
    advanced_matches = 0
    for adv in ADVANCED_KEYWORDS:
        matches = len(re.findall(r"\b" + adv + r"\b", text_lower))
        advanced_matches += matches

    # 4. Count skill matches in the resume
    skills_in_resume = 0
    for skill in student_skills:
        if skill.lower().strip() in text_lower:
            skills_in_resume += 1

    # Scoring Formula:
    # Base: 40 points
    # + Action verbs (up to 20 points, 2 points per match)
    # + Project terms (up to 15 points, 1.5 points per match)
    # + Advanced terms (up to 15 points, 3 points per match)
    # + Skills matched (up to 10 points, 1 point per match)
    score = 40.0
    score += min(verb_matches * 2.0, 20.0)
    score += min(proj_matches * 1.5, 15.0)
    score += min(advanced_matches * 3.0, 15.0)
    score += min(skills_in_resume * 1.0, 10.0)

    # Penalize extremely short text ONLY if it doesn't contain advanced concepts
    if len(resume_text.split()) < 8 and advanced_matches == 0:
        score = min(score, 35.0)

    return min(max(round(score, 1), 0.0), 100.0)
