import os
import json
import csv
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from ai_engine.recommendation_engine import generate_recommendation

def verify_all():
    print("\n" + "="*50)
    print("CAREERCOMPASS AI — EXPANDED DATABASE VERIFIER")
    print("="*50)
    
    # 1. Verify roles.csv
    role_spec_path = os.path.join(BASE_DIR, "database", "industry_layer", "roles.csv")
    assert os.path.exists(role_spec_path), "roles.csv missing!"
    with open(role_spec_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        roles = list(reader)
    print(f"[OK] roles.csv exists: {len(roles)} master roles found (expected 30).")
    assert len(roles) == 30, f"Expected 30 roles, got {len(roles)}"
    
    # 2. Verify employee_profiles.csv
    profiles_path = os.path.join(BASE_DIR, "database", "industry_layer", "employee_profiles.csv")
    assert os.path.exists(profiles_path), "employee_profiles.csv missing!"
    with open(profiles_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        profiles = list(reader)
    print(f"[OK] employee_profiles.csv exists: {len(profiles)} profiles found (expected >= 121).")
    assert len(profiles) >= 121, f"Expected at least 121 profiles, got {len(profiles)}"
    
    # Check if role_id is valid
    role_ids = {int(r["role_id"]) for r in roles}
    for p in profiles:
        assert "role_id" in p, "role_id column missing in employee_profiles!"
        assert int(p["role_id"]) in role_ids, f"Profile {p['profile_id']} has invalid role_id {p['role_id']}!"
    print("[OK] All employee profiles map to valid master role_ids.")
    
    # 3. Verify interview_questions.csv & json
    iq_csv_path = os.path.join(BASE_DIR, "database", "hiring_layer", "interview_questions.csv")
    iq_json_path = os.path.join(BASE_DIR, "database", "datasets", "interview_questions", "interview_questions.json")
    assert os.path.exists(iq_csv_path), "interview_questions.csv missing!"
    assert os.path.exists(iq_json_path), "interview_questions.json missing!"
    
    with open(iq_csv_path, "r", encoding="utf-8") as f:
        iq_csv = list(csv.DictReader(f))
    with open(iq_json_path, "r", encoding="utf-8") as f:
        iq_json = json.load(f)
        
    print(f"[OK] interview_questions.csv count: {len(iq_csv)} rows (expected 300+).")
    print(f"[OK] interview_questions.json count: {len(iq_json)} items (expected 300+).")
    assert len(iq_csv) >= 300, f"Expected 300+ questions, got {len(iq_csv)}"
    assert len(iq_json) >= 300, f"Expected 300+ questions, got {len(iq_json)}"
    
    # 4. Verify learning_resources.csv & json
    lr_csv_path = os.path.join(BASE_DIR, "database", "learning_layer", "learning_resources.csv")
    lr_json_path = os.path.join(BASE_DIR, "database", "datasets", "resources", "learning_resources.json")
    assert os.path.exists(lr_csv_path), "learning_resources.csv missing!"
    assert os.path.exists(lr_json_path), "learning_resources.json missing!"
    
    with open(lr_csv_path, "r", encoding="utf-8") as f:
        lr_csv = list(csv.DictReader(f))
    with open(lr_json_path, "r", encoding="utf-8") as f:
        lr_json = json.load(f)
        
    print(f"[OK] learning_resources.csv count: {len(lr_csv)} rows (expected 100+).")
    print(f"[OK] learning_resources.json count: {len(lr_json)} items (expected 100+).")
    assert len(lr_csv) >= 100, f"Expected 100+ resources, got {len(lr_csv)}"
    assert len(lr_json) >= 100, f"Expected 100+ resources, got {len(lr_json)}"
    
    # 5. Verify projects_master.csv & projects.json
    pm_csv_path = os.path.join(BASE_DIR, "database", "learning_layer", "projects_master.csv")
    ps_map_path = os.path.join(BASE_DIR, "database", "learning_layer", "project_skill_mapping.csv")
    pm_json_path = os.path.join(BASE_DIR, "database", "datasets", "projects", "projects.json")
    assert os.path.exists(pm_csv_path), "projects_master.csv missing!"
    assert os.path.exists(ps_map_path), "project_skill_mapping.csv missing!"
    assert os.path.exists(pm_json_path), "projects.json missing!"
    
    with open(pm_csv_path, "r", encoding="utf-8") as f:
        pm_csv = list(csv.DictReader(f))
    with open(ps_map_path, "r", encoding="utf-8") as f:
        ps_map = list(csv.DictReader(f))
    with open(pm_json_path, "r", encoding="utf-8") as f:
        pm_json = json.load(f)
        
    print(f"[OK] projects_master.csv count: {len(pm_csv)} rows (expected 50-100).")
    print(f"[OK] project_skill_mapping.csv count: {len(ps_map)} rows.")
    print(f"[OK] projects.json count: {len(pm_json)} items (expected 50-100).")
    assert 50 <= len(pm_csv) <= 100, f"Expected 50-100 projects, got {len(pm_csv)}"
    assert 50 <= len(pm_json) <= 100, f"Expected 50-100 projects, got {len(pm_json)}"
    
    # 6. Verify stage_assessments.json
    sa_json_path = os.path.join(BASE_DIR, "database", "learning_layer", "stage_assessments.json")
    assert os.path.exists(sa_json_path), "stage_assessments.json missing!"
    with open(sa_json_path, "r", encoding="utf-8") as f:
        sa_json = json.load(f)
    print(f"[OK] stage_assessments.json exists: {len(sa_json)} stages configured.")
    assert len(sa_json) == 4, f"Expected 4 stages, got {len(sa_json)}"
    for s in sa_json:
        assert "stage_id" in s and "mcqs" in s and "coding_challenge" in s
        assert len(s["mcqs"]) >= 10, f"Expected at least 10 MCQs per stage, got {len(s['mcqs'])}"
    print("[OK] All stage assessments structures are valid.")
    
    # 7. Run recommendation engine test
    print("\nTesting dynamic recommendations matching...")
    test_skills = ["Go", "Kafka", "PostgreSQL"]
    res = generate_recommendation(
        qualification="3rd Year Student",
        known_skills=test_skills,
        dream_company="Blinkit",
        dream_sector="Quick-Commerce",
        target_role="Software Development Engineer (SDE)",
        skip_llm=True
    )
    
    print("[OK] Recommendation engine generated output successfully.")
    print(f"  Urgency: {res['timeline']['urgency']}")
    print(f"  Recommended projects count: {len(res['projects'])}")
    print(f"  Recommended resources count: {len(res['resources'])}")
    print(f"  Recommended questions count: {len(res['recommended_questions'])}")
    
    assert len(res["projects"]) > 0, "No projects returned!"
    assert len(res["resources"]) > 0, "No resources returned!"
    assert len(res["recommended_questions"]) > 0, "No questions returned!"
    
    print("\n" + "="*50)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("="*50 + "\n")

if __name__ == "__main__":
    verify_all()
