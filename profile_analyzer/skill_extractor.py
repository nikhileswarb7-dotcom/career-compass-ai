# Skill Extractor & Normalizer - CareerCompass AI

class SkillExtractor:
    """
    Standardizes raw text skills, normalizing synonyms and mapping them
    to standard curriculum skills defined in the SDE syllabus.
    """
    
    SKILL_MAPPING = {
        "dsa": "DSA (Combined)",
        "data structures": "DSA (Combined)",
        "algorithms": "DSA (Combined)",
        "data structure": "DSA (Combined)",
        "os": "Operating Systems",
        "operating system": "Operating Systems",
        "operating systems": "Operating Systems",
        "cn": "Computer Networks",
        "computer network": "Computer Networks",
        "computer networks": "Computer Networks",
        "oop": "Object Oriented Programming",
        "object oriented": "Object Oriented Programming",
        "object oriented programming": "Object Oriented Programming",
        "oops": "Object Oriented Programming",
        "git": "Git & GitHub",
        "github": "Git & GitHub",
        "git & github": "Git & GitHub",
        "lld": "Low Level Design",
        "low level design": "Low Level Design",
        "hld": "High Level Design",
        "high level design": "High Level Design",
        "system design": "System Design",
        "restful": "REST APIs",
        "rest api": "REST APIs",
        "rest apis": "REST APIs",
        "spring": "Spring Boot",
        "springboot": "Spring Boot",
        "spring boot": "Spring Boot",
        "dbms": "DBMS",
        "database management": "DBMS",
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "redis": "Redis",
        "kafka": "Kafka",
        "docker": "Docker",
        "microservices": "Microservices",
        "microservice": "Microservices",
        "kubernetes": "Kubernetes",
        "grpc": "gRPC",
        "nodejs": "NodeJS",
        "node": "NodeJS",
        "java": "Java",
        "go": "Go",
        "golang": "Go",
        "python": "Python",
        "aws": "AWS"
    }

    @classmethod
    def extract_and_normalize(cls, raw_skills: list[str]) -> list[str]:
        if not raw_skills:
            return []
            
        normalized = set()
        for skill in raw_skills:
            s_clean = skill.strip().lower()
            if s_clean in cls.SKILL_MAPPING:
                normalized.add(cls.SKILL_MAPPING[s_clean])
            else:
                # Add title cased if not mapped explicitly
                normalized.add(skill.strip().title())
                
        return sorted(list(normalized))
