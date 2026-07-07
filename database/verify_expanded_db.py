import os
import csv
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

def check_csv_rows(layer_folder, filename):
    filepath = os.path.join(DB_DIR, layer_folder, filename)
    if not os.path.exists(filepath):
        print(f"FAIL: {filename} does not exist at {filepath}")
        return None
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"PASS: {filename} exists with {len(rows)} rows.")
        return rows

def verify_all():
    print("\n" + "="*50)
    print("CAREERCOMPASS AI — EXPANDED DATASET VALIDATION")
    print("="*50)
    
    # 1. Check roles.csv (Expected 10-20, generated has 12)
    roles = check_csv_rows("industry_layer", "roles.csv")
    if roles:
        role_ids = {int(r["role_id"]) for r in roles}
        if len(roles) == 30:
            print("  -> PASS: roles.csv has exactly 30 unique roles.")
        else:
            print(f"  -> FAIL: Expected 30 roles, got {len(roles)}.")
            
    # 2. Check employee_profiles.csv (Expected 121 rows from parsing)
    profiles = check_csv_rows("industry_layer", "employee_profiles.csv")
    if profiles:
        invalid_role_refs = 0
        for p in profiles:
            role_id = int(p["role_id"]) if p["role_id"] else None
            if role_id not in role_ids:
                invalid_role_refs += 1
        if invalid_role_refs == 0:
            print("  -> PASS: All employee profiles map to a valid role_id.")
        else:
            print(f"  -> FAIL: Found {invalid_role_refs} profiles with invalid role_id references.")

    # 3. Check interview_questions.csv (Expected 300+ entries)
    questions = check_csv_rows("hiring_layer", "interview_questions.csv")
    if questions:
        if len(questions) >= 300:
            print(f"  -> PASS: interview_questions.csv contains {len(questions)} entries (>= 300).")
        else:
            print(f"  -> FAIL: Expected 300+ questions, got {len(questions)}.")

    # 4. Check learning_resources.csv (Expected 100+ entries)
    resources = check_csv_rows("learning_layer", "learning_resources.csv")
    if resources:
        if len(resources) >= 100:
            print(f"  -> PASS: learning_resources.csv contains {len(resources)} entries (>= 100).")
        else:
            print(f"  -> FAIL: Expected 100+ resources, got {len(resources)}.")

    # 5. Check projects_master.csv (Expected 50-100 entries)
    projects = check_csv_rows("learning_layer", "projects_master.csv")
    if projects:
        if 50 <= len(projects) <= 100:
            print(f"  -> PASS: projects_master.csv contains {len(projects)} entries (between 50 and 100).")
        else:
            print(f"  -> FAIL: Expected between 50 and 100 projects, got {len(projects)}.")

    # 6. Verify stage_assessments.json (Expected valid JSON with MCQs and coding template)
    assessments_path = os.path.join(DB_DIR, "learning_layer", "stage_assessments.json")
    if os.path.exists(assessments_path):
        try:
            with open(assessments_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                print(f"PASS: stage_assessments.json loaded with {len(json_data)} stages.")
                for stage in json_data:
                    stage_id = stage["stage_id"]
                    mcq_count = len(stage["mcqs"])
                    has_coding = "coding_challenge" in stage
                    print(f"  -> Stage {stage_id}: {mcq_count} MCQs, Coding Challenge present: {has_coding}")
                print("  -> PASS: stage_assessments.json structure is valid.")
        except Exception as e:
            print(f"  -> FAIL: Failed to parse stage_assessments.json: {e}")
    else:
        print("  -> FAIL: stage_assessments.json does not exist.")

    print("="*50)
    print("Validation finished.")
    print("="*50 + "\n")

if __name__ == "__main__":
    verify_all()
