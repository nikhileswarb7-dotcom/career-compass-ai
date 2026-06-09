# Phase 3 Database Migration & Seeding Script
# CareerCompass AI

import os
import sys
import json
import psycopg2
from psycopg2.extras import Json

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "career_compass_ai",
    "user":     "postgres",
    "password": "Nikhil@2824"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_migration():
    print("Connecting to PostgreSQL database...")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        print("Successfully connected to database.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    # 1. Create tables by running the DDL statements directly
    print("Creating Phase 3 tables...")
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS resource_skill_mapping (
            id SERIAL PRIMARY KEY,
            resource_id INT REFERENCES resources(resource_id) ON DELETE CASCADE,
            skill_id INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(resource_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS roadmap_stage_skill_mapping (
            id SERIAL PRIMARY KEY,
            stage_id INT REFERENCES roadmap_stages(stage_id) ON DELETE CASCADE,
            skill_id INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(stage_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS skill_clusters (
            cluster_id          SERIAL PRIMARY KEY,
            cluster_name        VARCHAR(100) UNIQUE NOT NULL,
            default_milestone   TEXT,
            display_order       INT DEFAULT 0
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS skill_cluster_skills (
            id                  SERIAL PRIMARY KEY,
            cluster_id          INT REFERENCES skill_clusters(cluster_id) ON DELETE CASCADE,
            skill_id            INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(cluster_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS project_skill_mapping (
            id                  SERIAL PRIMARY KEY,
            project_id          INT REFERENCES projects(project_id) ON DELETE CASCADE,
            skill_id            INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(project_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS interview_question_skill_mapping (
            id                  SERIAL PRIMARY KEY,
            question_id         INT REFERENCES interview_questions(question_id) ON DELETE CASCADE,
            skill_id            INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(question_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS mcqs (
            mcq_id              SERIAL PRIMARY KEY,
            question            TEXT NOT NULL,
            options             JSONB NOT NULL,
            correct_option      INT NOT NULL,
            explanation         TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS mcq_skill_mapping (
            id                  SERIAL PRIMARY KEY,
            mcq_id              INT REFERENCES mcqs(mcq_id) ON DELETE CASCADE,
            skill_id            INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(mcq_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS candidate_skill_gaps (
            id                  SERIAL PRIMARY KEY,
            student_id          INT REFERENCES students(student_id) ON DELETE CASCADE,
            skill_id            INT REFERENCES skills(skill_id) ON DELETE CASCADE,
            priority            VARCHAR(20),
            status              VARCHAR(50) DEFAULT 'Missing',
            UNIQUE(student_id, skill_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS student_dynamic_progress (
            id                  SERIAL PRIMARY KEY,
            student_id          INT REFERENCES students(student_id) ON DELETE CASCADE,
            stage_title         VARCHAR(200) NOT NULL,
            status              VARCHAR(50) DEFAULT 'Not Started',
            completion_pct      INT DEFAULT 0,
            UNIQUE(student_id, stage_title)
        );
        """
    ]

    for stmt in ddl_statements:
        try:
            cur.execute(stmt)
        except Exception as e:
            print(f"Error running DDL: {e}")
            conn.rollback()
            conn.close()
            return
    conn.commit()
    print("Tables verified/created successfully.")

    # 2. Map skills
    cur.execute("SELECT skill_id, skill_name, category FROM skills;")
    skills = cur.fetchall()
    skills_map = {row[1].lower().strip(): row[0] for row in skills}
    skills_by_id = {row[0]: row[1] for row in skills}

    # 3. Populate resource_skill_mapping
    print("Populating resource_skill_mapping from resources...")
    cur.execute("""
        INSERT INTO resource_skill_mapping (resource_id, skill_id)
        SELECT resource_id, skill_id FROM resources WHERE skill_id IS NOT NULL
        ON CONFLICT DO NOTHING;
    """)
    conn.commit()

    # If some resources have skill_id as NULL, let's see if we can resolve it via topic name matching skill name
    cur.execute("SELECT resource_id, topic FROM resources WHERE skill_id IS NULL AND topic IS NOT NULL;")
    null_skill_res = cur.fetchall()
    res_mappings_added = 0
    for r_id, topic in null_skill_res:
        t_low = topic.lower().strip()
        if t_low in skills_map:
            cur.execute("""
                INSERT INTO resource_skill_mapping (resource_id, skill_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
            """, (r_id, skills_map[t_low]))
            res_mappings_added += 1
    conn.commit()
    print(f"Mapped {res_mappings_added} additional resource-to-skill linkages.")

    # 4. Populate skill_clusters and skill_cluster_skills
    print("Populating skill_clusters...")
    clusters_data = [
        {
            "name": "Languages & Foundations",
            "milestone": "Demonstrate language familiarity, OOP concepts, and basic git workspace setup.",
            "order": 1,
            "skills": ["java", "python", "go", "c programming", "c++", "object oriented programming", "oop", "git & github"]
        },
        {
            "name": "Data Structures & Algorithms",
            "milestone": "Master time complexities and solve medium-level algorithmic challenges on array/linked lists/trees.",
            "order": 2,
            "skills": ["dsa (combined)", "data structures", "algorithms"]
        },
        {
            "name": "Databases & Core CS",
            "milestone": "Design relational database schemas, write complex queries, and explain core OS/network protocols.",
            "order": 3,
            "skills": ["dbms", "sql", "mysql", "postgresql", "operating systems", "computer networks", "linux basics"]
        },
        {
            "name": "Backend API Foundations",
            "milestone": "Develop and deploy robust CRUD API endpoints with error handling and validations.",
            "order": 4,
            "skills": ["spring boot", "rest apis", "nodejs"]
        },
        {
            "name": "Distributed Systems & Caching",
            "milestone": "Configure Redis caches, process real-time Kafka event streams, and dockerize backend services.",
            "order": 5,
            "skills": ["redis", "kafka", "microservices", "docker", "message queues (kafka)", "aws basics", "kubernetes"]
        },
        {
            "name": "System Design & Architecture",
            "milestone": "Create low-level class structural models and high-level architectural designs for scaling traffic.",
            "order": 6,
            "skills": ["system design", "low level design", "high level design"]
        }
    ]

    for c in clusters_data:
        cur.execute("""
            INSERT INTO skill_clusters (cluster_name, default_milestone, display_order)
            VALUES (%s, %s, %s)
            ON CONFLICT (cluster_name) DO UPDATE
            SET default_milestone = EXCLUDED.default_milestone, display_order = EXCLUDED.display_order
            RETURNING cluster_id;
        """, (c["name"], c["milestone"], c["order"]))
        c_id = cur.fetchone()[0]

        # Link skills
        for s_name in c["skills"]:
            if s_name in skills_map:
                cur.execute("""
                    INSERT INTO skill_cluster_skills (cluster_id, skill_id)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """, (c_id, skills_map[s_name]))
    conn.commit()
    print("Skill clusters populated successfully.")

    # 5. Populate project_skill_mapping
    print("Populating project_skill_mapping...")
    cur.execute("SELECT project_id, skills_covered FROM projects;")
    projs = cur.fetchall()
    proj_mappings = 0
    for p_id, skills_covered in projs:
        if isinstance(skills_covered, str):
            try:
                skills_covered = json.loads(skills_covered)
            except Exception:
                skills_covered = []
        if isinstance(skills_covered, list):
            for s_name in skills_covered:
                s_low = s_name.lower().strip()
                if s_low in skills_map:
                    cur.execute("""
                        INSERT INTO project_skill_mapping (project_id, skill_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING;
                    """, (p_id, skills_map[s_low]))
                    proj_mappings += 1
    conn.commit()
    print(f"Created {proj_mappings} project-skill mappings.")

    # 6. Populate interview_question_skill_mapping
    print("Populating interview_question_skill_mapping...")
    cur.execute("SELECT question_id, category FROM interview_questions;")
    questions = cur.fetchall()
    q_mappings = 0
    for q_id, category in questions:
        c_low = category.lower().strip() if category else ""
        # Map categories to skills
        matched_skill_id = None
        if c_low in skills_map:
            matched_skill_id = skills_map[c_low]
        elif c_low == "dsa":
            matched_skill_id = skills_map.get("dsa (combined)")
        elif c_low == "dbms":
            matched_skill_id = skills_map.get("dbms")
        elif c_low == "os":
            matched_skill_id = skills_map.get("operating systems")
        elif c_low == "cn":
            matched_skill_id = skills_map.get("computer networks")
        
        if matched_skill_id:
            cur.execute("""
                INSERT INTO interview_question_skill_mapping (question_id, skill_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
            """, (q_id, matched_skill_id))
            q_mappings += 1
    conn.commit()
    print(f"Created {q_mappings} interview question-skill mappings.")

    # 7. Populate mcqs and mcq_skill_mapping
    print("Seeding MCQs table...")
    mcq_seed_data = [
        # Java
        {"question": "What is the correct way to allocate memory for an array of size 10 in Java?", "options": ["int arr = new int[10];", "int[] arr = new int[10];", "int arr[] = int[10];", "int[] arr = int new[10];"], "correct": 1, "explanation": "In Java, an array is allocated using the 'new' keyword and specifying the type and brackets like 'int[] arr = new int[10];'", "skill": "java"},
        {"question": "Which of these is not a valid access modifier in Java?", "options": ["public", "private", "protected", "internal"], "correct": 3, "explanation": "'internal' is used in languages like C# or Kotlin, but is not a valid Java access modifier.", "skill": "java"},
        # Spring Boot
        {"question": "Which Spring Boot annotation is used to create a Restful controller interface?", "options": ["@Controller", "@RestController", "@Repository", "@Service"], "correct": 1, "explanation": "@RestController combines @Controller and @ResponseBody, making it ideal for returning JSON REST responses.", "skill": "spring boot"},
        {"question": "What is the default port for Spring Boot application server?", "options": ["8080", "5000", "3000", "8000"], "correct": 0, "explanation": "Spring Boot applications run on port 8080 by default inside Tomcat.", "skill": "spring boot"},
        # Redis
        {"question": "Which command is used in Redis to set a key with an expiration time?", "options": ["SETEX", "EXPIRE", "PEXPIRE", "SET EXP"], "correct": 0, "explanation": "SETEX sets the string value of a key and associated timeout in seconds in one atomic command.", "skill": "redis"},
        {"question": "Which Redis data structure is optimal for caching geo-coordinates of riders?", "options": ["Sorted Sets", "Hashes", "Geospatial Indexes (GEO)", "HyperLogLogs"], "correct": 2, "explanation": "Redis GEO commands (GEOADD, GEORADIUS) are designed specifically for coordinate operations.", "skill": "redis"},
        # Kafka
        {"question": "How does Apache Kafka achieve high throughput for log files?", "options": ["By encrypting data packets", "Using zero-copy transfer and sequential disk I/O", "Running all partitions in RAM memory", "Compressing databases"], "correct": 1, "explanation": "Kafka writes sequentially to disk files and utilizes OS-level sendfile zero-copy memory transfers to achieve incredible speeds.", "skill": "kafka"},
        {"question": "In Kafka, a consumer group allows:", "options": ["Multiple consumers to read from the exact same partition concurrently", "Scaling of read bandwidth by distributing partitions among group members", "Replication of data points across zones", "Automatic topic creation configurations"], "correct": 1, "explanation": "A consumer group distributes partition reading responsibilities across members, ensuring scaling.", "skill": "kafka"},
        # System Design
        {"question": "What does CAP stand for in distributed systems theorem?", "options": ["Concurrency, Availability, Performance", "Consistency, Availability, Partition Tolerance", "Caching, API design, Portability", "Complexity, Alignment, Performance"], "correct": 1, "explanation": "The CAP theorem states that a distributed data store can guarantee at most two out of Consistency, Availability, and Partition Tolerance.", "skill": "system design"},
        {"question": "Which component is used to distribute client requests across multiple application servers?", "options": ["Database indexer", "Message queue", "Load balancer", "Redis cache"], "correct": 2, "explanation": "Load balancers distribute traffic across server nodes to prevent overload.", "skill": "system design"}
    ]

    mcq_count = 0
    for m in mcq_seed_data:
        cur.execute("""
            INSERT INTO mcqs (question, options, correct_option, explanation)
            VALUES (%s, %s, %s, %s)
            RETURNING mcq_id;
        """, (m["question"], Json(m["options"]), m["correct"], m["explanation"]))
        mcq_id = cur.fetchone()[0]

        s_name = m["skill"]
        if s_name in skills_map:
            cur.execute("""
                INSERT INTO mcq_skill_mapping (mcq_id, skill_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
            """, (mcq_id, skills_map[s_name]))
            mcq_count += 1
    conn.commit()
    print(f"Inserted and mapped {mcq_count} target MCQs by skill.")

    cur.close()
    conn.close()
    print("Phase 3 DDL, seeding and migrations completed successfully!")

if __name__ == "__main__":
    run_migration()
