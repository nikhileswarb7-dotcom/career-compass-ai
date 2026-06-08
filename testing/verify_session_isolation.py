# Integration Test - Session Isolation
# CareerCompass AI

import requests
import psycopg2

API_BASE = "http://127.0.0.1:8000"

def test_session_isolation():
    print("\nCareerCompass AI - Session Isolation Verification Test")
    print("=" * 60)

    # 1. Onboard User 1 ("Alice Isolation Test")
    payload_1 = {
        "name": "Alice Isolation Test",
        "qualification": "3rd Year Student",
        "branch": "Computer Science",
        "cgpa": 8.5,
        "dream_company": "Google",
        "dream_sector": "SaaS",
        "fresh_passout": False,
        "target_role": "Software Development Engineer",
        "linkedin_url": "",
        "github_username": "",
        "resume_text": "",
        "known_skills": ["Java", "SQL"]
    }

    print("Sending Onboarding 1 for 'Alice Isolation Test'...")
    resp1 = requests.post(f"{API_BASE}/api/student/analyze", json=payload_1)
    assert resp1.status_code == 200, f"Onboarding 1 failed: {resp1.text}"
    res1 = resp1.json()
    student_id_1 = res1.get("student_id")
    session_id_1 = res1.get("session_id")
    print(f"  User 1 -> student_id: {student_id_1}, session_id: {session_id_1}")
    
    assert student_id_1 is not None
    assert session_id_1 is not None

    # Save skills for User 1 using recommend endpoint (skills confirmation stage)
    payload_rec_1 = {
        "name": "Alice Isolation Test",
        "qualification": "3rd Year Student",
        "branch": "Computer Science",
        "cgpa": 8.5,
        "dream_company": "Google",
        "dream_sector": "SaaS",
        "fresh_passout": False,
        "target_role": "Software Development Engineer",
        "known_skills": ["Java", "SQL"],
        "student_id": student_id_1,
        "session_id": session_id_1
    }
    resp_rec1 = requests.post(f"{API_BASE}/api/recommend", json=payload_rec_1)
    assert resp_rec1.status_code == 200, f"Recommend 1 failed: {resp_rec1.text}"

    # Verify User 1 skills in DB
    conn = psycopg2.connect(host="localhost", port=5432, dbname="career_compass_ai", user="postgres", password="Nikhil@2824")
    cur = conn.cursor()
    cur.execute("SET search_path TO career_compass_ai, public;")
    cur.execute("""
        SELECT s.skill_name 
        FROM student_skills ss 
        JOIN skills s ON ss.skill_id = s.skill_id 
        WHERE ss.student_id = %s
    """, (student_id_1,))
    skills_1 = {r[0] for r in cur.fetchall()}
    print(f"  User 1 skills in DB: {skills_1}")
    assert "Java" in skills_1, "Expected Java in User 1 skills"

    # 2. Onboard User 2 with the SAME name ("Alice Isolation Test"), but different skills/qualification
    payload_2 = {
        "name": "Alice Isolation Test",
        "qualification": "1st Year Student",
        "branch": "Computer Science",
        "cgpa": 7.8,
        "dream_company": "Google",
        "dream_sector": "SaaS",
        "fresh_passout": False,
        "target_role": "Software Development Engineer",
        "linkedin_url": "",
        "github_username": "",
        "resume_text": "",
        "known_skills": ["Python"]
    }

    print("\nSending Onboarding 2 for 'Alice Isolation Test' (same name, new session)...")
    resp2 = requests.post(f"{API_BASE}/api/student/analyze", json=payload_2)
    assert resp2.status_code == 200, f"Onboarding 2 failed: {resp2.text}"
    res2 = resp2.json()
    student_id_2 = res2.get("student_id")
    session_id_2 = res2.get("session_id")
    print(f"  User 2 -> student_id: {student_id_2}, session_id: {session_id_2}")
    
    assert student_id_2 is not None
    assert session_id_2 is not None

    # Assert student IDs and session IDs are completely unique
    assert student_id_1 != student_id_2, "Student IDs must be unique to ensure profile isolation!"
    assert session_id_1 != session_id_2, "Session IDs must be unique to ensure workflow isolation!"
    print("  [PASS] Student and Session IDs are unique!")

    # Save skills for User 2
    payload_rec_2 = {
        "name": "Alice Isolation Test",
        "qualification": "1st Year Student",
        "branch": "Computer Science",
        "cgpa": 7.8,
        "dream_company": "Google",
        "dream_sector": "SaaS",
        "fresh_passout": False,
        "target_role": "Software Development Engineer",
        "known_skills": ["Python"],
        "student_id": student_id_2,
        "session_id": session_id_2
    }
    resp_rec2 = requests.post(f"{API_BASE}/api/recommend", json=payload_rec_2)
    assert resp_rec2.status_code == 200, f"Recommend 2 failed: {resp_rec2.text}"

    # Verify User 2 skills in DB (should NOT contain User 1's skills)
    cur.execute("""
        SELECT s.skill_name 
        FROM student_skills ss 
        JOIN skills s ON ss.skill_id = s.skill_id 
        WHERE ss.student_id = %s
    """, (student_id_2,))
    skills_2 = {r[0] for r in cur.fetchall()}
    print(f"  User 2 skills in DB: {skills_2}")
    
    assert "Python" in skills_2, "Expected Python in User 2 skills"
    assert "Java" not in skills_2, "LEAK DETECTED: User 2 inherited User 1's skills!"
    assert "SQL" not in skills_2, "LEAK DETECTED: User 2 inherited User 1's skills!"
    print("  [PASS] User 2 skills are isolated from User 1!")

    # Verify User 1 skills are still intact
    cur.execute("""
        SELECT s.skill_name 
        FROM student_skills ss 
        JOIN skills s ON ss.skill_id = s.skill_id 
        WHERE ss.student_id = %s
    """, (student_id_1,))
    skills_1_post = {r[0] for r in cur.fetchall()}
    print(f"  User 1 skills after User 2 onboarding: {skills_1_post}")
    assert "Java" in skills_1_post
    assert "Python" not in skills_1_post
    print("  [PASS] User 1 skills are intact!")

    cur.close()
    conn.close()
    print("\nALL SESSION ISOLATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_session_isolation()
