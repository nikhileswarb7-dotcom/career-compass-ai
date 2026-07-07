import os
import sys
import re

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from database.parse_profiles import parse_profile_pdf, PROFILES_DIR

def run_validation():
    print("\n============================================================")
    print("CareerCompass AI — Raw Profiles Automated Quality Validator")
    print("============================================================\n")

    if not os.path.exists(PROFILES_DIR):
        print(f"[ERROR] Profiles directory does not exist at: {PROFILES_DIR}")
        return

    print(f"Scanning profiles directory: {PROFILES_DIR}")
    pdf_files = []
    for root, _, files in os.walk(PROFILES_DIR):
        for f in files:
            if f.endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))

    total_files = len(pdf_files)
    print(f"Found {total_files} PDF profiles. Beginning automated audit...\n")

    valid_profiles = []
    warning_profiles = []
    invalid_profiles = []

    for idx, filepath in enumerate(pdf_files, 1):
        rel_path = os.path.relpath(filepath, PROFILES_DIR)
        
        # Progress indicator
        if idx % 100 == 0 or idx == total_files:
            print(f"Audited {idx}/{total_files} files...")

        try:
            profile = parse_profile_pdf(filepath)
            
            name = profile.get("name")
            skills = profile.get("skills", [])
            experiences = profile.get("experience", [])
            
            # Reasons for warnings/failures
            reasons = []
            
            if not name:
                reasons.append("Missing Name")
            if not skills:
                reasons.append("Zero Skills Extracted")
            if not experiences:
                reasons.append("Zero Experiences Extracted")
                
            if not name or (not skills and not experiences):
                invalid_profiles.append({
                    "file": rel_path,
                    "name": name or "Unknown",
                    "skills_count": len(skills),
                    "exp_count": len(experiences),
                    "reasons": ", ".join(reasons) or "Corrupted Text"
                })
            elif not skills or not experiences:
                warning_profiles.append({
                    "file": rel_path,
                    "name": name,
                    "skills_count": len(skills),
                    "exp_count": len(experiences),
                    "reasons": ", ".join(reasons)
                })
            else:
                valid_profiles.append({
                    "file": rel_path,
                    "name": name,
                    "skills_count": len(skills),
                    "exp_count": len(experiences)
                })
        except Exception as e:
            invalid_profiles.append({
                "file": rel_path,
                "name": "Corrupted/Unreadable PDF",
                "skills_count": 0,
                "exp_count": 0,
                "reasons": f"PDF Reading Error: {str(e)}"
            })

    # Summary Statistics
    print("\n" + "="*45)
    print("                AUDIT SUMMARY")
    print("="*45)
    print(f"Total Profiles Scanned:   {total_files}")
    print(f"Fully Valid Profiles:     {len(valid_profiles)} ({round(len(valid_profiles)/total_files*100, 1) if total_files else 0}%)")
    print(f"Warning/Partial Profiles: {len(warning_profiles)} ({round(len(warning_profiles)/total_files*100, 1) if total_files else 0}%)")
    print(f"Invalid/Corrupt Profiles: {len(invalid_profiles)} ({round(len(invalid_profiles)/total_files*100, 1) if total_files else 0}%)")
    print("="*45)

    # Output Warnings
    if warning_profiles:
        print("\n" + "!"*45)
        print("          WARNING PROFILES DETECTED")
        print(" (Name parsed but missing either skills or experience)")
        print("!"*45)
        
        for wp in warning_profiles[:20]:  # Limit output log length
            print(f"- {wp['name']} ({wp['file']}): {wp['reasons']}")
        if len(warning_profiles) > 20:
            print(f"... and {len(warning_profiles) - 20} more warning profiles.")

    # Output Invalid Profiles
    if invalid_profiles:
        print("\n" + "x"*45)
        print("          CRITICAL INVALID PROFILES")
        print("  (Cannot be parsed / Corrupted / Missing sections)")
        print("x"*45)
        
        for ip in invalid_profiles[:30]:  # Show up to 30 failures
            print(f"- {ip['name']} ({ip['file']}): {ip['reasons']}")
        if len(invalid_profiles) > 30:
            print(f"... and {len(invalid_profiles) - 30} more invalid profiles.")
            
        print("\n[ACTION REQUIRED] Please review or remove the above invalid files to keep your training dataset clean and accurate.")
    else:
        print("\n[SUCCESS] No critical invalid files found! Your raw profile dataset is clean.")

if __name__ == "__main__":
    run_validation()
