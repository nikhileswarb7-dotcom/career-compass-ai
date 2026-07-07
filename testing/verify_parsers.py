# Verification Test for Profile Parsers
# CareerCompass AI

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from profile_analyzer.skill_extractor import SkillExtractor
from profile_analyzer.resume_parser import ResumeParser
from profile_analyzer.linkedin_parser import LinkedInParser
from profile_analyzer.github_analyzer import GitHubAnalyzer

def verify_all_parsers():
    print("\nCareerCompass AI - Profile Parsers Verification Suite")
    print("=" * 60)

    # 1. Verify SkillExtractor
    print("Testing SkillExtractor...")
    raw_list = ["java", "git", "lld", "system design", "K8s", "c++", "unknown_tech"]
    normalized = SkillExtractor.extract_and_normalize(raw_list)
    print(f"  Raw: {raw_list}")
    print(f"  Normalized: {normalized}")
    
    assert "Java" in normalized
    assert "Git & GitHub" in normalized
    assert "Low Level Design" in normalized
    assert "System Design" in normalized
    assert "Kubernetes" in normalized
    assert "C++" in normalized
    assert "Unknown_Tech" in normalized
    print("  [PASS] SkillExtractor checks passed!")

    # 2. Verify ResumeParser
    print("\nTesting ResumeParser...")
    resume_text = """
    Alex Developer
    Email: alex.developer@example.com
    CGPA: 8.5
    Education: B.Tech Computer Science and Engineering
    
    Experience:
    Software Engineering Intern at Startup. Worked with Java and MySQL database schemas.
    
    Projects:
    Built a high-performance HTTP gateway using Go, Redis caching, and Kafka.
    Utilized Git & GitHub for version control and docker for deployments.
    
    Skills:
    C++, Python, OOP, LLD, REST APIs
    """
    
    parsed_resume = ResumeParser.parse_resume(resume_text)
    print(f"  Parsed Name: {parsed_resume.get('name')}")
    print(f"  Parsed Email: {parsed_resume.get('email')}")
    print(f"  Parsed CGPA: {parsed_resume.get('cgpa')}")
    print(f"  Extracted Skills count: {len(parsed_resume.get('skills_raw', []))}")
    print(f"  Extracted Skills: {parsed_resume.get('skills_raw')}")
    
    assert parsed_resume.get("email") == "alex.developer@example.com"
    assert parsed_resume.get("cgpa") == 8.5
    extracted_skills = parsed_resume.get("skills_raw", [])
    assert "Java" in extracted_skills
    assert "MySQL" in extracted_skills
    assert "Go" in extracted_skills
    assert "Redis" in extracted_skills
    assert "Message Queues (Kafka)" in extracted_skills
    assert "Git & GitHub" in extracted_skills
    assert "Docker" in extracted_skills
    print("  [PASS] ResumeParser checks passed!")

    # 3. Verify LinkedInParser
    print("\nTesting LinkedInParser...")
    # Mock text matching standard LinkedIn format
    linkedin_text = """
    Alex Developer
    Headline: Software Development Engineer Intern
    Summary: Passionate about backend engineering, microservices, and system design.
    Experience:
    Google - SDE Intern
    - Worked on Spring Boot backend services and PostgreSQL queries.
    """
    
    parsed_linkedin = LinkedInParser.parse_profile(linkedin_text)
    print(f"  Parsed Headline: {parsed_linkedin.get('headline')}")
    print(f"  Parsed Current Role: {parsed_linkedin.get('current_role')}")
    print(f"  Extracted LinkedIn Skills: {parsed_linkedin.get('skills_raw')}")
    
    linkedin_skills = parsed_linkedin.get("skills_raw", [])
    assert "Spring Boot" in linkedin_skills
    assert "PostgreSQL" in linkedin_skills
    assert "System Design" in linkedin_skills
    assert "Microservices" in linkedin_skills
    print("  [PASS] LinkedInParser checks passed!")

    # 4. Verify GitHubAnalyzer
    print("\nTesting GitHubAnalyzer...")
    # Test handle extraction
    handle_url = "https://github.com/alexdeveloper"
    extracted_handle = GitHubAnalyzer.extract_handle(handle_url)
    print(f"  URL: {handle_url} -> Extracted Handle: {extracted_handle}")
    assert extracted_handle == "alexdeveloper"
    
    # Test graceful failure / error handling for nonexistent users or rate limiting
    bad_profile = GitHubAnalyzer.analyze_profile("nonexistent_user_xyz_123")
    print(f"  Invalid User -> Source: {bad_profile.get('source')}")
    print(f"  Invalid User -> Error: {bad_profile.get('error')}")
    assert "error" in bad_profile or "source" in bad_profile
    print("  [PASS] GitHubAnalyzer checks passed!")

    print("\nALL PARSER AND PROFILE VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_all_parsers()
