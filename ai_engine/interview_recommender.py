# Interview Question Recommender - CareerCompass AI

COMPANY_QUESTIONS = {
    "blinkit": [
        {
            "id": 101, "category": "System Design", "difficulty": "Hard",
            "question": "Design a Real-Time Rider Dispatch & Geo-Tracking System for Blinkit (10-minute delivery)",
            "tags": ["System Design", "Distributed Systems", "Redis", "Kafka"],
            "solution": "Use Uber H3 or Google S2 geometry library for geo-spatial partitioning. Track active rider locations in Redis via GEOPOS/GEOADD. Broadcast status changes with WebSockets and buffer dispatch events using Apache Kafka.",
            "frequency": "Very Common"
        },
        {
            "id": 102, "category": "DSA", "difficulty": "Medium",
            "question": "Group Anagrams (Group matching lists of warehouse item SKU codes)",
            "tags": ["Arrays", "Hashing", "Strings", "Python", "Java"],
            "solution": "Use a hash map where the key is the sorted string of the word and the value is a list of anagrams. Runs in O(N * K log K) where K is max word length.",
            "frequency": "Very Common"
        },
        {
            "id": 103, "category": "LLD / DBMS", "difficulty": "Medium",
            "question": "Design an Idempotent Inventory Cart and Checkout System",
            "tags": ["PostgreSQL", "MySQL", "Distributed Systems", "Spring Boot"],
            "solution": "Implement optimistic locking on the inventory table (version column) or use Distributed Locks via Redis (Redlock) to prevent double allocation of items during high-traffic checkout.",
            "frequency": "Common"
        },
        {
            "id": 104, "category": "DSA", "difficulty": "Medium",
            "question": "Search in a 2D Matrix (representing warehouse grid coordinate paths)",
            "tags": ["Binary Search", "Arrays"],
            "solution": "Perform a binary search on the matrix rows or standard step-wise search starting from the top-right corner. Runs in O(log(M * N)) time complexity.",
            "frequency": "Common"
        }
    ],
    "amazon": [
        {
            "id": 201, "category": "System Design / LLD", "difficulty": "Hard",
            "question": "Design Amazon Locker Service",
            "tags": ["System Design", "Distributed Systems", "MySQL", "PostgreSQL"],
            "solution": "Create schema with Locker, LockerGroup, Order, and Package entities. Use a state pattern for locker state (Available, Booked, Occupied). Use a centralized notification system with SMS/Email OTP codes.",
            "frequency": "Very Common"
        },
        {
            "id": 202, "category": "DSA", "difficulty": "Medium",
            "question": "LRU Cache Implementation",
            "tags": ["Arrays", "Linked Lists", "Redis", "Java", "Go"],
            "solution": "Use a combination of a Doubly Linked List and a HashMap. The map enables O(1) key lookups, and the doubly linked list handles O(1) eviction and updates of the least-recently used elements.",
            "frequency": "Very Common"
        },
        {
            "id": 203, "category": "DSA", "difficulty": "Medium",
            "question": "Course Schedule (Resolving package build dependency trees)",
            "tags": ["Graphs", "Topological Sort", "Python", "Go"],
            "solution": "Represent courses and prerequisites as a directed graph. Detect cycles and output order using Kahn's algorithm (BFS using indegrees) or DFS-based topological sort. O(V + E) time.",
            "frequency": "Common"
        },
        {
            "id": 204, "category": "Behavioral", "difficulty": "Medium",
            "question": "Describe a situation where you had to make a quick decision without your manager's approval (Bias for Action)",
            "tags": ["System Design", "Distributed Systems"],
            "solution": "Structure response using STAR: explain the customer-impacting bug (Situation), your task to fix it immediately (Task), your deployment steps and risk mitigation (Action), and the successful results (Result).",
            "frequency": "Very Common"
        }
    ],
    "google": [
        {
            "id": 301, "category": "DSA", "difficulty": "Hard",
            "question": "Median of Two Sorted Arrays (Used in ad-click bidding sorting)",
            "tags": ["Binary Search", "Arrays", "Go", "Java"],
            "solution": "Apply binary search on the partition index of the smaller array. Calculate left and right elements on both sides to find balanced split. Time complexity must be O(log(min(M, N))).",
            "frequency": "Very Common"
        },
        {
            "id": 302, "category": "System Design", "difficulty": "Hard",
            "question": "Design Google Web Crawler at Scale",
            "tags": ["System Design", "Distributed Systems", "Docker", "Kubernetes"],
            "solution": "Design a master-worker architecture with URL Frontier, DNS Resolver, HTML Fetcher, Content Extractor, and Duplicate Detector. Store visited URLs in a highly scaled Bloom Filter.",
            "frequency": "Very Common"
        },
        {
            "id": 303, "category": "DSA", "difficulty": "Hard",
            "question": "Longest Increasing Path in a Matrix",
            "tags": ["Graphs", "DFS", "Python", "Java"],
            "solution": "Use Depth First Search (DFS) on each cell of the matrix. Cache the longest path from each cell in a memoization table to avoid duplicate subproblem computations. Runs in O(M * N) time.",
            "frequency": "Common"
        }
    ],
    "microsoft": [
        {
            "id": 401, "category": "DSA", "difficulty": "Medium",
            "question": "Binary Tree Zigzag Level Order Traversal",
            "tags": ["Trees", "BFS", "Java", "Go"],
            "solution": "Perform BFS level-by-level using a queue. For alternate levels, reverse the order of elements before adding to the result list. Runs in O(N) time and space.",
            "frequency": "Very Common"
        },
        {
            "id": 402, "category": "System Design", "difficulty": "Hard",
            "question": "Design a Distributed Rate Limiter for Microsoft Teams API",
            "tags": ["System Design", "Redis", "Distributed Systems", "gRPC"],
            "solution": "Use Redis with token bucket or sliding window log algorithms. Run Redis clustered nodes with replication and local in-memory backups to minimize latency overhead to <1ms.",
            "frequency": "Very Common"
        },
        {
            "id": 403, "category": "DSA", "difficulty": "Medium",
            "question": "Longest Palindromic Substring",
            "tags": ["Strings", "Dynamic Programming", "Python"],
            "solution": "Expand around centers (2N - 1 centers) or use dynamic programming to build a palindrome check table. Optimal time complexity is O(N^2) space O(1), or O(N) using Manacher's algorithm.",
            "frequency": "Common"
        }
    ],
    "flipkart": [
        {
            "id": 501, "category": "Machine Coding", "difficulty": "Hard",
            "question": "Design a Cab Booking Service (Flipkart Internal/Machine Coding)",
            "tags": ["Java", "Go", "System Design", "Spring Boot"],
            "solution": "Implement fully functional model classes: Rider, Cab, Trip. Provide methods to register cabs, book rides (picking nearest available cab matching filters), and complete trips. Ensure thread-safety.",
            "frequency": "Very Common"
        },
        {
            "id": 502, "category": "DSA", "difficulty": "Medium",
            "question": "Rotting Oranges (Simulating grid propagation)",
            "tags": ["Graphs", "BFS", "Arrays"],
            "solution": "Use BFS starting with all initial rotten oranges in a queue. Keep track of elapsed time and propagate rot to 4-directional neighbors. Return time or -1 if unreachable.",
            "frequency": "Very Common"
        },
        {
            "id": 503, "category": "System Design", "difficulty": "Hard",
            "question": "Design Flipkart's Flash Sale Inventory Reservation System",
            "tags": ["System Design", "Redis", "Kafka", "Distributed Systems"],
            "solution": "Use Redis lua script to perform atomic decrement of inventory. Place orders in Kafka queue for asynchronous processing, letting users know they are in the queue for confirmation.",
            "frequency": "Very Common"
        }
    ],
    "tcs": [
        {
            "id": 601, "category": "Programming Basics", "difficulty": "Easy",
            "question": "Reverse Words in a Given String",
            "tags": ["Strings", "Java", "Python"],
            "solution": "Split the string by space, reverse the array of words, and join them back with a single space. Handle multiple consecutive spaces correctly.",
            "frequency": "Very Common"
        },
        {
            "id": 602, "category": "DBMS", "difficulty": "Medium",
            "question": "Write SQL query to find the 2nd Highest Salary of an Employee",
            "tags": ["MySQL", "PostgreSQL", "DBMS"],
            "solution": "SELECT MAX(Salary) FROM Employee WHERE Salary < (SELECT MAX(Salary) FROM Employee) or use LIMIT OFFSET syntax.",
            "frequency": "Very Common"
        },
        {
            "id": 603, "category": "OOPs", "difficulty": "Medium",
            "question": "Explain Method Overloading vs Method Overriding with Example",
            "tags": ["Java", "Python", "OOPs"],
            "solution": "Overloading is compile-time polymorphism (same name, diff parameters in same class). Overriding is run-time polymorphism (child class overrides parent's method with same signature).",
            "frequency": "Common"
        }
    ],
    "infosys": [
        {
            "id": 701, "category": "DSA", "difficulty": "Medium",
            "question": "Longest Substring Without Repeating Characters",
            "tags": ["Strings", "Java", "Python", "NodeJS"],
            "solution": "Maintain a sliding window using two pointers. Store character indices in a HashMap. If a repeat is found, jump the left pointer to max of current left and duplicate index + 1.",
            "frequency": "Very Common"
        },
        {
            "id": 702, "category": "DSA", "difficulty": "Easy",
            "question": "Detect Loop in a Singly Linked List",
            "tags": ["Linked Lists", "Java", "Python"],
            "solution": "Use Floyd's Cycle Finding Algorithm (two pointers: fast and slow). If they meet, a loop exists. Otherwise, if fast reaches null, no loop exists.",
            "frequency": "Very Common"
        },
        {
            "id": 703, "category": "DBMS", "difficulty": "Medium",
            "question": "Explain SQL Joins, Indexing, and differences between Primary and Unique Keys",
            "tags": ["MySQL", "PostgreSQL", "DBMS"],
            "solution": "Primary Key is unique and cannot be null (only one per table). Unique Key allows one null value. Joins merge columns based on keys. B-Trees speed up search index lookups.",
            "frequency": "Common"
        }
    ]
}

def load_all_questions():
    import json
    import os
    import csv
    
    questions = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Try JSON first
    json_path = os.path.join(base_dir, "database", "datasets", "interview_questions", "interview_questions.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for idx, q in enumerate(data):
                    questions.append({
                        "id": idx + 1,
                        "category": q.get("category"),
                        "difficulty": q.get("difficulty"),
                        "question": q.get("question"),
                        "tags": q.get("tags", []),
                        "solution": q.get("answer"),
                        "frequency": q.get("frequency")
                    })
                return questions
        except Exception:
            pass
            
    # Try CSV next
    csv_path = os.path.join(base_dir, "database", "hiring_layer", "interview_questions.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tags = []
                    try:
                        import ast
                        tags = ast.literal_eval(row.get("tags", "[]"))
                    except Exception:
                        tags = [t.strip().strip("'\"") for t in row.get("tags", "[]").replace("[", "").replace("]", "").split(",") if t.strip()]
                    
                    questions.append({
                        "id": int(row.get("question_id", 1)),
                        "category": row.get("category"),
                        "difficulty": row.get("difficulty"),
                        "question": row.get("question"),
                        "tags": tags,
                        "solution": row.get("answer"),
                        "frequency": row.get("frequency")
                    })
                return questions
        except Exception:
            pass
            
    return []

def recommend_questions(missing_skills: dict, dream_company: str, dream_sector: str) -> list:
    """
    Selects actual interview questions matching the target company and targets
    any specific skill gaps identified in missing_skills.
    """
    flat_missing = []
    for priority, skills in missing_skills.items():
        flat_missing += [s.lower() for s in skills]

    questions_pool = load_all_questions()
    
    # Identify company-specific questions
    company_key = dream_company.lower().strip()
    company_specific = COMPANY_QUESTIONS.get(company_key, [])
    if not company_specific:
        company_specific = COMPANY_QUESTIONS["tcs"] + COMPANY_QUESTIONS["infosys"]
            
    matched_questions = []
    other_questions = []

    # Process company-specific questions first (highly relevant)
    for q in company_specific:
        score = 5  # Baseline score for company match
        for tag in q.get("tags", []):
            if tag.lower() in flat_missing:
                score += 3  # Higher bonus for company-specific gap match
        matched_questions.append((score, q))

    # Process generic questions from the pool
    for q in questions_pool:
        # Avoid duplicating if same question is already present in company_specific
        if any(cq["question"] == q["question"] for cq in company_specific):
            continue
            
        score = 0
        for tag in q.get("tags", []):
            if tag.lower() in flat_missing:
                score += 2  # Match for missing skills
            elif tag.lower() == dream_company.lower():
                score += 1  # Company name match in tags
        if score > 0:
            matched_questions.append((score, q))
        else:
            other_questions.append(q)

    # Sort matched questions by score descending
    matched_questions.sort(key=lambda x: x[0], reverse=True)
    sorted_matched = [q for score, q in matched_questions]

    # Combine prioritizing gap and company matches
    final_list = sorted_matched + other_questions
    
    # Return at most 8 questions for a comprehensive plan
    return final_list[:8]
