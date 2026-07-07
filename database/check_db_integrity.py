# Database Integrity Checks - CareerCompass AI

import os
import sys
import psycopg2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database_connector import DB_CONFIG

def verify_integrity():
    print("=" * 60)
    print("DATABASE INTEGRITY CHECKS")
    print("=" * 60)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO career_compass_ai, public;")

    failures = 0

    # 1. Duplicate mappings in stage_skills
    cur.execute("""
        SELECT stage_id, skill_id, COUNT(*) 
        FROM stage_skills 
        GROUP BY stage_id, skill_id 
        HAVING COUNT(*) > 1;
    """)
    dups_l5 = cur.fetchall()
    print(f"1. Duplicate (stage_id, skill_id) in stage_skills: {len(dups_l5)}")
    if dups_l5:
        print(f"   FAIL: Found duplicates: {dups_l5}")
        failures += 1
    else:
        print("   PASS: No duplicates in stage_skills.")

    # 2. Duplicate mappings in roadmap_stage_skill_mapping
    cur.execute("""
        SELECT stage_id, skill_id, COUNT(*) 
        FROM roadmap_stage_skill_mapping 
        GROUP BY stage_id, skill_id 
        HAVING COUNT(*) > 1;
    """)
    dups_l16 = cur.fetchall()
    print(f"2. Duplicate (stage_id, skill_id) in roadmap_stage_skill_mapping: {len(dups_l16)}")
    if dups_l16:
        print(f"   FAIL: Found duplicates: {dups_l16}")
        failures += 1
    else:
        print("   PASS: No duplicates in roadmap_stage_skill_mapping.")

    # 3. Orphan stage_skills (invalid stage references)
    cur.execute("""
        SELECT COUNT(*) FROM stage_skills ss
        LEFT JOIN roadmap_stages rs ON ss.stage_id = rs.stage_id
        WHERE rs.stage_id IS NULL;
    """)
    orphans_stage_l5 = cur.fetchone()[0]
    print(f"3. Orphan stage references in stage_skills: {orphans_stage_l5}")
    if orphans_stage_l5 > 0:
        print("   FAIL: Found stage_id values referencing non-existent stages.")
        failures += 1
    else:
        print("   PASS: All stages in stage_skills are valid.")

    # 4. Orphan roadmap_stage_skill_mapping (invalid stage references)
    cur.execute("""
        SELECT COUNT(*) FROM roadmap_stage_skill_mapping rssm
        LEFT JOIN roadmap_stages rs ON rssm.stage_id = rs.stage_id
        WHERE rs.stage_id IS NULL;
    """)
    orphans_stage_l16 = cur.fetchone()[0]
    print(f"4. Orphan stage references in roadmap_stage_skill_mapping: {orphans_stage_l16}")
    if orphans_stage_l16 > 0:
        print("   FAIL: Found stage_id values referencing non-existent stages.")
        failures += 1
    else:
        print("   PASS: All stages in roadmap_stage_skill_mapping are valid.")

    # 5. Invalid skill references in stage_skills
    cur.execute("""
        SELECT COUNT(*) FROM stage_skills ss
        LEFT JOIN skills s ON ss.skill_id = s.skill_id
        WHERE s.skill_id IS NULL;
    """)
    orphans_skill_l5 = cur.fetchone()[0]
    print(f"5. Invalid skill references in stage_skills: {orphans_skill_l5}")
    if orphans_skill_l5 > 0:
        print("   FAIL: Found skill_id values referencing non-existent skills.")
        failures += 1
    else:
        print("   PASS: All skills in stage_skills are valid.")

    # 6. Invalid skill references in roadmap_stage_skill_mapping
    cur.execute("""
        SELECT COUNT(*) FROM roadmap_stage_skill_mapping rssm
        LEFT JOIN skills s ON rssm.skill_id = s.skill_id
        WHERE s.skill_id IS NULL;
    """)
    orphans_skill_l16 = cur.fetchone()[0]
    print(f"6. Invalid skill references in roadmap_stage_skill_mapping: {orphans_skill_l16}")
    if orphans_skill_l16 > 0:
        print("   FAIL: Found skill_id values referencing non-existent skills.")
        failures += 1
    else:
        print("   PASS: All skills in roadmap_stage_skill_mapping are valid.")

    cur.close()
    conn.close()

    print("=" * 60)
    if failures == 0:
        print("INTEGRITY VERIFICATION SUCCESSFUL!")
        sys.exit(0)
    else:
        print("INTEGRITY VERIFICATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    verify_integrity()
