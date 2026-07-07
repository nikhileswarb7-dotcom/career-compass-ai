# Run All Submission Tests - CareerCompass AI

import os
import sys
import subprocess
import json

WORKSPACE_DIR = r"c:\Users\nikhi\OneDrive\Desktop\career-compass-ai"
sys.path.append(WORKSPACE_DIR)

TEST_FILES = [
    ("Database & Schema Integrity", "testing/verify_expanded_db.py"),
    ("Phase 2 Roadmap Correctness & Prerequisites", "testing/verify_roadmap_correctness.py"),
    ("Phase 3B Hybrid & ML Inference Fallbacks", "testing/test_hybrid_integration.py"),
    ("Session Flow Validation", "testing/verify_session_flow.py"),
    ("Session Isolation & Concurrency", "testing/verify_session_isolation.py"),
    ("API Endpoint Validation", "testing/verify_endpoints.py"),
    ("Legacy Test Cases (TC001 - TC014)", "testing/run_tests.py")
]

def run_tests():
    print("="*80)
    print("CAREER COMPASS AI — UNIFIED SUBMISSION TEST RUNNER")
    print("="*80)
    
    summary = []
    all_passed = True
    
    for desc, filepath in TEST_FILES:
        print(f"\nRunning: {desc} ({filepath})...")
        full_path = os.path.join(WORKSPACE_DIR, filepath)
        
        # Run process
        try:
            res = subprocess.run(
                [r".venv\Scripts\python.exe", full_path],
                capture_output=True,
                text=True,
                cwd=WORKSPACE_DIR
            )
            success = res.returncode == 0
            if not success:
                all_passed = False
            
            print(f"Result: {'PASS' if success else 'FAIL'} (exit {res.returncode})")
            if not success:
                print(f"Stderr:\n{res.stderr}")
                print(f"Stdout:\n{res.stdout}")
                
            summary.append({
                "test_suite": desc,
                "filepath": filepath,
                "status": "PASS" if success else "FAIL",
                "exit_code": res.returncode
            })
        except Exception as e:
            all_passed = False
            print(f"Error running test {filepath}: {e}")
            summary.append({
                "test_suite": desc,
                "filepath": filepath,
                "status": "ERROR",
                "exit_code": -1
            })
            
    print("\n" + "="*80)
    print("UNIFIED TEST RUNNER SUMMARY")
    print("="*80)
    for s in summary:
        print(f"  {s['test_suite']:50s}: {s['status']}")
    print("="*80)
    
    # Save machine readable summary
    summary_path = os.path.join(WORKSPACE_DIR, "testing", "outputs", "unified_test_summary.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    print(f"Saved machine-readable test summary to {summary_path}")
    
    if all_passed:
        print("All test suites passed successfully!")
    else:
        print("Warning: One or more test suites failed.")

if __name__ == "__main__":
    run_tests()
