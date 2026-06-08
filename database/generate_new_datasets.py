import os
import csv
import json
import random

# Set random seed for reproducibility
random.seed(42)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")

INDUSTRY_DIR = os.path.join(DB_DIR, "industry_layer")
CAREER_DIR = os.path.join(DB_DIR, "career_layer")
HIRING_DIR = os.path.join(DB_DIR, "hiring_layer")
LEARNING_DIR = os.path.join(DB_DIR, "learning_layer")

def write_csv(filepath, headers, rows):
    with open(filepath, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Written {len(rows)} rows to {os.path.basename(filepath)}")

# ====================================================================
# 1. job_descriptions.csv
# ====================================================================
def generate_job_descriptions():
    csv_path = os.path.join(HIRING_DIR, "job_descriptions.csv")
    
    # 20 realistic Job Descriptions mapping companies to roles
    # companies: 1=Blinkit, 2=Zomato, 3=Swiggy, 4=Paytm, 5=PhonePe, 6=Flipkart, 7=Amazon, 8=Google, 9=Microsoft, 10=Meta
    # roles: 1=Intern, 2=SDE I, 3=SDE II, 8=Backend, 9=Frontend, 10=SRE, 11=Mobile, 12=AI/ML
    jds = [
        # Blinkit
        (1, 1, 2, "0-1", "8-12 LPA", "Work as SDE Intern in Catalog backend team. Write scalable APIs using Java and Go.", "['Develop APIs','Write unit tests','Optimize Redis caches']", "['Java','Go','Data Structures']"),
        (2, 1, 2, "1-3", "12-18 LPA", "SDE I in Checkout team. Focus on backend transactions, low-latency queues and Postgres.", "['Maintain transaction pipelines','Design schemas','Optimize slow queries']", "['Go','PostgreSQL','Kafka','Git']"),
        (3, 1, 3, "3-6", "24-35 LPA", "SDE II in Rider Dispatch team. Design distributed geolocation trackers and rate limiters.", "['System architecture','Mentoring SDE Is','Participate in design reviews']", "['Go','Distributed Systems','Redis','System Design']"),
        (4, 1, 8, "2-5", "18-28 LPA", "Backend Engineer in Inventory control. Maintain Kafka streams and Spring Boot services.", "['Manage inventory microservices','Tune Kafka pipelines','Implement metrics tracking']", "['Java','Spring Boot','Kafka','Docker']"),
        (5, 1, 9, "2-4", "15-22 LPA", "Frontend Engineer in Customer App team. Build responsive web applications using React.", "['Develop responsive UIs','Optimize frontend bundle size','Collaborate with designers']", "['React','TypeScript','NextJS','CSS']"),
        
        # Zomato
        (6, 2, 2, "1-3", "14-20 LPA", "SDE I in Order Tracking team. Deliver real-time status updates via WebSockets.", "['Implement WebSockets','Optimize Redis operations','Coordinate with Mobile team']", "['NodeJS','Redis','MongoDB','Docker']"),
        (7, 2, 8, "2-5", "20-30 LPA", "Backend SDE in Delivery Logistics. Build low-latency routing and matching engines.", "['Build geospatial matching','Scale microservices','Profile database indexing']", "['Go','PostgreSQL','Redis','gRPC']"),
        
        # Swiggy
        (8, 3, 2, "1-2", "13-18 LPA", "SDE I in Cart management. Ensure consistency of customer orders under heavy load.", "['Maintain shopping cart service','Write concurrent code','Setup Prometheus alerts']", "['Java','Spring Boot','MySQL','Git']"),
        (9, 3, 11, "2-4", "16-24 LPA", "Android Mobile Engineer in Driver App team. Build offline-first applications.", "['Design driver tracking client','Optimize offline cache','Refactor legacy Java to Kotlin']", "['Kotlin','Android','SQLite','REST APIs']"),
        
        # Amazon
        (10, 7, 1, "0-1", "80k-1L/mo", "SDE Intern in AWS EC2 Console. Learn building scalable cloud dashboards.", "['Build admin features','Fix frontend bugs','Configure CI/CD pipelines']", "['TypeScript','React','AWS','Git']"),
        (11, 7, 2, "1-3", "20-28 LPA", "SDE I in Retail Catalog. Manage ingestion of millions of retail items dynamically.", "['Optimize retail ETL','Scale DynamoDB tables','Implement microservices']", "['Java','AWS','DynamoDB','Microservices']"),
        (12, 7, 3, "4-7", "38-52 LPA", "SDE II in Prime Video. Design high-performance content caching and metadata delivery.", "['Architect media cache','Optimize distributed locks','Mentor junior engineers']", "['C++','Redis','System Design','Distributed Systems']"),
        (13, 7, 10, "3-5", "22-32 LPA", "SRE in AWS Infrastructure. Ensure reliability and high-availability of load balancers.", "['Build auto-scaling triggers','Automate server configurations','Write monitoring agents']", "['Python','Go','Docker','Kubernetes','AWS']"),
        
        # Google
        (14, 8, 2, "1-3", "24-32 LPA", "SDE I in Google Search infrastructure. Write optimized indexing pipelines.", "['Profile search crawl memory','Implement high-throughput C++ algorithms','Write test cases']", "['C++','Python','Algorithms','Data Structures']"),
        (15, 8, 3, "3-6", "42-60 LPA", "SDE II in Google Cloud Platform (GCP). Design API gateways and access controls.", "['Architect API gateways','Enforce low-latency authentication','Design distributed maps']", "['Go','GCP','Distributed Systems','System Design']"),
        (16, 8, 12, "2-5", "30-45 LPA", "ML SDE in Google Assistant. Train and serve low-latency conversation classifiers.", "['Serve deep learning models','Build prompt engineering filters','Optimize latency of ML APIs']", "['Python','TensorFlow','ElasticSearch','Algorithms']"),
        
        # Microsoft
        (17, 9, 2, "1-3", "18-25 LPA", "SDE I in Teams backend. Focus on chat messaging consistency and real-time syncing.", "['Implement Teams sync APIs','Optimize Azure SQL storage','Participate in code reviews']", "['C#','Java','MySQL','Azure']"),
        (18, 9, 3, "3-6", "32-48 LPA", "SDE II in Azure Storage. Build high-concurrency blob replication protocols.", "['Design Azure replication servers','Implement consensus protocols','Optimize IO operations']", "['C++','Go','Distributed Systems','System Design']"),
        
        # Meta
        (19, 10, 2, "1-3", "25-35 LPA", "SDE I in Instagram Feed. Focus on delivering relevant feed elements efficiently.", "['Optimize query execution plan','Implement feed caching','Write GraphQL endpoints']", "['Python','React','GraphQL','MySQL']"),
        (20, 10, 3, "4-7", "45-65 LPA", "SDE II in WhatsApp Messaging. Ensure end-to-end messaging reliability at scale.", "['Design messaging message brokers','Handle concurrent websocket connections','Minimize connection handshake latency']", "['Erlang','Go','Distributed Systems','System Design']")
    ]
    
    rows = []
    for idx, jd in enumerate(jds):
        # Convert single-quoted string arrays to valid JSON double-quoted arrays
        resp = jd[6].replace("'", '"') if isinstance(jd[6], str) else json.dumps(jd[6])
        reqs = jd[7].replace("'", '"') if isinstance(jd[7], str) else json.dumps(jd[7])
        
        rows.append({
            "jd_id": idx + 1,
            "company_id": jd[1],
            "role_id": jd[2],
            "experience_required_years": jd[3],
            "salary_range": jd[4],
            "description": jd[5],
            "responsibilities": resp,
            "requirements": reqs
        })
        
    write_csv(csv_path, ["jd_id", "company_id", "role_id", "experience_required_years", "salary_range", "description", "responsibilities", "requirements"], rows)

# ====================================================================
# 2. interview_experiences.csv
# ====================================================================
def generate_interview_experiences():
    csv_path = os.path.join(HIRING_DIR, "interview_experiences.csv")
    
    candidates = ["Taitiksh Sharma", "Vineela Reddy", "Ashok Mehta", "Sneha Garg", "Akhil Kumar", "Teja Reddy", "Vineela Verma", "Srishti Pandey", "Pranav Joshi", "Anjali Nair"]
    verdicts = ["Offered", "Rejected"]
    
    # 20 realistic Interview Experiences
    experiences = []
    exp_id = 1
    
    # Blinkit
    experiences.append((1, 2, "Taitiksh Sharma", "Offered", 8, "Very fast-paced. 1 DSA round on Graph BFS/DFS, 1 Machine Coding round building an in-memory rate limiter, and 1 LLD round.", "Understand Redis rate-limiting patterns and practice graph traversals under time constraints."))
    experiences.append((1, 8, "Akhil Kumar", "Offered", 7, "Focused on Go concurrency and channels. They asked me to explain the internal working of Kafka partitions.", "Practice Go channel synchronization and read about Kafka offsets and consumer groups."))
    
    # Zomato
    experiences.append((2, 2, "Sneha Garg", "Rejected", 8, "Asked tough dynamic programming problem (similar to Edit Distance) followed by high-level scaling queries.", "Focus on DP optimization and system design concepts like consistent hashing."))
    
    # Swiggy
    experiences.append((3, 11, "Teja Reddy", "Offered", 8, "Android mobile engineer loop. 1 round on Kotlin/Coroutines, 1 on building a simple offline database cache.", "Brush up Kotlin coroutine contexts, dispatchers, and Room SQLite database integration."))
    
    # Amazon
    experiences.append((7, 1, "Vineela Verma", "Offered", 7, "2 coding rounds (trees and arrays) and 1 behavioral round focused on Amazon Leadership Principles.", "Read and write STAR stories matching Amazon's 16 Leadership Principles. Practice Medium LeetCode trees."))
    experiences.append((7, 2, "Ashok Mehta", "Offered", 8, "Standard SDE I loop. Graph Dijkstra problem and building a distributed key-value store schema design.", "Be strong with graph algorithms and system design basics (availability, partitioning)."))
    experiences.append((7, 3, "Srishti Pandey", "Offered", 9, "HLD round on designing a Netflix-like media delivery network. Checked edge latency and database scaling.", "Watch HLD playlists (caching, CDNs, database sharding). Walk through trade-offs."))
    
    # Google
    experiences.append((8, 2, "Pranav Joshi", "Rejected", 9, "4 coding rounds. Hard algorithms (sliding window, graph coloring). The expectations on optimization are high.", "Optimize time and space bounds to absolute limits. Talk through every choice out loud."))
    experiences.append((8, 3, "Anjali Nair", "Offered", 10, "1 System Design round on Cloud Load Balancer, 1 Coding (hard binary search), and 1 Googlyness round.", "Practice explaining your thought process clearly and build solid system designs that highlight trade-offs."))
    
    # Microsoft
    experiences.append((9, 2, "Aditya Sen", "Offered", 8, "Coding round on LinkedList loops and Binary Tree serialization. System design round on Teams chat history.", "Be comfortable with Tree Traversals and design basic chat messaging architectures."))
    
    # Add dummy entries to reach 20 rows
    for i in range(10):
        comp_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        role_id = random.choice([1, 2, 3, 8, 9])
        candidate = random.choice(candidates)
        verdict = random.choice(verdicts)
        diff = random.randint(5, 10)
        
        experiences.append((
            comp_id,
            role_id,
            candidate,
            verdict,
            diff,
            f"Consisted of {random.randint(2,4)} rounds covering coding and project discussions. Interviewers were supportive.",
            "Practice core DSA, system design basics, and explain your code layout step-by-step."
        ))
        
    rows = []
    for idx, exp in enumerate(experiences):
        rows.append({
            "experience_id": idx + 1,
            "company_id": exp[0],
            "role_id": exp[1],
            "candidate_name": exp[2],
            "verdict": exp[3],
            "difficulty_rating": exp[4],
            "experience_story": exp[5],
            "tips": exp[6]
        })
        
    write_csv(csv_path, ["experience_id", "company_id", "role_id", "candidate_name", "verdict", "difficulty_rating", "experience_story", "tips"], rows)

# ====================================================================
# 3. skill_roadmaps.csv
# ====================================================================
def generate_skill_roadmaps():
    csv_path = os.path.join(LEARNING_DIR, "skill_roadmaps.csv")
    skills_csv_path = os.path.join(CAREER_DIR, "skills_master.csv")
    
    # Load all skill IDs and names
    skills = []
    with open(skills_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            skills.append((int(r["skill_id"]), r["skill_name"]))
            
    levels = ["Beginner", "Intermediate", "Advanced"]
    
    rows = []
    roadmap_id = 1
    
    for s_id, s_name in skills:
        for lvl in levels:
            if lvl == "Beginner":
                duration = 4
                goals = json.dumps([f"Understand syntax and setup", f"Build simple programs using {s_name}", f"Learn standard libraries"])
                resources = f"{s_name} crash course, Official {s_name} documentation"
                milestone = f"Complete 5 beginner console projects in {s_name}."
            elif lvl == "Intermediate":
                duration = 6
                goals = json.dumps([f"Explore concurrency and structures", f"Build CRUD backend service with {s_name}", f"Unit testing"])
                resources = f"Intermediate {s_name} programming course, GitHub boilerplate projects"
                milestone = f"Build and deploy a scalable microservice using {s_name}."
            else: # Advanced
                duration = 8
                goals = json.dumps([f"Memory profiling and GC tuning", f"Distributed scale structures with {s_name}", f"Architectural reviews"])
                resources = f"Advanced {s_name} design guides, Production scale open-source repos"
                milestone = f"Optimize latency and load throughput of a {s_name} production system by 30%."
                
            rows.append({
                "roadmap_id": roadmap_id,
                "skill_id": s_id,
                "level": lvl,
                "duration_weeks": duration,
                "learning_goals": goals,
                "recommended_resources": resources,
                "milestone": milestone
            })
            roadmap_id += 1
            
    write_csv(csv_path, ["roadmap_id", "skill_id", "level", "duration_weeks", "learning_goals", "recommended_resources", "milestone"], rows)

def main():
    print("Starting generation of new SDE datasets...")
    print("=" * 60)
    generate_job_descriptions()
    generate_interview_experiences()
    generate_skill_roadmaps()
    print("=" * 60)
    print("New SDE datasets created successfully!")

if __name__ == "__main__":
    main()
