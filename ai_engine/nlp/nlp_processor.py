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
    "Software Development Engineer (SDE)": [
        r"\bsde\b", r"\bsoftware\s?development\s?engineer\b"
    ],
    "Backend Developer": [
        r"\bbackend\b", r"\bbackend\s?developer\b", r"\bbackend\s?engineer\b"
    ],
    "Frontend Developer": [
        r"\bfrontend\b", r"\bfrontend\s?developer\b", r"\bfrontend\s?engineer\b"
    ],
    "Full Stack Developer": [
        r"\bfull\s?stack\b", r"\bfullstack\b", r"\bfull\s?stack\s?developer\b", r"\bfull\s?stack\s?engineer\b"
    ],
    "Software Engineer": [
        r"\bsoftware\s?engineer\b", r"\bsoftware\s?developer\b"
    ],
    "Mobile App Developer (Android)": [
        r"\bandroid\b", r"\bandroid\s?developer\b", r"\bandroid\s?engineer\b"
    ],
    "Mobile App Developer (iOS)": [
        r"\bios\b", r"\bios\s?developer\b", r"\bios\s?engineer\b"
    ],
    "Flutter Developer": [
        r"\bflutter\b", r"\bflutter\s?developer\b"
    ],
    "React Native Developer": [
        r"\breact\s?native\b", r"\breact\s?native\s?developer\b"
    ],
    "DevOps Engineer": [
        r"\bdevops\b", r"\bdevops\s?engineer\b"
    ],
    "Cloud Engineer": [
        r"\bcloud\s?engineer\b", r"\bcloud\s?developer\b"
    ],
    "Site Reliability Engineer (SRE)": [
        r"\bsre\b", r"\bsite\s?reliability\b", r"\bsite\s?reliability\s?engineer\b"
    ],
    "Data Analyst": [
        r"\bdata\s?analyst\b"
    ],
    "Data Engineer": [
        r"\bdata\s?engineer\b"
    ],
    "Data Scientist": [
        r"\bdata\s?scientist\b"
    ],
    "AI Engineer": [
        r"\bai\s?engineer\b", r"\bai\s?developer\b", r"\bartificial\s?intelligence\b"
    ],
    "Machine Learning Engineer": [
        r"\bml\s?engineer\b", r"\bml\s?developer\b", r"\bmachine\s?learning\b", r"\bmachine\s?learning\s?engineer\b"
    ],
    "Deep Learning Engineer": [
        r"\bdeep\s?learning\b", r"\bdeep\s?learning\s?engineer\b"
    ],
    "NLP Engineer": [
        r"\bnlp\b", r"\bnlp\s?engineer\b", r"\bnatural\s?language\s?processing\b"
    ],
    "Computer Vision Engineer": [
        r"\bcomputer\s?vision\b", r"\bcomputer\s?vision\s?engineer\b"
    ],
    "MLOps Engineer": [
        r"\bmlops\b", r"\bmlops\s?engineer\b"
    ],
    "Cyber Security Engineer": [
        r"\bcyber\s?security\b", r"\bcyber\s?security\s?engineer\b", r"\bsecurity\s?engineer\b"
    ],
    "Security Analyst": [
        r"\bsecurity\s?analyst\b"
    ],
    "SDET (Software Development Engineer in Test)": [
        r"\bsdet\b", r"\bsoftware\s?development\s?engineer\s?in\s?test\b"
    ],
    "QA Automation Engineer": [
        r"\bqa\b", r"\bqa\s?automation\b", r"\bautomation\s?engineer\b", r"\bqa\s?engineer\b"
    ],
    "Product Manager": [
        r"\bproduct\s?manager\b", r"\bpm\b"
    ],
    "Associate Product Manager (APM)": [
        r"\bapm\b", r"\bassociate\s?product\s?manager\b"
    ],
    "Business Analyst": [
        r"\bbusiness\s?analyst\b"
    ],
    "UI/UX Designer": [
        r"\bui\/ux\b", r"\bui\s?ux\b", r"\bdesigner\b", r"\bui\s?designer\b", r"\bux\s?designer\b"
    ],
    "Embedded Software Engineer": [
        r"\bembedded\b", r"\bembedded\s?engineer\b", r"\bembedded\s?software\s?engineer\b"
    ]
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
            "target_role": "Software Development Engineer (SDE)",
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
        "target_role": role or "Software Development Engineer (SDE)",
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
