"""
CareerCompass AI — Test Runner
Runs all test cases against the recommendation engine and NLP processor.

Usage:
    python run_tests.py
"""

import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ai_engine"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ai_engine", "nlp"))

from recommendation_engine import generate_recommendation
from nlp_processor import parse_user_input

TEST_FILE = os.path.join(os.path.dirname(__file__), "test_cases", "test_cases.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "outputs", "test_results.json")


def run_tests():
    with open(TEST_FILE) as f:
        test_cases = json.load(f)

    results = []
    passed = 0
    failed = 0

    print("\nCareerCompass AI — Test Runner")
    print("=" * 50)

    for tc in test_cases:
        test_id = tc["test_id"]
        desc = tc["description"]

        # NLP test
        if "nlp_input" in tc:
            parsed = parse_user_input(tc["nlp_input"])
            expected = tc["expected_parse"]

            errors = []
            if expected.get("qualification") and parsed["qualification"] != expected["qualification"]:
                errors.append(f"qualification: expected '{expected['qualification']}', got '{parsed['qualification']}'")

            for skill in expected.get("known_skills_should_include", []):
                if skill not in parsed["known_skills"]:
                    errors.append(f"missing skill: '{skill}' not extracted")

            if expected.get("target_company") and parsed["target_company"] != expected["target_company"]:
                errors.append(f"company: expected '{expected['target_company']}', got '{parsed['target_company']}'")

            status = "PASS" if not errors else "FAIL"
            result_entry = {
                "test_id": test_id,
                "type": "NLP",
                "description": desc,
                "status": status,
                "errors": errors,
                "parsed_output": parsed,
            }

        # Recommendation test
        elif "input" in tc:
            rec = generate_recommendation(
                qualification=tc["input"]["qualification"],
                known_skills=tc["input"]["known_skills"]
            )
            expected = tc["expected"]

            errors = []
            score = rec["assessment"]["readiness_score"]
            score_range = expected.get("readiness_score_range", [0, 100])
            if not (score_range[0] <= score <= score_range[1]):
                errors.append(f"score {score} not in expected range {score_range}")

            high_missing = rec["gaps"]["high_priority_missing"]
            for skill in expected.get("high_priority_skills_should_include", []):
                if skill not in high_missing:
                    errors.append(f"expected '{skill}' in high priority missing, but not found")

            if expected.get("urgency") and rec["urgency_level"] != expected["urgency"]:
                errors.append(f"urgency: expected '{expected['urgency']}', got '{rec['urgency_level']}'")

            status = "PASS" if not errors else "FAIL"
            result_entry = {
                "test_id": test_id,
                "type": "Recommendation",
                "description": desc,
                "status": status,
                "readiness_score": score,
                "errors": errors,
                "output_summary": {
                    "readiness_score": score,
                    "urgency": rec["urgency_level"],
                    "months_to_ready": rec["next_steps"]["estimated_months_to_ready"],
                    "top_missing": rec["gaps"]["high_priority_missing"],
                    "message": rec["message"],
                }
            }
        else:
            continue

        results.append(result_entry)
        if status == "PASS":
            passed += 1
            print(f"  [PASS] {test_id}: {desc}")
        else:
            failed += 1
            print(f"  [FAIL] {test_id}: {desc}")
            for err in errors:
                print(f"      -> {err}")

    # Save results
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(results)} tests")
    print(f"Output saved to: {OUTPUT_FILE}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
