"""
CareerCompass AI — NLP Processor
Extracts: qualification, known skills, target company, target role
from free-text user input.

Uses rule-based NLP (no external API needed).
Optional: can be upgraded with spaCy later.
"""

import re


# ----------------------------------------------------------------
# Known entity lists
# ----------------------------------------------------------------

QUALIFICATION_PATTERNS = {
    "1st Year Student":         [r"\b1st\s?year\b", r"\bfirst\s?year\b", r"\byear\s?1\b"],
    "2nd Year Student":         [r"\b2nd\s?year\b", r"\bsecond\s?year\b", r"\byear\s?2\b"],
    "3rd Year Student":         [r"\b3rd\s?year\b", r"\bthird\s?year\b", r"\byear\s?3\b"],
    "4th Year Student":         [r"\b4th\s?year\b", r"\bfourth\s?year\b", r"\bfinal\s?year\b", r"\byear\s?4\b"],
    "Fresh Graduate":           [r"\bfresh\s?grad(uate)?\b", r"\bjust\s?graduated\b", r"\brecently\s?graduated\b", r"\bnew\s?grad(uate)?\b", r"\bgraduate\b"],
    "Trainee Engineer":         [r"\btrainee\b", r"\btraining\b"],
    "Junior Software Engineer": [r"\bjunior\b", r"\bjunior\s?(software|developer|engineer|sde)\b", r"\b[12]\s?year[s]?\s?(experience|exp)\b"],
}

KNOWN_SKILLS_LIST = [
    "C Programming", "C++", "Java", "Python", "SQL",
    "Data Structures", "Algorithms", "DSA", "DSA (Combined)",
    "DBMS", "Operating Systems", "OS", "Computer Networks", "CN",
    "Object Oriented Programming", "OOP",
    "Spring Boot", "REST APIs", "Microservices", "Message Queues",
    "Kafka", "MySQL", "PostgreSQL", "Redis",
    "Git", "Git & GitHub", "Docker", "AWS", "Linux",
    "Low Level Design", "LLD", "High Level Design", "HLD", "System Design",
]

# Alias normalization: maps abbreviations/alternate names to canonical skill name
SKILL_ALIASES = {
    "dsa":                  "DSA (Combined)",
    "data structures":      "DSA (Combined)",
    "algorithms":           "DSA (Combined)",
    "data structure":       "DSA (Combined)",
    "os":                   "Operating Systems",
    "operating system":     "Operating Systems",
    "cn":                   "Computer Networks",
    "computer network":     "Computer Networks",
    "oop":                  "Object Oriented Programming",
    "object oriented":      "Object Oriented Programming",
    "oops":                 "Object Oriented Programming",
    "git":                  "Git & GitHub",
    "github":               "Git & GitHub",
    "lld":                  "Low Level Design",
    "hld":                  "High Level Design",
    "kafka":                "Message Queues (Kafka)",
    "message queue":        "Message Queues (Kafka)",
    "restful":              "REST APIs",
    "rest api":             "REST APIs",
}

COMPANY_PATTERNS = {
    "Blinkit": [r"\bblinkit\b", r"\bgrofers\b"],
    "Google":  [r"\bgoogle\b"],
    "Amazon":  [r"\bamazon\b", r"\baws company\b"],
    "Zomato":  [r"\bzomato\b"],
}

ROLE_PATTERNS = {
    "Software Development Engineer": [
        r"\bsde\b", r"\bsoftware\s?development\s?engineer\b",
        r"\bsoftware\s?engineer\b", r"\bbackend\s?engineer\b",
        r"\bsoftware\s?developer\b"
    ],
}


# ----------------------------------------------------------------
# Extraction functions
# ----------------------------------------------------------------

def extract_qualification(text: str) -> str | None:
    """Detect which qualification level the user belongs to."""
    text_lower = text.lower()
    for qual, patterns in QUALIFICATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return qual
    return None


def extract_skills(text: str) -> list[str]:
    """Extract known skills from user text."""
    text_lower = text.lower()
    found_skills = set()

    # Direct alias match
    for alias, canonical in SKILL_ALIASES.items():
        if alias in text_lower:
            found_skills.add(canonical)

    # Full skill name match
    for skill in KNOWN_SKILLS_LIST:
        if skill.lower() in text_lower:
            canonical = SKILL_ALIASES.get(skill.lower(), skill)
            found_skills.add(canonical)

    return sorted(found_skills)


def extract_company(text: str) -> str | None:
    """Detect which company the user is targeting."""
    text_lower = text.lower()
    for company, patterns in COMPANY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return company
    return None


def extract_role(text: str) -> str | None:
    """Detect which role the user is targeting."""
    text_lower = text.lower()
    for role, patterns in ROLE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return role
    return None


def parse_user_input(text: str) -> dict:
    """
    Main NLP function: parse free-text user query into structured profile.

    Example input:
        "I'm a 3rd year student. I know Java and Git. I want to become SDE at Blinkit."

    Example output:
        {
            "qualification": "3rd Year Student",
            "known_skills": ["Git & GitHub", "Java"],
            "target_company": "Blinkit",
            "target_role": "Software Development Engineer",
            "missing_entities": []
        }
    """
    qualification = extract_qualification(text)
    skills = extract_skills(text)
    company = extract_company(text)
    role = extract_role(text)

    missing = []
    if not qualification:
        missing.append("qualification")
    if not company:
        missing.append("target_company")
    if not role:
        missing.append("target_role")

    return {
        "qualification": qualification,
        "known_skills": skills,
        "target_company": company or "Blinkit",
        "target_role": role or "Software Development Engineer",
        "missing_entities": missing,
        "raw_input": text,
    }


def generate_clarification_message(parsed: dict) -> str | None:
    """
    If key info is missing, ask the user for it.
    Returns None if all required fields are present.
    """
    if not parsed["missing_entities"]:
        return None

    messages = []
    if "qualification" in parsed["missing_entities"]:
        messages.append(
            "What is your current qualification? "
            "(1st Year, 2nd Year, 3rd Year, 4th Year, Fresh Graduate, Trainee Engineer, Junior Software Engineer)"
        )

    return "\n".join(messages)


# ----------------------------------------------------------------
# Demo
# ----------------------------------------------------------------

if __name__ == "__main__":
    test_inputs = [
        "I'm a 3rd year student. I know Java and Git. I want to become SDE at Blinkit.",
        "I am in second year. I know python and OOP.",
        "Just graduated. Know Java, Spring Boot, MySQL, Redis. Looking for SDE roles at Blinkit.",
        "Trainee at a startup. Know java and rest apis. Want to switch to product company.",
        "I'm a first year student. I know C programming and Python. Target: SDE at Blinkit.",
    ]

    for text in test_inputs:
        print(f"\nInput: {text}")
        result = parse_user_input(text)
        print(f"Parsed: {result}")
        clarify = generate_clarification_message(result)
        if clarify:
            print(f"Clarification needed: {clarify}")
