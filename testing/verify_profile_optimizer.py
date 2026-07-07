import urllib.request
import json
import os
import sys

def verify_profile_optimizer():
    print("CareerCompass AI — Verify Profile Optimizer Endpoint")
    print("=" * 50)
    
    # Check if backend server is running
    url = "http://127.0.0.1:8000/api/profile/optimize"
    
    payload = {
        "name": "Alex Developer",
        "dream_company": "Blinkit",
        "target_role": "Software Development Engineer (SDE)",
        "project_name": "High-Concurrency Order Dispatching Engine",
        "skills": ["Go", "Redis", "Kafka", "PostgreSQL", "JavaScript"],
        "skip_llm": True
    }
    
    try:
        print(f"Sending POST request to {url}...")
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=60) as res:
            response_code = res.getcode()
            response_data = json.loads(res.read().decode('utf-8'))
            
            print(f"[SUCCESS] Received HTTP {response_code} response!")
            print("-" * 50)
            print(f"Source: {response_data.get('source')}")
            print(f"Name: {response_data.get('name')}")
            print(f"Target Company: {response_data.get('dream_company')}")
            print(f"Target Role: {response_data.get('target_role')}")
            print(f"Project Name: {response_data.get('project_name')}")
            
            # Verify Resume bullets
            bullets = response_data.get("resume_bullets", [])
            print(f"\nResume Bullets ({len(bullets)}):")
            for b in bullets:
                print(f" - {b}")
                
            # Verify LinkedIn summary
            li_summary = response_data.get("linkedin_summary", "")
            print(f"\nLinkedIn Summary (length: {len(li_summary)} chars):")
            print(li_summary[:150] + "...")
            
            # Verify GitHub README
            gh_readme = response_data.get("github_readme", "")
            print(f"\nGitHub README (length: {len(gh_readme)} chars):")
            print(gh_readme[:150] + "...")
            
            # Run schema checks
            errors = []
            if len(bullets) != 4:
                errors.append(f"Expected exactly 4 resume bullets, got {len(bullets)}")
            if not isinstance(li_summary, str) or len(li_summary) == 0:
                errors.append("LinkedIn summary is empty or invalid format")
            if not isinstance(gh_readme, str) or len(gh_readme) == 0:
                errors.append("GitHub README is empty or invalid format")
                
            if errors:
                print("\n[FAIL] Schema validation failed with errors:")
                for err in errors:
                    print(f"  -> {err}")
                sys.exit(1)
            else:
                print("\n[PASS] Schema validation passed successfully!")
                sys.exit(0)
                
    except Exception as e:
        print(f"\n[FAIL] Endpoint request failed: {e}")
        print("Please ensure the FastAPI backend is running on http://127.0.0.1:8000")
        sys.exit(1)

if __name__ == "__main__":
    verify_profile_optimizer()
