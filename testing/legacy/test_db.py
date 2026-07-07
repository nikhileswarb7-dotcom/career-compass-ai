import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import DB_CONFIG
import psycopg2
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='career_compass_ai' AND table_name='student_outcomes'")
    print("student_outcomes columns:", cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM career_compass_ai.student_outcomes")
    print("student_outcomes count:", cur.fetchone()[0])
    cur.close()
    conn.close()
except Exception as e:
    print("ERROR:", e)
