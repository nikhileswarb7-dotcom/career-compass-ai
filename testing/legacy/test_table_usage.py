import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import DB_CONFIG
import psycopg2
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    for table in ['companies', 'roles', 'employee_profiles']:
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='career_compass_ai' AND table_name='{table}'")
        print(f"Table {table} columns:", cur.fetchall())
        
    cur.close()
    conn.close()
except Exception as e:
    print("ERROR:", e)
