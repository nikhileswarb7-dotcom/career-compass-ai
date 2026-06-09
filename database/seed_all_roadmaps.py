# Seeding Script - CareerCompass AI
# Seeds target companies, roles, company-role mappings, and 840 custom qualification-company-role roadmaps.

import os
import sys
import json
import psycopg2

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "career_compass_ai",
    "user":     "postgres",
    "password": "Nikhil@2824"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

COMPANIES_DATA = [
    {
        "name": "Blinkit",
        "industry": "Quick Commerce",
        "founded_year": 2013,
        "description": "Blinkit is India's leading instant delivery platform delivering groceries and essentials in 10 minutes.",
        "mission": "To deliver everything in minutes.",
        "work_culture": "Fast-paced product engineering culture. Data-driven decisions. Ownership mindset.",
        "tech_stack": ["Java", "Python", "Spring Boot", "Kafka", "MySQL", "Redis", "AWS", "Docker", "Kubernetes", "Elasticsearch"],
        "hiring_process": ["Online Assessment", "DSA Interview", "Low Level Design", "High Level Design", "HR Round"],
        "salary_range": {"intern": "20k-50k/mo", "sde1": "10-18 LPA", "sde2": "18-30 LPA"},
        "career_growth": "Intern -> SDE-1 -> SDE-2 -> Senior SDE -> Tech Lead"
    },
    {
        "name": "Zomato",
        "industry": "FoodTech",
        "founded_year": 2008,
        "description": "Zomato is a technology platform connecting customers, restaurant partners, and delivery partners.",
        "mission": "Better food for more people.",
        "work_culture": "Collaborative, customer-obsessed, highly energetic, and scale-driven product culture.",
        "tech_stack": ["Golang", "PHP", "NodeJS", "Redis", "Kafka", "PostgreSQL", "React", "Docker", "AWS"],
        "hiring_process": ["Resume Shortlist", "OA", "Technical Round 1 (DSA)", "Technical Round 2 (LLD/HLD)", "HR Round"],
        "salary_range": {"intern": "25k-45k/mo", "sde1": "12-20 LPA", "sde2": "20-35 LPA"},
        "career_growth": "Intern -> SDE-1 -> SDE-2 -> Lead -> EM"
    },
    {
        "name": "Swiggy",
        "industry": "FoodTech",
        "founded_year": 2014,
        "description": "Swiggy is India's leading on-demand convenience platform, offering food delivery, grocery, and dining.",
        "mission": "To elevate the quality of life of urban consumers by offering unparalleled convenience.",
        "work_culture": "Bias for action, customer first, humility, and rigorous technical scalability reviews.",
        "tech_stack": ["Golang", "Java", "Python", "Redis", "Kafka", "PostgreSQL", "Docker", "Kubernetes", "AWS"],
        "hiring_process": ["OA", "DSA Round 1", "DSA Round 2", "System Design HLD/LLD", "HM Loop"],
        "salary_range": {"intern": "30k-50k/mo", "sde1": "14-22 LPA", "sde2": "22-38 LPA"},
        "career_growth": "Associate Developer -> SDE -> Senior SDE -> Staff SDE"
    },
    {
        "name": "Paytm",
        "industry": "FinTech",
        "founded_year": 2010,
        "description": "Paytm is India's leading mobile payments and financial services platform.",
        "mission": "To bring 500 million unserved and underserved Indians into the mainstream economy.",
        "work_culture": "High velocity delivery, high compliance and security focus, and massive scale banking transaction loads.",
        "tech_stack": ["Java", "Spring Boot", "MySQL", "HBase", "Kafka", "Redis", "Docker", "AWS"],
        "hiring_process": ["OA", "Technical Round 1", "Technical Round 2", "System Design & Concurrency", "HR"],
        "salary_range": {"intern": "15k-30k/mo", "sde1": "8-15 LPA", "sde2": "15-25 LPA"},
        "career_growth": "Software Engineer -> Senior Software Engineer -> Tech Lead"
    },
    {
        "name": "PhonePe",
        "industry": "FinTech",
        "founded_year": 2015,
        "description": "PhonePe is India's leading digital payments platform and UPI ecosystem provider.",
        "mission": "To build a large, secure, and reliable digital payments infrastructure.",
        "work_culture": "Strong emphasis on code readability, microservices independence, high test coverage, and strict architecture rules.",
        "tech_stack": ["Java", "Spring Boot", "Cassandra", "PostgreSQL", "Kafka", "Redis", "AWS", "Kubernetes"],
        "hiring_process": ["OA", "Machine Coding Round", "DSA/Algorithms", "System Design", "HM Loop"],
        "salary_range": {"intern": "35k-60k/mo", "sde1": "16-24 LPA", "sde2": "24-40 LPA"},
        "career_growth": "SDE-1 -> SDE-2 -> SDE-3 -> Architect"
    },
    {
        "name": "Flipkart",
        "industry": "E-Commerce",
        "founded_year": 2007,
        "description": "Flipkart is India's leading e-commerce marketplace.",
        "mission": "To make online shopping affordable and accessible.",
        "work_culture": "Rigorous technology benchmarks. Machine coding rounds test modular OOP design patterns under timed constraints.",
        "tech_stack": ["Java", "Scala", "MySQL", "Hadoop", "Kafka", "Redis", "Docker", "Private Cloud"],
        "hiring_process": ["OA", "Machine Coding Round", "Technical DSA Round", "System Design (HLD)", "HM/HR Round"],
        "salary_range": {"intern": "40k-70k/mo", "sde1": "18-26 LPA", "sde2": "26-42 LPA"},
        "career_growth": "SDE-1 -> SDE-2 -> SDE-3 -> Architect"
    },
    {
        "name": "Amazon",
        "industry": "E-Commerce",
        "founded_year": 1994,
        "description": "Amazon is a global technology MNC focusing on e-commerce, cloud computing, and digital streaming.",
        "mission": "To be Earth's most customer-centric company.",
        "work_culture": "Strict adherence to the 16 Leadership Principles (customer obsession, bias for action, write-ups).",
        "tech_stack": ["Java", "C++", "Python", "DynamoDB", "S3", "EC2", "Lambda", "SQS", "Redshift"],
        "hiring_process": ["OA", "Technical Loop 1 (DSA)", "Technical Loop 2 (DSA)", "System Design (HLD/LLD)", "Bar Raiser Round"],
        "salary_range": {"intern": "60k-100k/mo", "sde1": "20-32 LPA", "sde2": "32-55 LPA"},
        "career_growth": "SDE-1 (L4) -> SDE-2 (L5) -> SDE-3 (L6) -> Principal (L7)"
    },
    {
        "name": "Google",
        "industry": "Technology",
        "founded_year": 1998,
        "description": "Google is a global MNC specializing in search engine tech, cloud computing, and software platforms.",
        "mission": "To organize the world's information and make it universally accessible and useful.",
        "work_culture": "High autonomy, open source contribution, rigorous algorithmic reviews, and strong peer review processes.",
        "tech_stack": ["C++", "Golang", "Java", "Python", "Borg", "Spanner", "Bigtable", "TensorFlow", "GCP"],
        "hiring_process": ["Technical Phone Screen", "Onsite Round 1 (DSA)", "Onsite Round 2 (DSA)", "Onsite Round 3 (DSA)", "System Design", "Googliness Round"],
        "salary_range": {"intern": "80k-120k/mo", "sde1": "25-38 LPA", "sde2": "38-65 LPA"},
        "career_growth": "SDE II (L3) -> SDE III (L4) -> Senior SDE (L5) -> Staff (L6)"
    },
    {
        "name": "Microsoft",
        "industry": "Technology",
        "founded_year": 1975,
        "description": "Microsoft is a global technology MNC producing operating systems, office suites, and Azure cloud.",
        "mission": "To empower every person and every organization on the planet to achieve more.",
        "work_culture": "Growth mindset, cross-team collaboration, customer-centric engineering, and robust platform scale tools.",
        "tech_stack": ["C#", "C++", "TypeScript", "Azure", "SQL Server", "CosmosDB", "Docker", "Kubernetes"],
        "hiring_process": ["OA", "Technical Round 1 (DSA)", "Technical Round 2 (DSA/LLD)", "System Design (HLD)", "AA (As Appropriate) Round"],
        "salary_range": {"intern": "70k-110k/mo", "sde1": "22-35 LPA", "sde2": "35-58 LPA"},
        "career_growth": "SDE (59-60) -> SDE II (61-62) -> Senior SDE (63-64) -> Principal (65+)"
    },
    {
        "name": "Meta",
        "industry": "SocialMedia",
        "founded_year": 2004,
        "description": "Meta builds technologies that help people connect, find communities, and grow businesses.",
        "mission": "To give people the power to build community and bring the world closer together.",
        "work_culture": "Move fast, focus on impact, build awesome things, live in the future, and practice absolute engineering ownership.",
        "tech_stack": ["Python", "Hack", "C++", "React", "PyTorch", "Cassandra", "Memcached", "TAO", "Merlin"],
        "hiring_process": ["Technical Phone Screen", "Coding Loop 1", "Coding Loop 2", "System Design (HLD)", "Behavioral Round"],
        "salary_range": {"intern": "90k-140k/mo", "sde1": "30-45 LPA", "sde2": "45-75 LPA"},
        "career_growth": "E3 -> E4 -> E5 -> E6 -> E7"
    },
    {
        "name": "TCS",
        "industry": "IT Services",
        "founded_year": 1968,
        "description": "Tata Consultancy Services is an IT services, consulting and business solutions organization.",
        "mission": "To help customers achieve their business objectives by providing innovative, best-in-class consulting.",
        "work_culture": "Process-driven, structured compliance, enterprise project scaling, and long-term stable client relationships.",
        "tech_stack": ["Java", "Spring", "SQL Server", "Oracle", "JavaScript", "HTML/CSS", "AWS", "Azure"],
        "hiring_process": ["NQT (National Qualifier Test)", "Technical Interview (Java/DBMS)", "Managerial Interview", "HR Round"],
        "salary_range": {"intern": "10k-25k/mo", "sde1": "3.5-7 LPA", "sde2": "7-12 LPA"},
        "career_growth": "Assistant Systems Engineer -> Systems Engineer -> IT Consultant -> Project Manager"
    },
    {
        "name": "Infosys",
        "industry": "IT Services",
        "founded_year": 1981,
        "description": "Infosys is a global leader in next-generation digital services and consulting.",
        "mission": "To be a globally respected corporation that provides best-of-breed business solutions.",
        "work_culture": "Structured training programs at Mysore campus, process conformance, and scalable software services.",
        "tech_stack": ["Java", "Python", "SQL", "Spring Boot", "Angular", "Docker", "AWS", "SAP"],
        "hiring_process": ["Infosys Certification / InfyTQ", "Technical Interview (Java/OOP/SQL)", "HR Round"],
        "salary_range": {"intern": "10k-25k/mo", "sde1": "3.6-8 LPA", "sde2": "8-13 LPA"},
        "career_growth": "Systems Engineer -> Technology Analyst -> Technology Lead -> Project Manager"
    },
    {
        "name": "Uber",
        "industry": "Transportation / Tech",
        "founded_year": 2009,
        "description": "Uber is a global mobility-as-a-service provider, connecting riders with drivers.",
        "mission": "We ignite opportunity by setting the world in motion.",
        "work_culture": "Highly analytical SDE culture. Heavy focus on system design, low-latency concurrent processing, and microservices architecture.",
        "tech_stack": ["Golang", "Java", "Python", "Redis", "Kafka", "MySQL", "Docker", "Kubernetes", "AWS"],
        "hiring_process": ["OA", "DSA Round 1", "DSA Round 2", "System Design HLD/LLD", "Behavioral Loop"],
        "salary_range": {"intern": "50k-90k/mo", "sde1": "18-28 LPA", "sde2": "28-48 LPA"},
        "career_growth": "SDE-1 -> SDE-2 -> Senior -> Staff -> Principal"
    },
    {
        "name": "Atlassian",
        "industry": "Software / Collaboration",
        "founded_year": 2002,
        "description": "Atlassian builds tools like Jira, Confluence, and Trello to help teams organize and collaborate.",
        "mission": "To help unleash the potential of every team.",
        "work_culture": "Open, value-driven culture. Strong focus on code quality, testing, clean architectures, and collaboration values.",
        "tech_stack": ["Java", "Spring Boot", "Kotlin", "React", "AWS", "Docker", "PostgreSQL"],
        "hiring_process": ["Resume Screen", "OA", "Technical Interview (DSA)", "System Design (LLD)", "Values / Fit Round"],
        "salary_range": {"intern": "45k-80k/mo", "sde1": "16-25 LPA", "sde2": "25-45 LPA"},
        "career_growth": "P3 (Associate) -> P4 (SDE) -> P5 (Senior SDE) -> P6 (Principal)"
    },
    {
        "name": "Razorpay",
        "industry": "FinTech",
        "founded_year": 2014,
        "description": "Razorpay is a leading payments solution in India, allowing businesses to accept, process, and disburse payments.",
        "mission": "To power the financial infrastructure for businesses in India.",
        "work_culture": "Fast-growing startup culture. High ownership, product-driven engineering, and focus on security compliance.",
        "tech_stack": ["Golang", "PHP", "React", "Redis", "MySQL", "Docker", "AWS", "Kafka"],
        "hiring_process": ["OA", "DSA Round", "Machine Coding Round", "System Design (LLD/HLD)", "HR Round"],
        "salary_range": {"intern": "30k-50k/mo", "sde1": "14-22 LPA", "sde2": "22-38 LPA"},
        "career_growth": "SDE-1 -> SDE-2 -> SDE-3 -> Architect"
    },
    {
        "name": "Adobe",
        "industry": "Software / Creative Tech",
        "founded_year": 1982,
        "description": "Adobe is a global leader in digital media and digital marketing solutions.",
        "mission": "To change the world through digital experiences.",
        "work_culture": "Stable, innovation-focused corporate SDE culture. Focus on desktop applications, web platforms, and creative cloud solutions.",
        "tech_stack": ["C++", "Java", "Python", "React", "AWS", "Azure", "Docker"],
        "hiring_process": ["OA", "Technical Interview 1 (DSA)", "Technical Interview 2 (Core CS)", "System Design (LLD)", "HR Round"],
        "salary_range": {"intern": "40k-75k/mo", "sde1": "15-24 LPA", "sde2": "24-42 LPA"},
        "career_growth": "SDE-1 -> SDE-2 -> Member of Technical Staff (MTS) -> Senior MTS -> Principal"
    },
    {
        "name": "Walmart",
        "industry": "Retail / Tech",
        "founded_year": 1962,
        "description": "Walmart Global Tech builds technology platform solutions to power the world's largest retailer.",
        "mission": "To save people money so they can live better.",
        "work_culture": "Scale-driven SDE culture. Heavy emphasis on massive e-commerce architectures, supply chain systems, and cloud databases.",
        "tech_stack": ["Java", "Spring Boot", "React", "Cassandra", "Kafka", "Docker", "Kubernetes", "Azure"],
        "hiring_process": ["OA", "DSA Round 1", "DSA Round 2 / LLD", "System Design HLD", "HM Round"],
        "salary_range": {"intern": "35k-65k/mo", "sde1": "14-22 LPA", "sde2": "22-36 LPA"},
        "career_growth": "SDE-1 -> SDE-2 -> Senior SDE -> Staff SDE -> Principal"
    },
    {
        "name": "ServiceNow",
        "industry": "Enterprise Software / SaaS",
        "founded_year": 2004,
        "description": "ServiceNow provides a cloud computing platform to help companies manage digital workflows.",
        "mission": "We make the world of work, work better for people.",
        "work_culture": "Enterprise SaaS engineering. Emphasis on platform scalability, automation workflows, JavaScript/Java frameworks, and database efficiency.",
        "tech_stack": ["Java", "JavaScript", "React", "MySQL", "Docker", "Kubernetes", "AWS"],
        "hiring_process": ["OA", "DSA Technical Round 1", "DSA/LLD Technical Round 2", "System Design", "HM/HR Loop"],
        "salary_range": {"intern": "40k-70k/mo", "sde1": "16-24 LPA", "sde2": "24-40 LPA"},
        "career_growth": "Associate Software Engineer -> Software Engineer -> Senior Software Engineer -> Staff SDE"
    }
]

ROLES_DATA = [
    {"name": "Software Development Engineer", "desc": "Designs and builds backend microservices, handles DSA algorithms, and works on system scale."},
    {"name": "Software Development Engineer I (SDE-1)", "desc": "Entry-level SDE role. Focuses on writing clean code, modular components, and solving DSA problems."},
    {"name": "Junior Software Engineer", "desc": "Assists in component development, bug fixing, database setups, and API testing under mentorship."},
    {"name": "Trainee Engineer", "desc": "Apprenticeship SDE role. Learns programming syntax, OOP foundations, basic git controls, and system logs."},
    {"name": "QA Automation Engineer", "desc": "Writes browser automation test scripts (Playwright/Selenium), test cases, and asserts API endpoints."},
    {"name": "Backend Engineer", "desc": "Focuses on backend architectures, high-performance database queries, caching layers, and messaging pipelines."},
    {"name": "Frontend Engineer", "desc": "Focuses on user interfaces, state managers, React, TypeScript, NextJS, CSS animations, and browser rendering."},
    {"name": "SRE / DevOps Engineer", "desc": "Handles cloud infrastructure, Docker container registries, CI/CD pipelines, Kubernetes, and log observability dashboards."},
    {"name": "Mobile Engineer", "desc": "Builds mobile applications using Swift (iOS) or Kotlin (Android), mobile architectures, and app store deployment workflows."},
    {"name": "AI / ML Engineer", "desc": "Focuses on mathematical stats, machine learning pipelines, deep learning networks (PyTorch/TensorFlow), and MLOps serving APIs."}
]

def seed_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SET search_path TO career_compass_ai, public;")
    
    print("Loading existing companies...")
    cur.execute("SELECT company_id, company_name FROM companies;")
    existing_companies = {r[1].lower(): r[0] for r in cur.fetchall()}
    
    next_company_id = max(existing_companies.values()) + 1 if existing_companies else 1
    
    print("Clearing companies table...")
    # Truncating companies table will cascade delete company_roles, roadmaps, and roadmap_stages
    cur.execute("TRUNCATE TABLE companies CASCADE;")
    
    print("Seeding Companies...")
    companies_map = {}
    for comp in COMPANIES_DATA:
        name_low = comp["name"].lower()
        if name_low in existing_companies:
            comp_id = existing_companies[name_low]
        else:
            comp_id = next_company_id
            next_company_id += 1
            
        companies_map[name_low] = comp_id
        
        # Determine company_type
        c_type = "Product"
        if comp["name"] in ["Amazon", "Google", "Microsoft", "Meta", "Uber", "Atlassian", "Adobe"]:
            c_type = "MNC"
        elif comp["name"] in ["TCS", "Infosys"]:
            c_type = "IT Services"
            
        cur.execute("""
            INSERT INTO companies (company_id, company_name, industry, founded_year, description, mission, work_culture, tech_stack, hiring_process, salary_range, career_growth, company_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO UPDATE 
            SET company_name = EXCLUDED.company_name, industry = EXCLUDED.industry, founded_year = EXCLUDED.founded_year, description = EXCLUDED.description, mission = EXCLUDED.mission, work_culture = EXCLUDED.work_culture, tech_stack = EXCLUDED.tech_stack, hiring_process = EXCLUDED.hiring_process, salary_range = EXCLUDED.salary_range, career_growth = EXCLUDED.career_growth, company_type = EXCLUDED.company_type;
        """, (
            comp_id, comp["name"], comp["industry"], comp["founded_year"], comp["description"], comp["mission"],
            comp["work_culture"], json.dumps(comp["tech_stack"]), json.dumps(comp["hiring_process"]),
            json.dumps(comp["salary_range"]), comp["career_growth"], c_type
        ))

        # Seed company_metadata
        tier = 2
        hiring_bar = 70.0
        cgpa = 7.0
        backlogs = False
        hiring_count = 150
        
        if comp["name"] in ["Google", "Microsoft", "Meta", "Amazon", "Blinkit", "Zomato", "Swiggy", "PhonePe", "Uber", "Atlassian", "Adobe", "Walmart", "Razorpay", "ServiceNow"]:
            tier = 1
            hiring_bar = 90.0
            cgpa = 8.0
            hiring_count = 50
        elif comp["name"] in ["TCS", "Infosys"]:
            tier = 3
            hiring_bar = 45.0
            cgpa = 6.0
            backlogs = True
            hiring_count = 1000
            
        cur.execute("""
            INSERT INTO company_metadata (company_id, tier, hiring_bar_score, target_cgpa, allow_backlogs, annual_hiring_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO UPDATE
            SET tier = EXCLUDED.tier, hiring_bar_score = EXCLUDED.hiring_bar_score, target_cgpa = EXCLUDED.target_cgpa, allow_backlogs = EXCLUDED.allow_backlogs, annual_hiring_count = EXCLUDED.annual_hiring_count;
        """, (comp_id, tier, hiring_bar, cgpa, backlogs, hiring_count))

    # Reset companies sequence to max + 1
    cur.execute("SELECT setval('companies_company_id_seq', COALESCE((SELECT MAX(company_id)+1 FROM companies), 1), false);")

    # Reset roles sequence first to avoid unique key conflicts with roles 1-12
    cur.execute("SELECT setval('roles_role_id_seq', COALESCE((SELECT MAX(role_id)+1 FROM roles), 1), false);")

    print("Seeding Roles...")
    roles_map = {}
    for r in ROLES_DATA:
        if r["name"] == "Software Development Engineer":
            cur.execute("""
                INSERT INTO roles (role_id, role_name, description, responsibilities, experience_levels, career_level)
                VALUES (99, %s, %s, '[]', '[]', 'Mid')
                ON CONFLICT (role_name) DO UPDATE SET description = EXCLUDED.description, career_level = EXCLUDED.career_level
                RETURNING role_id;
            """, (r["name"], r["desc"]))
        else:
            cur.execute("""
                INSERT INTO roles (role_name, description, responsibilities, experience_levels, career_level)
                VALUES (%s, %s, '[]', '[]', 'Mid')
                ON CONFLICT (role_name) DO UPDATE SET description = EXCLUDED.description, career_level = EXCLUDED.career_level
                RETURNING role_id;
            """, (r["name"], r["desc"]))
        roles_map[r["name"].lower()] = cur.fetchone()[0]

    # Reset roles sequence again
    cur.execute("SELECT setval('roles_role_id_seq', COALESCE((SELECT MAX(role_id)+1 FROM roles), 1), false);")

    print("Seeding Company Roles Mapping...")
    company_roles_map = {} # keys: (company_id, role_id) -> company_role_id
    for c_name, c_id in companies_map.items():
        for r_name, r_id in roles_map.items():
            cur.execute("""
                INSERT INTO company_roles (company_id, role_id, cgpa_cutoff, backlogs_allowed, notes)
                VALUES (%s, %s, 6.0, TRUE, %s)
                ON CONFLICT (company_id, role_id) DO UPDATE SET notes = EXCLUDED.notes
                RETURNING company_role_id;
            """, (c_id, r_id, f"Preparation path for {c_name} SDE position."))
            company_roles_map[(c_id, r_id)] = cur.fetchone()[0]

    print("Loading Qualifications...")
    cur.execute("SELECT qualification_id, qualification_name FROM qualifications;")
    quals = {r[1]: r[0] for r in cur.fetchall()}

    # Clear existing roadmaps
    print("Clearing existing roadmaps & stages...")
    cur.execute("TRUNCATE TABLE roadmap_stages, roadmaps CASCADE;")
    
    print("Generating 840 Roadmaps and 3360 custom stages...")
    roadmaps_seeded = 0
    stages_seeded = 0

    # We map qualifications and duration
    quals_meta = {
        "1st Year Student": {"months": 48, "weeks_per_stage": 12},
        "2nd Year Student": {"months": 36, "weeks_per_stage": 9},
        "3rd Year Student": {"months": 18, "weeks_per_stage": 5},
        "4th Year Student": {"months": 6, "weeks_per_stage": 3},
        "Fresh Graduate": {"months": 6, "weeks_per_stage": 3},
        "Trainee Engineer": {"months": 9, "weeks_per_stage": 6},
        "Junior Software Engineer": {"months": 12, "weeks_per_stage": 7}
    }

    # Generate custom stages based on target role
    def get_stages_for_role(role_name, company_name, w_stage):
        r_low = role_name.lower()
        c_name = company_name.capitalize()
        
        if "frontend" in r_low:
            return [
                {
                    "title": "HTML, CSS, JavaScript UI Foundations",
                    "focus": f"Mastery of DOM, ES6+, dynamic layouts, and web interfaces tailored for {c_name}'s web entry points.",
                    "goals": ["Build responsive layout wireframes", "Understand JavaScript closures, promises, and async/await", "Solve 30 CSS/JS coding exercises"],
                    "milestone": "Build 3 vanilla JS interactive projects from scratch."
                },
                {
                    "title": f"React & TypeScript Integration",
                    "focus": f"Learn component lifecycles, state handlers, static types, and custom hooks matching {c_name}'s frontend standard.",
                    "goals": ["Understand state props and functional hooks", "Integrate TypeScript in React applications", "Implement modular UI classes"],
                    "milestone": "Create and publish a complete React + TS dashboard on GitHub."
                },
                {
                    "title": f"NextJS & Core Frontend Orchestration",
                    "focus": f"Learn server-side rendering, static site generation, and state management (Zustand/Redux) to optimize page load speeds.",
                    "goals": ["Build NextJS routing workflows", "Configure global store states", "Optimize bundle packages to improve core web vitals"],
                    "milestone": "Develop a high-performance e-commerce landing page with API fetches."
                },
                {
                    "title": "Frontend Verification & Deploy Pipeline",
                    "focus": f"Automate test cases (Jest, Playwright) and configure CI/CD deployments to test user flows under high simulation.",
                    "goals": ["Write unit tests using Jest", "Perform end-to-end user path testing via Playwright", "Configure automated Vercel/Netlify deploy hooks"],
                    "milestone": "Complete 5 mock frontend engineering technical interviews."
                }
            ]
        elif "backend" in r_low:
            return [
                {
                    "title": "Backend Languages & Clean Design OOPs",
                    "focus": f"Mastery of backend syntaxes (Go, Java, Python) and object architectures for high-capacity workflows at {c_name}.",
                    "goals": ["Master language collections and multithreading syntax", "Implement OOP design principles", "Write clean unit tests for class methods"],
                    "milestone": "Build 5 console-based object-oriented applications."
                },
                {
                    "title": "Database Normalization & Query Speed",
                    "focus": f"Design relational schemas, ACID consistency transactional operations, and index configurations in PostgreSQL/MySQL.",
                    "goals": ["Design 3NF relational schemas", "Write complex SQL joins and aggregation queries", "Analyze query execution plans and index hotspots"],
                    "milestone": "Implement a relational database featuring optimized B-Tree indexing."
                },
                {
                    "title": "REST APIs, Caching & Log Streaming",
                    "focus": f"Expose endpoints using Spring Boot or Go, deploy Redis caches, and configure Apache Kafka log topic processors.",
                    "goals": ["Build secure REST controllers", "Implement cache-aside workflows using Redis", "Stream system event logs to Kafka topics"],
                    "milestone": "Deploy a backend microservice cluster combining databases, cache, and messaging queue."
                },
                {
                    "title": "Distributed Blueprints & System Design",
                    "focus": f"Master high-level system components (load balancers, CDNs, replication) and low-level design diagrams matching {c_name}'s scale.",
                    "goals": ["Explain CAP theorem tradeoffs", "Design low-level classes (e.g. Parking Lot, Dispatcher)", "Architect highly-scalable distributed configurations"],
                    "milestone": "Create and explain 3 full system design HLD blueprints."
                }
            ]
        elif "devops" in r_low or "sre" in r_low:
            return [
                {
                    "title": "Linux Administration & Web Protocols",
                    "focus": f"Bash automation scripting, Linux filesystem security, and TCP/IP network protocol routing parameters for {c_name}.",
                    "goals": ["Learn bash shell operations", "Automate server tasks using cron and bash", "Understand DNS, HTTP, and load balancing routing"],
                    "milestone": "Configure a local web server and automate log parsing via Bash."
                },
                {
                    "title": "Container Isolation & CI/CD Pipelines",
                    "focus": f"Docker image builds, Docker Compose configurations, and GitHub Actions workflow testing automation.",
                    "goals": ["Write lightweight Dockerfiles", "Orchestrate multi-container setups using Compose", "Build automated pipeline pushes to container registries"],
                    "milestone": "Configure an automated CI/CD pipeline building and testing docker images."
                },
                {
                    "title": "Infrastructure as Code & Kubernetes Scale",
                    "focus": f"Manage multi-tier cloud infrastructure using Terraform and orchestrate live microservices with Kubernetes.",
                    "goals": ["Write Terraform scripts for AWS/GCP resource allocation", "Understand Kubernetes Pods, ReplicaSets, and Services", "Deploy local clusters via Minikube"],
                    "milestone": "Provision a load-balanced cluster routing traffic across active pods."
                },
                {
                    "title": "System Observability, Alerts & Security",
                    "focus": f"Implement Prometheus scraping metrics, Grafana dashboards, Elasticsearch logging, and secure infrastructure channels.",
                    "goals": ["Expose metrics endpoints and scraper rules", "Design Grafana monitoring alert thresholds", "Analyze system load traces and security controls"],
                    "milestone": "Build a centralized logging and monitoring server with real-time alerts."
                }
            ]
        elif "ai" in r_low or "ml" in r_low:
            return [
                {
                    "title": "Mathematical Foundations & Pandas Data",
                    "focus": f"Linear algebra, multivariate calculus, stats models, and NumPy/Pandas processing pipelines at {c_name}.",
                    "goals": ["Manipulate large datasets via Pandas", "Perform Exploratory Data Analysis (EDA) plotting", "Understand regression bounds and probability functions"],
                    "milestone": "Clean and preprocess a raw dataset of 10,000 transaction records."
                },
                {
                    "title": "Classical Machine Learning & Feature Selection",
                    "focus": f"Regression models, decision trees, random forests, clustering, and Scikit-Learn training paradigms.",
                    "goals": ["Train classifiers and regressors", "Perform cross-validation and hyperparameter tuning", "Validate models using F1-score and confusion matrices"],
                    "milestone": "Deploy a validated predictive classifier using Scikit-Learn."
                },
                {
                    "title": "Deep Learning & Language Networks",
                    "focus": f"Artificial neural networks, CNNs, sequence modeling, PyTorch/TensorFlow framework controls, and Transformers.",
                    "goals": ["Implement neural network feedforward layers", "Train convolutional filters for image categorizing", "Fine-tune pretrained transformers for NLP tagging"],
                    "milestone": "Train and save a deep learning model classifying input sequences."
                },
                {
                    "title": "MLOps Serving APIs & Model Tracking",
                    "focus": f"Expose inference pipelines via FastAPI, containerize ML models, and manage experiment records using MLflow.",
                    "goals": ["Expose model predictions via REST routes", "Build lightweight inference Docker containers", "Track parameters and metrics logs in MLflow"],
                    "milestone": "Serve a containerized ML classifier handling high-frequency inference requests."
                }
            ]
        elif "mobile" in r_low:
            return [
                {
                    "title": "Kotlin/Swift Programming & Async Coroutines",
                    "focus": f"Mobile OOP architectures, Kotlin (Android) / Swift (iOS) syntax, and thread handling concepts for {c_name}'s apps.",
                    "goals": ["Master language collections and static functions", "Implement concurrency structures", "Write modular utilities for data conversion"],
                    "milestone": "Implement 5 standalone helper utilities in Kotlin/Swift."
                },
                {
                    "title": "Native SDK Views & Lifecycle States",
                    "focus": f"Building interfaces via Jetpack Compose/SwiftUI, Activity lifecycles, and SQLite room database storage.",
                    "goals": ["Design UI screens using native constraint rules", "Manage local state changes", "Persist mobile states into local relational DBs"],
                    "milestone": "Build a local-storage mobile note-taking app."
                },
                {
                    "title": "API Network Integration & MVVM Pattern",
                    "focus": f"Retrieve data over HTTP via Retrofit/URLSession, apply MVVM separation of concerns, and mock api tests.",
                    "goals": ["Execute asynchronous network fetches", "Implement clean repository patterns", "Separate UI layout from view-model controller logic"],
                    "milestone": "Build a live app consuming external REST endpoints."
                },
                {
                    "title": "Mobile App Security, UI Mocks & Deploy",
                    "focus": f"Write Espresso/UI tests, secure local API keys, configure OAuth logins, and package deployment files for App Store.",
                    "goals": ["Automate UI interactions using test frameworks", "Enforce local encryption keys", "Export packaged bundle release binaries"],
                    "milestone": "Configure automated UI unit testing suite for mobile application."
                }
            ]
        elif "qa" in r_low:
            return [
                {
                    "title": "Software QA Fundamentals & HTML Dom",
                    "focus": f"Software testing life cycle (STLC), test case design, bug tracking flow, and browser DOM path selectors at {c_name}.",
                    "goals": ["Write clear test cases and failure reports", "Understand locator mechanics (XPath, CSS selectors)", "Analyze DOM node hierarchies in browsers"],
                    "milestone": "Complete manual testing suite for an e-commerce catalog page."
                },
                {
                    "title": "Browser Automation (Playwright & Selenium)",
                    "focus": f"Write browser automation actions using Playwright/Selenium and implement Page Object Model.",
                    "goals": ["Automate form inputs and button clicks", "Handle dynamic overlays and delay waits", "Apply Page Object Model (POM) pattern classes"],
                    "milestone": "Automate complete e-commerce user checkout journey."
                },
                {
                    "title": "REST API Automated Assertions",
                    "focus": f"API request mocking, assertion libraries (Supertest, Postman), response schema validation, and DB verification.",
                    "goals": ["Write automated API payload checks", "Assert backend database updates post-API trigger", "Test API headers, auth tokens, and status codes"],
                    "milestone": "Build automated API testing suite asserting DB records."
                },
                {
                    "title": "Continuous Test Pipelines & Load Testing",
                    "focus": f"Integrating automated test scripts in Jenkins/GitHub Actions pipelines and conducting load tests (k6).",
                    "goals": ["Execute test runs inside CI containers", "Simulate concurrent user loads using k6 scripts", "Generate automatic HTML reports on build completion"],
                    "milestone": "Integrate test validations in automated server build cycles."
                }
            ]
        else: # SDE General, SDE-1, Junior SDE, Trainee
            return [
                {
                    "title": "Programming Foundation & Class Models",
                    "focus": f"Mastery of core language syntax (Java/C++), basic logic scripts, and OOP encapsulation principles for {c_name}.",
                    "goals": ["Learn data types, operators, loops, arrays", "Design modular class inheritance models", "Solve 50 easy coding challenges"],
                    "milestone": "Build 3 standalone console-based OOP tools."
                },
                {
                    "title": "Data Structures & Runtime Complexities",
                    "focus": f"Linear and non-linear DSA architectures, recursion trees, sorting/searching algorithms, and Big O notations.",
                    "goals": ["Master Arrays, Lists, Stacks, Queues, and BSTs", "Calculate time and space complexities", "Solve 100+ LeetCode problems (Easy + Medium)"],
                    "milestone": "Solve 100 LeetCode problems with high efficiency."
                },
                {
                    "title": f"Relational Schema Design & Web APIs",
                    "focus": f"ACID parameters, normalized relational tables, SQL queries, and backend REST APIs.",
                    "goals": ["Design normalized databases", "Expose secure REST controllers", "Connect backend servers to SQL tables"],
                    "milestone": "Deploy a complete CRUD web service connected to PostgreSQL."
                },
                {
                    "title": "System Scalability & Placement Prep Loop",
                    "focus": f"High Level Design and Low Level Design diagrams, OOP class pattern reviews, and mock interview loops tailored for {c_name}.",
                    "goals": ["Learn load balancer routing and cache-aside patterns", "Design OOP classes for system flows", "Complete 3 timed technical mock interviews"],
                    "milestone": "Pass mock technical loops and finalize ATS-optimized resume."
                }
            ]

    # Iterating and seeding combinations
    for q_name, q_id in quals.items():
        meta = quals_meta[q_name]
        total_months = meta["months"]
        w_stage = meta["weeks_per_stage"]
        
        for c_name, c_id in companies_map.items():
            # Match case
            c_title = next(c["name"] for c in COMPANIES_DATA if c["name"].lower() == c_name)
            
            for r_name, r_id in roles_map.items():
                r_title = next(r["name"] for r in ROLES_DATA if r["name"].lower() == r_name)
                
                # Fetch company_role_id
                company_role_id = company_roles_map[(c_id, r_id)]
                
                overview = f"{q_name} custom roadmap template targeting {r_title} at {c_title} over {total_months} months. Covers role-specific stack, databases, distributed designs, and placement prep milestones."
                
                cur.execute("""
                    INSERT INTO roadmaps (qualification_id, company_role_id, total_duration_months, overview)
                    VALUES (%s, %s, %s, %s)
                    RETURNING roadmap_id;
                """, (q_id, company_role_id, total_months, overview))
                roadmap_id = cur.fetchone()[0]
                roadmaps_seeded += 1
                
                # Generate stages
                stages = get_stages_for_role(r_title, c_title, w_stage)
                for idx, st in enumerate(stages):
                    cur.execute("""
                        INSERT INTO roadmap_stages (roadmap_id, stage_number, stage_title, duration_weeks, focus_area, learning_goals, weekly_hours, milestone)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING stage_id;
                    """, (
                        roadmap_id, idx + 1, st["title"], w_stage, st["focus"],
                        json.dumps(st["goals"]), 15, st["milestone"]
                    ))
                    stage_id = cur.fetchone()[0]
                    stages_seeded += 1
                    
    print("Seeding Role Skills...")
    cur.execute("TRUNCATE TABLE role_skills RESTART IDENTITY CASCADE;")

    cur.execute("SELECT skill_id, skill_name FROM skills;")
    skills_db = {r[1]: r[0] for r in cur.fetchall()}

    role_skill_profiles = {
        "software development engineer": {
            "High": ["Java", "DSA (Combined)", "DBMS", "Operating Systems", "Computer Networks", "Spring Boot", "System Design"],
            "Medium": ["SQL", "MySQL", "Git & GitHub", "Low Level Design", "High Level Design", "Object Oriented Programming", "REST APIs"],
            "Low": ["Docker", "Redis", "Microservices"]
        },
        "software development engineer i (sde-1)": {
            "High": ["Java", "DSA (Combined)", "DBMS"],
            "Medium": ["SQL", "MySQL", "Git & GitHub", "Object Oriented Programming", "REST APIs"],
            "Low": ["Operating Systems", "Computer Networks", "Docker"]
        },
        "junior software engineer": {
            "High": ["Java", "DSA (Combined)"],
            "Medium": ["SQL", "Git & GitHub", "Object Oriented Programming"],
            "Low": ["DBMS", "REST APIs"]
        },
        "trainee engineer": {
            "High": ["C Programming", "Java"],
            "Medium": ["Data Structures", "Object Oriented Programming", "Git & GitHub"],
            "Low": ["Linux Basics"]
        },
        "qa automation engineer": {
            "High": ["Python", "Git & GitHub"],
            "Medium": ["Java", "SQL", "Object Oriented Programming"],
            "Low": ["REST APIs"]
        },
        "backend engineer": {
            "High": ["Python", "SQL", "PostgreSQL", "Redis", "Microservices"],
            "Medium": ["Java", "Spring Boot", "REST APIs", "Message Queues (Kafka)", "Low Level Design", "Git & GitHub"],
            "Low": ["Docker", "AWS Basics", "System Design"]
        },
        "frontend engineer": {
            "High": ["Git & GitHub", "Object Oriented Programming"],
            "Medium": ["SQL", "Data Structures", "Algorithms", "REST APIs"],
            "Low": ["Docker", "System Design"]
        },
        "sre / devops engineer": {
            "High": ["Docker", "AWS Basics", "Linux Basics", "Git & GitHub"],
            "Medium": ["Python", "Computer Networks", "Operating Systems", "Message Queues (Kafka)"],
            "Low": ["System Design", "PostgreSQL", "Redis"]
        },
        "mobile engineer": {
            "High": ["Java", "Git & GitHub", "Object Oriented Programming"],
            "Medium": ["Data Structures", "Algorithms", "REST APIs"],
            "Low": ["DBMS"]
        },
        "ai / ml engineer": {
            "High": ["Python", "Algorithms", "Data Structures"],
            "Medium": ["SQL", "PostgreSQL", "Git & GitHub"],
            "Low": ["AWS Basics", "Linux Basics"]
        }
    }

    role_skills_seeded = 0
    for (c_id, r_id), company_role_id in company_roles_map.items():
        cur.execute("SELECT role_name FROM roles WHERE role_id = %s;", (r_id,))
        role_name = cur.fetchone()[0].lower().strip()
        
        profile = role_skill_profiles.get(role_name)
        if not profile:
            profile = role_skill_profiles["software development engineer"]
            
        for priority, skill_names in profile.items():
            for s_name in skill_names:
                s_id = skills_db.get(s_name)
                if s_id:
                    cur.execute("""
                        INSERT INTO role_skills (company_role_id, skill_id, priority)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (company_role_id, s_id, priority))
                    role_skills_seeded += 1
                    
    print(f"Seeded {role_skills_seeded} role skills in PostgreSQL.")

    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\nSUCCESS! Seeded {roadmaps_seeded} roadmaps and {stages_seeded} stages in PostgreSQL.")

if __name__ == "__main__":
    seed_database()
