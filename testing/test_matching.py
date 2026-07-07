import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database_connector import DB_CONFIG
import psycopg2

def test_matching():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO career_compass_ai, public;")
    cur.execute("SELECT skill_id, skill_name FROM skills;")
    skills_db = cur.fetchall()
    skills_master = {r[1].lower().strip(): r[0] for r in skills_db}
    print(f"skills_master keys: {list(skills_master.keys())}")
    
    test_skill = "Systems Design"
    test_skill_lower = test_skill.lower().strip()
    
    matched_id = None
    if test_skill_lower in skills_master:
        matched_id = skills_master[test_skill_lower]
        print(f"Exact match: {matched_id}")
    else:
        for skill_m, s_id in skills_master.items():
            if skill_m in test_skill_lower or test_skill_lower in skill_m:
                matched_id = s_id
                print(f"Substring match with '{skill_m}': {matched_id}")
                break
                
    cur.close()
    conn.close()

if __name__ == "__main__":
    test_matching()
