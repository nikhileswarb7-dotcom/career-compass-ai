# Add New Skills Migration - CareerCompass AI

import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database_connector import DB_CONFIG

NEW_SKILLS = [
    ("JavaScript", "Programming", "Beginner"),
    ("TypeScript", "Programming", "Intermediate"),
    ("HTML & CSS", "Frontend", "Beginner"),
    ("React", "Frontend", "Intermediate"),
    ("NodeJS", "Backend", "Intermediate"),
    ("Angular", "Frontend", "Intermediate"),
    ("Vue.js", "Frontend", "Intermediate"),
    ("Express.js", "Backend", "Intermediate"),
    ("FastAPI", "Backend", "Intermediate"),
    ("Django", "Backend", "Intermediate"),
    ("MongoDB", "Database", "Intermediate"),
    ("DynamoDB", "Database", "Intermediate"),
    ("JUnit", "Testing", "Intermediate"),
    ("Selenium", "Testing", "Intermediate"),
    ("Playwright", "Testing", "Intermediate"),
    ("Android", "Mobile", "Intermediate"),
    ("iOS", "Mobile", "Intermediate"),
    ("Flutter", "Mobile", "Intermediate"),
    ("Terraform", "DevOps", "Advanced"),
    ("Prometheus", "DevOps", "Intermediate"),
    ("Grafana", "DevOps", "Intermediate"),
    ("PyTorch", "Data/ML", "Advanced"),
    ("TensorFlow", "Data/ML", "Advanced"),
    ("Pandas", "Data/ML", "Intermediate"),
    ("Scikit-Learn", "Data/ML", "Advanced")
]

def add_skills():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO career_compass_ai, public;")
    
    cur.execute("SELECT COUNT(*) FROM skills;")
    before_count = cur.fetchone()[0]
    print(f"Skills count before migration: {before_count}")
    
    inserted = 0
    for name, cat, diff in NEW_SKILLS:
        cur.execute("SELECT 1 FROM skills WHERE LOWER(skill_name) = %s;", (name.lower().strip(),))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO skills (skill_name, category, difficulty)
                VALUES (%s, %s, %s);
            """, (name, cat, diff))
            inserted += 1
            
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM skills;")
    after_count = cur.fetchone()[0]
    print(f"Skills count after migration: {after_count}")
    print(f"Successfully inserted {inserted} new canonical skills.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_skills()
