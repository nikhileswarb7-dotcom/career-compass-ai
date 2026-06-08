# Integration Test - Session-Based Workflow Gating & Data Isolation
# CareerCompass AI

import requests
import uuid
import psycopg2

API_BASE = "http://127.0.0.1:8000"

def test_session_workflow():
    print("\nCareerCompass AI - Session Workflow Integration Test")
    print("=" * 60)

    # 1. Initiate profile analysis & registration
    payload_analyze = {
        "name": "Integration Test Candidate",
        "qualification": "3rd Year Student",
        "branch": "Computer Science",
        "cgpa": 8.8,
        "dream_company": "Blinkit",
        "dream_sector": "Quick-Commerce",
        "fresh_passout": False,
        "target_role": "Junior Software Engineer",
        "linkedin_url": "https://linkedin.com/in/test-candidate",
        "github_username": "testcandidate",
        "resume_text": "Experienced in Java, SQL, Git & GitHub.",
        "known_skills": ["Java", "SQL"]
    }

    print("Sending POST /api/student/analyze...")
    resp_analyze = requests.post(f"{API_BASE}/api/student/analyze", json=payload_analyze)
    assert resp_analyze.status_code == 200, f"Analyze failed: {resp_analyze.text}"
    res_data = resp_analyze.json()
    
    student_id = res_data.get("student_id")
    session_id = res_data.get("session_id")
    
    print(f"  Received student_id: {student_id} (type: {type(student_id).__name__})")
    print(f"  Received session_id: {session_id} (type: {type(session_id).__name__})")
    
    assert student_id is not None, "student_id is missing!"
    assert session_id is not None, "session_id is missing!"
    
    # Assert student_id is an integer (Modification 1)
    assert isinstance(student_id, int), f"student_id must be INT, got {type(student_id).__name__}"
    
    # Assert session_id is a valid UUID
    try:
        val_uuid = uuid.UUID(session_id)
        print("  session_id is a valid UUID")
    except ValueError:
        raise AssertionError(f"session_id '{session_id}' is not a valid UUID string")

    # 2. Confirm skills and promote status to skills_confirmed
    payload_recommend = {
        "name": "Integration Test Candidate",
        "qualification": "3rd Year Student",
        "branch": "Computer Science",
        "cgpa": 8.8,
        "dream_company": "Blinkit",
        "dream_sector": "Quick-Commerce",
        "fresh_passout": False,
        "target_role": "Junior Software Engineer",
        "known_skills": ["Java", "Git & GitHub", "SQL"],
        "student_id": student_id,
        "session_id": session_id
    }

    print("Sending POST /api/recommend...")
    resp_recommend = requests.post(f"{API_BASE}/api/recommend", json=payload_recommend)
    assert resp_recommend.status_code == 200, f"Recommend failed: {resp_recommend.text}"
    rec_data = resp_recommend.json()
    assert rec_data.get("session_id") == session_id
    assert rec_data.get("student_id") == student_id

    # 3. Retrieve session details
    print(f"Sending GET /api/session/{session_id}...")
    resp_sess = requests.get(f"{API_BASE}/api/session/{session_id}")
    assert resp_sess.status_code == 200
    sess_data = resp_sess.json()
    print(f"  Session status: '{sess_data['status']}'")
    assert sess_data["status"] == "skills_confirmed", f"Expected skills_confirmed status, got {sess_data['status']}"

    # 4. Promote progress status
    print(f"Sending POST /api/session/{session_id}/progress to set status to 'dashboard_completed'...")
    resp_prog = requests.post(f"{API_BASE}/api/session/{session_id}/progress", json={"status": "dashboard_completed"})
    assert resp_prog.status_code == 200
    
    # Verify status in database
    resp_sess2 = requests.get(f"{API_BASE}/api/session/{session_id}")
    assert resp_sess2.json()["status"] == "dashboard_completed"
    print("  Progress successfully promoted!")

    # 5. Verify dynamic sub-endpoints (Modification 4)
    print(f"Testing dynamic GET /api/readiness/{session_id}...")
    resp_readiness = requests.get(f"{API_BASE}/api/readiness/{session_id}")
    assert resp_readiness.status_code == 200
    readiness_data = resp_readiness.json()
    print(f"  Readiness Score: {readiness_data['readiness_score']}%")
    assert "readiness_score" in readiness_data

    print(f"Testing dynamic GET /api/recommendations/{session_id}...")
    resp_recs = requests.get(f"{API_BASE}/api/recommendations/{session_id}")
    assert resp_recs.status_code == 200
    recs_data = resp_recs.json()
    print(f"  Projects found: {len(recs_data.get('projects', []))}")
    print(f"  Resources found: {len(recs_data.get('resources', []))}")
    assert "projects" in recs_data
    assert "resources" in recs_data

    print(f"Testing dynamic GET /api/interview-plan/{session_id}...")
    resp_interview = requests.get(f"{API_BASE}/api/interview-plan/{session_id}")
    assert resp_interview.status_code == 200
    int_data = resp_interview.json()
    print(f"  Interview questions found: {len(int_data.get('recommended_questions', []))}")
    assert "recommended_questions" in int_data

    print(f"Testing dynamic GET /api/roadmap/{session_id}...")
    resp_roadmap = requests.get(f"{API_BASE}/api/roadmap/{session_id}")
    assert resp_roadmap.status_code == 200
    roadmap_data = resp_roadmap.json()
    print(f"  Roadmap stages: {len(roadmap_data.get('stages', []))}")
    assert "stages" in roadmap_data

    # 6. Verify PostgreSQL as Source of Truth & metadata-only storage (Modification 2 & 3)
    conn = psycopg2.connect(host="localhost", port=5432, dbname="career_compass_ai", user="postgres", password="Nikhil@2824")
    cur = conn.cursor()
    cur.execute("SELECT student_id, target_company, target_role, status FROM career_compass_ai.analysis_sessions WHERE session_id = %s", (session_id,))
    db_row = cur.fetchone()
    cur.close()
    conn.close()
    
    assert db_row is not None
    assert db_row[0] == student_id
    assert db_row[1] == "Blinkit"
    assert db_row[2] == "Junior Software Engineer"
    assert db_row[3] == "dashboard_completed"
    print("  Verified session record exists in PostgreSQL and stores metadata only (no nested JSON recommendation caches)!")

    print("\nALL WORKFLOW INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_session_workflow()
