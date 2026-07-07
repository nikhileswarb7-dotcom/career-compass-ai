# Verification Test for Job Descriptions and Mock Interview Sessions
# CareerCompass AI

import sys
import os
import requests

def test_mock_interview_endpoints():
    print("\nCareerCompass AI - Mock Interview Endpoints Verification")
    print("=" * 60)

    base_url = "http://127.0.0.1:8000"

    # 1. Fetch all job descriptions
    print("1. Fetching available job descriptions...")
    try:
        res = requests.get(f"{base_url}/api/job-descriptions")
        assert res.status_code == 200
        jds = res.json()
        print(f"  [SUCCESS] Successfully retrieved {len(jds)} job descriptions!")
        
        # Verify our newly inserted Swiggy JD (jd_id = 28)
        swiggy_jd = next((j for j in jds if j["jd_id"] == 28), None)
        assert swiggy_jd is not None
        print(f"  [SUCCESS] Found Swiggy Logistics SDE JD (ID 28):")
        print(f"    Company: {swiggy_jd['company_name']}")
        print(f"    Role: {swiggy_jd['role_name']}")
        print(f"    Salary: {swiggy_jd['salary_range']}")
        print(f"    Requirements: {swiggy_jd['requirements']}")
    except Exception as e:
        print(f"  [FAIL] Failed to fetch or validate job descriptions: {e}")
        sys.exit(1)

    # 2. Start mock interview
    print("\n2. Initializing mock interview session (/start)...")
    try:
        payload = {
            "session_id": "test-session-id",
            "jd_id": 28,
            "message": "/start"
        }
        res = requests.post(f"{base_url}/api/chat/interview", json=payload)
        assert res.status_code == 200
        data = res.json()
        print(f"  [SUCCESS] Interview Started!")
        print(f"  Interviewer Response:\n{data.get('reply')}")
        assert data.get("mode") == "interview_started"
    except Exception as e:
        print(f"  [FAIL] Failed to start mock interview: {e}")
        sys.exit(1)

    # 3. Send candidate answer
    print("\n3. Sending candidate response to interviewer...")
    try:
        payload = {
            "session_id": "test-session-id",
            "jd_id": 28,
            "message": "I am a backend engineer. I have strong experience writing concurrent Go microservices, caching telemetry coordinates in Redis, and pushing updates over WebSocket channels."
        }
        res = requests.post(f"{base_url}/api/chat/interview", json=payload)
        assert res.status_code == 200
        data = res.json()
        print(f"  [SUCCESS] Interviewer replied back!")
        print(f"  Interviewer Response:\n{data.get('reply')}")
        assert "reply" in data
    except Exception as e:
        print(f"  [FAIL] Failed to submit response to interviewer: {e}")
        sys.exit(1)

    print("\nMOCK INTERVIEW ENDPOINTS VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_mock_interview_endpoints()
