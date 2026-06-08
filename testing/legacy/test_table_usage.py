import psycopg2
try:
    conn = psycopg2.connect(host='localhost', port=5432, dbname='career_compass_ai', user='postgres', password='Nikhil@2824')
    cur = conn.cursor()
    
    for table in ['companies', 'roles', 'employee_profiles']:
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='career_compass_ai' AND table_name='{table}'")
        print(f"Table {table} columns:", cur.fetchall())
        
    cur.close()
    conn.close()
except Exception as e:
    print("ERROR:", e)
