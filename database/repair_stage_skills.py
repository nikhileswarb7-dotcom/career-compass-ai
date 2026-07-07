# Repair SDE Stage-Skill Mappings - CareerCompass AI
# Idempotent, transactional, and dry-run capable.

import os
import json
import psycopg2
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database_connector import DB_CONFIG

def load_json(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_repair(dry_run=True):
    print("=" * 60)
    print(f"SDE ROADMAP STAGE-SKILL REPAIR SCRIPT (DRY-RUN: {dry_run})")
    print("=" * 60)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

    # 1. Back up existing stage_skills and roadmap_stage_skill_mapping data
    print("Backing up existing mappings in memory...")
    cur.execute("SELECT id, stage_id, skill_id FROM stage_skills;")
    backup_stage_skills = cur.fetchall()
    cur.execute("SELECT id, stage_id, skill_id FROM roadmap_stage_skill_mapping;")
    backup_roadmap_stage_skills = cur.fetchall()
    print(f"  Backed up {len(backup_stage_skills)} records from stage_skills.")
    print(f"  Backed up {len(backup_roadmap_stage_skills)} records from roadmap_stage_skill_mapping.")

    # Load SDE roadmaps JSON
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = os.path.join(base_dir, "database", "datasets", "roadmaps", "blinkit_sde_roadmaps.json")
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        conn.close()
        sys.exit(1)

    data = load_json(json_path)

    # Get Blinkit SDE company_role_id
    cur.execute("""
        SELECT cr.company_role_id 
        FROM company_roles cr
        JOIN companies c ON cr.company_id = c.company_id
        JOIN roles r ON cr.role_id = r.role_id
        WHERE LOWER(c.company_name) = 'blinkit' AND LOWER(r.role_name) = 'software development engineer (sde)';
    """)
    row = cur.fetchone()
    if not row:
        print("Error: Blinkit SDE company_role_id not found in DB.")
        conn.close()
        sys.exit(1)
    company_role_id = row[0]
    print(f"Resolved Blinkit SDE company_role_id: {company_role_id}")

    # Load skills master for mapping
    cur.execute("SELECT skill_id, skill_name FROM skills;")
    skills_db = cur.fetchall()
    skills_map = {}
    skills_by_id = {}
    for sid, sname in skills_db:
        sname_cleaned = sname.lower().strip()
        skills_map.setdefault(sname_cleaned, []).append(sid)
        skills_by_id[sid] = sname

    # Stats tracking
    stats = {
        "inserted": 0,
        "existing": 0,
        "unresolved": set(),
        "ambiguous": {},
        "skipped": 0
    }

    try:
        # Loop through JSON roadmaps
        for rm in data["roadmaps"]:
            qual_name = rm["qualification"]
            
            # Resolve qualification_id
            cur.execute("SELECT qualification_id FROM qualifications WHERE LOWER(qualification_name) = %s;", (qual_name.lower().strip(),))
            row_qual = cur.fetchone()
            if not row_qual:
                print(f"  WARN: Qualification '{qual_name}' not found in DB. Skipping roadmap.")
                stats["skipped"] += 1
                continue
            qual_id = row_qual[0]

            # Resolve roadmap_id
            cur.execute("""
                SELECT roadmap_id FROM roadmaps 
                WHERE qualification_id = %s AND company_role_id = %s;
            """, (qual_id, company_role_id))
            row_rm = cur.fetchone()
            if not row_rm:
                print(f"  WARN: Roadmap not found for qualification '{qual_name}' and SDE role. Skipping.")
                stats["skipped"] += 1
                continue
            roadmap_id = row_rm[0]

            # Resolve stages for this roadmap
            for stage_json in rm["stages"]:
                stage_num = stage_json["stage_number"]
                skills_list = stage_json.get("skills", [])

                # Get stage_id for this specific roadmap and stage number
                cur.execute("""
                    SELECT stage_id, stage_title FROM roadmap_stages
                    WHERE roadmap_id = %s AND stage_number = %s;
                """, (roadmap_id, stage_num))
                row_stage = cur.fetchone()
                if not row_stage:
                    print(f"  WARN: Stage {stage_num} not found in DB for roadmap ID {roadmap_id}. Skipping stage.")
                    continue
                stage_id = row_stage[0]
                stage_title = row_stage[1]

                for s_name in skills_list:
                    s_name_cleaned = s_name.lower().strip()
                    
                    # Resolve skill_id
                    matched_ids = skills_map.get(s_name_cleaned, [])
                    if not matched_ids:
                        # Try substring match
                        matched_ids = [sid for sname_db, sids in skills_map.items() for sid in sids if s_name_cleaned in sname_db or sname_db in s_name_cleaned]

                    if not matched_ids:
                        stats["unresolved"].add(s_name)
                        print(f"    [UNRESOLVED] Skill name '{s_name}' on Roadmap {roadmap_id} Stage {stage_num}")
                        continue
                    elif len(matched_ids) > 1:
                        stats["ambiguous"][s_name] = matched_ids
                        print(f"    [AMBIGUOUS] Skill name '{s_name}' matches multiple IDs {matched_ids}")
                        continue
                    
                    skill_id = matched_ids[0]

                    # Check stage_skills (Layer 5)
                    cur.execute("""
                        SELECT 1 FROM stage_skills 
                        WHERE stage_id = %s AND skill_id = %s;
                    """, (stage_id, skill_id))
                    has_l5 = cur.fetchone()

                    # Check roadmap_stage_skill_mapping (Layer 16)
                    cur.execute("""
                        SELECT 1 FROM roadmap_stage_skill_mapping 
                        WHERE stage_id = %s AND skill_id = %s;
                    """, (stage_id, skill_id))
                    has_l16 = cur.fetchone()

                    if has_l5 and has_l16:
                        stats["existing"] += 1
                    else:
                        if not has_l5:
                            if not dry_run:
                                cur.execute("""
                                    INSERT INTO stage_skills (stage_id, skill_id) 
                                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                                """, (stage_id, skill_id))
                            stats["inserted"] += 1
                        if not has_l16:
                            if not dry_run:
                                cur.execute("""
                                    INSERT INTO roadmap_stage_skill_mapping (stage_id, skill_id) 
                                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                                """, (stage_id, skill_id))
                            if has_l5: # Count as insert if not already there
                                stats["inserted"] += 1

        if not dry_run:
            conn.commit()
            print("\nDatabase transaction committed successfully!")
        else:
            conn.rollback()
            print("\nDry-run completed. All database changes rolled back.")

    except Exception as e:
        conn.rollback()
        print(f"\nError running repair transaction: {e}")
        conn.close()
        sys.exit(1)

    # Print final summary report
    print("\n" + "=" * 50)
    print("REPAIR SUMMARY REPORT")
    print("=" * 50)
    print(f"  Inserted / Planned Mappings: {stats['inserted']}")
    print(f"  Existing Mappings:           {stats['existing']}")
    print(f"  Skipped Roadmaps:            {stats['skipped']}")
    print(f"  Unresolved Skill Names:      {list(stats['unresolved'])}")
    print(f"  Ambiguous Skill Names:       {stats['ambiguous']}")
    print("=" * 50 + "\n")

    conn.close()
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair SDE Stage-Skill Mappings in PostgreSQL")
    parser.add_argument("--commit", action="store_true", help="Commit changes to database instead of dry-run")
    args = parser.parse_args()
    
    run_repair(dry_run=not args.commit)
