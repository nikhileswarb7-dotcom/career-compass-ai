import urllib.request
import json
import time
import subprocess
import sys

def test_endpoints():
    print("Testing new Career Compass AI endpoints...")
    
    # 1. Test student/analyze
    analyze_payload = {
        "name": "Rahul",
        "linkedin_url": "https://linkedin.com/in/rahul-sharma",
        "github_username": "rahul-sde",
        "resume_text": "Experienced software intern. Tech: Java, Spring Boot, MySQL, Git.",
        "known_skills": ["Java"]
    }
    
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/student/analyze",
            data=json.dumps(analyze_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("[OK] /api/student/analyze responded successfully!")
            print(f"     Extracted skills: {data['extracted_skills']}")
    except Exception as e:
        print(f"[FAIL] /api/student/analyze: {e}")
        
    # 2. Test recommend
    recommend_payload = {
        "name": "Rahul Sharma",
        "qualification": "3rd Year Student",
        "known_skills": ["Java", "SQL"],
        "dream_company": "Blinkit"
    }
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/recommend",
            data=json.dumps(recommend_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("[OK] /api/recommend responded successfully!")
            print(f"     Readiness score: {data['readiness_score']}")
            print(f"     Timeline stages: {len(data['timeline']['stages'])} stages")
    except Exception as e:
        print(f"[FAIL] /api/recommend: {e}")

    # 3. Test roadmap
    roadmap_payload = {
        "qualification": "3rd Year Student",
        "known_skills": ["Java"],
        "dream_company": "Blinkit"
    }
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/roadmap",
            data=json.dumps(roadmap_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("[OK] /api/roadmap responded successfully!")
            print(f"     Timeline urgency: {data.get('urgency')}")
    except Exception as e:
        print(f"[FAIL] /api/roadmap: {e}")

    # 4. Test readiness
    readiness_payload = {
        "known_skills": ["Java", "DBMS"]
    }
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/readiness",
            data=json.dumps(readiness_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("[OK] /api/readiness responded successfully!")
            print(f"     Readiness score: {data.get('readiness_score')}%")
    except Exception as e:
        print(f"[FAIL] /api/readiness: {e}")

    # 5. Test interview-plan
    interview_payload = {
        "known_skills": ["Java"],
        "dream_company": "Blinkit"
    }
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/interview-plan",
            data=json.dumps(interview_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("[OK] /api/interview-plan responded successfully!")
            print(f"     Recommended questions count: {len(data.get('recommended_questions', []))}")
    except Exception as e:
        print(f"[FAIL] /api/interview-plan: {e}")

if __name__ == "__main__":
    test_endpoints()
