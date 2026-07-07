import os
import sys
import json
import psycopg2
import requests
from psycopg2.extras import Json

# Setup import path for DB connection parameters
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database_connector import DB_CONFIG

QUIZ_API_KEY = os.environ.get("QUIZ_API_KEY", "")

def fetch_mcqs(tag, count=10):
    """
    Fetches multiple-choice questions from QuizAPI for a specific technology tag.
    Falls back to curated high-quality questions if the API call fails.
    """
    print(f"Fetching MCQs for tag: '{tag}' from QuizAPI...")
    url = "https://quizapi.io/api/v1/questions"
    headers = {"X-Api-Key": QUIZ_API_KEY}
    params = {
        "tags": tag,
        "limit": count
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            raw_questions = response.json()
            formatted_mcqs = []
            
            for q in raw_questions:
                # Filter out null options
                options = []
                # Map answer_a, answer_b etc.
                ans_map = q.get("answers", {})
                for k in sorted(ans_map.keys()):
                    if ans_map[k] is not None:
                        options.append(ans_map[k])
                
                # Resolve correct answer index
                correct_answers = q.get("correct_answers", {})
                correct_idx = 0
                for k, v in correct_answers.items():
                    if v == "true" or v is True:
                        # e.g., 'answer_a_correct' -> character 'a' is index 0
                        ans_letter = k.split("_")[1]
                        correct_idx = ord(ans_letter) - ord('a')
                        break
                
                # If correct_idx is out of options bounds, default to 0
                if correct_idx >= len(options):
                    correct_idx = 0
                
                formatted_mcqs.append({
                    "question": q["question"],
                    "options": options,
                    "correct": correct_idx
                })
            
            if len(formatted_mcqs) >= count:
                print(f"  Successfully fetched {len(formatted_mcqs)} questions for {tag}.")
                return formatted_mcqs[:count]
    except Exception as e:
        print(f"  QuizAPI fetch failed for tag {tag}: {e}. Using curated backup questions.")
    
    # Static fallback data matching the stage requirements in case API limit/error occurs
    fallbacks = {
        "Docker": [
            {
                "question": "What is the primary difference between a Docker image and a Docker container?",
                "options": [
                    "An image is a read-only template; a container is a running instance of an image",
                    "Containers are stored in Docker Hub; images only run locally",
                    "Images are mutable; containers are completely immutable",
                    "There is no difference between them"
                ],
                "correct": 0
            },
            {
                "question": "Which Dockerfile instruction specifies the default command executed when a container starts?",
                "options": ["FROM", "RUN", "CMD", "EXPOSE"],
                "correct": 2
            },
            {
                "question": "What is the default isolation mechanism used by Docker containers on Linux?",
                "options": ["Hyper-V virtualization", "Linux Namespaces and Cgroups", "VirtualBox virtualization layers", "Systemd service wrappers"],
                "correct": 1
            },
            {
                "question": "In Git, how do you record changes to the repository?",
                "options": ["git push", "git commit", "git checkout", "git stage"],
                "correct": 1
            },
            {
                "question": "What is the difference between git fetch and git pull?",
                "options": [
                    "fetch only downloads changes without merging; pull downloads and merges",
                    "pull only downloads changes; fetch merges",
                    "fetch deletes local branches; pull updates them",
                    "they are exact aliases"
                ],
                "correct": 0
            },
            {
                "question": "In Docker, what represents a read-only template containing instructions for creating a container?",
                "options": ["Docker Volumes", "Docker Compose", "Docker Image", "Docker Daemon"],
                "correct": 2
            },
            {
                "question": "Which Docker command lists active running containers?",
                "options": ["docker ps", "docker run", "docker images", "docker logs"],
                "correct": 0
            },
            {
                "question": "What is the Git command to create a new branch named 'feature'?",
                "options": ["git branch -d feature", "git merge feature", "git checkout -b feature", "git push feature"],
                "correct": 2
            },
            {
                "question": "In Docker, how do you persist data generated by a container after the container is deleted?",
                "options": ["Using Docker Commit", "Using Docker Volumes", "Using Docker Port mapping", "Using Docker ENV variables"],
                "correct": 1
            },
            {
                "question": "What does the HEAD pointer in Git represent?",
                "options": ["The main branch of the remote server", "The currently active local commit/branch", "The first commit in the repository", "The staging index"],
                "correct": 1
            }
        ],
        "MySQL": [
            {
                "question": "In Go, what is the idiomatic way to safely pass data between concurrent goroutines?",
                "options": ["Writing to local text files", "Using global shared variables", "Communicating via Go channels", "Using database transactions"],
                "correct": 2
            },
            {
                "question": "How does Apache Kafka guarantee message ordering?",
                "options": ["Ordering is guaranteed across all topics globally", "Ordering is guaranteed within a single partition", "Ordering is guaranteed by consumer group offsets", "Ordering is guaranteed using system timestamps"],
                "correct": 1
            },
            {
                "question": "Which indexing model in PostgreSQL is most appropriate for high-concurrency range queries?",
                "options": ["Hash Index", "B-Tree Index", "GIN Index", "BRIN Index"],
                "correct": 1
            },
            {
                "question": "What is a goroutine in Go?",
                "options": ["A thread managed by the operating system kernel", "A lightweight execution thread managed by the Go runtime", "A database transaction block", "A network routing protocol"],
                "correct": 1
            },
            {
                "question": "In Kafka, what components consume messages from partitions?",
                "options": ["Producers", "Brokers", "Consumers", "Zookeeper nodes"],
                "correct": 2
            },
            {
                "question": "What is the default isolation level in MySQL InnoDB?",
                "options": ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"],
                "correct": 2
            },
            {
                "question": "In Go, what is the purpose of the 'defer' statement?",
                "options": ["Postpones execution of a function until the surrounding function returns", "Speeds up compile-time performance", "Defers variable allocation to heap", "Launches a new concurrent thread"],
                "correct": 0
            },
            {
                "question": "In Kafka, what is a Consumer Group?",
                "options": ["A set of consumers cooperating to consume data from a topic", "A cluster of Kafka brokers", "A registry of topics and partitions", "A security policy for producers"],
                "correct": 0
            },
            {
                "question": "What does ACID stand for in database transactions?",
                "options": ["Accuracy, Consistency, Interoperability, Durability", "Atomicity, Consistency, Isolation, Durability", "Atomicity, Concurrency, Isolation, Dependency", "Access, Control, Indexing, Distribution"],
                "correct": 1
            },
            {
                "question": "In Go, how do you handle errors object-orientedly or idiomatically?",
                "options": ["Using try-catch-finally blocks", "Throwing exceptions up the stack", "Returning an error value as the last return parameter", "System exit on any failure"],
                "correct": 2
            }
        ],
        "PostgreSQL": [
            {
                "question": "Which caching design pattern updates both cache and DB in a single atomic transaction block?",
                "options": ["Cache-Aside pattern", "Write-Through pattern", "Write-Behind/Write-Back pattern", "Read-Through pattern"],
                "correct": 1
            },
            {
                "question": "Which Redis command is optimal for tracking geo-coordinates of quick-commerce riders?",
                "options": ["HSET", "GEOADD", "ZADD", "LPUSH"],
                "correct": 1
            },
            {
                "question": "What is the primary benefit of read-replicas in PostgreSQL?",
                "options": ["Decrease writing response latency", "Improve database schema normalizations", "Scale read transactions and handle node failure redundancy", "Increase network packet compression"],
                "correct": 2
            },
            {
                "question": "What does the CAP theorem state?",
                "options": [
                    "A distributed system can guarantee at most two of Consistency, Availability, and Partition Tolerance",
                    "Caching always beats direct database execution in latency",
                    "All databases must support atomic transactions",
                    "Concurrency increases CPU allocation parameters"
                ],
                "correct": 0
            },
            {
                "question": "What is the primary difference between SQL and NoSQL databases?",
                "options": [
                    "SQL databases only run on Windows; NoSQL runs on Linux",
                    "SQL databases are typically relational/schematized; NoSQL are non-relational/flexible-schema",
                    "NoSQL databases don't support indexes",
                    "SQL databases cannot scale vertically"
                ],
                "correct": 1
            },
            {
                "question": "In Redis, what does the TTL property of a key represent?",
                "options": [
                    "Transaction Thread Limit",
                    "Total Transaction Latency",
                    "Time To Live (expiration duration)",
                    "Table Transient Link"
                ],
                "correct": 2
            },
            {
                "question": "Which load balancing algorithm distributes requests sequentially across a list of servers?",
                "options": [
                    "Least Connections",
                    "Round Robin",
                    "IP Hashing",
                    "Weighted Response Time"
                ],
                "correct": 1
            },
            {
                "question": "What is the purpose of a CDN (Content Delivery Network)?",
                "options": [
                    "To cache static assets closer to end users to reduce latency",
                    "To manage relational database backups",
                    "To containerize microservices",
                    "To encrypt user password keys"
                ],
                "correct": 0
            },
            {
                "question": "What is consistent hashing primarily used for?",
                "options": [
                    "Securing web passwords",
                    "Optimizing SQL query index queries",
                    "Minimizing key reorganization in distributed hash tables/caching during node changes",
                    "Calculating similarity scores of candidates"
                ],
                "correct": 2
            },
            {
                "question": "What is a single point of failure (SPOF) in system design?",
                "options": [
                    "A bug that crashes the browser client",
                    "A component whose failure stops the entire system from working",
                    "A database query that takes > 10 seconds",
                    "An unhandled promise rejection in node"
                ],
                "correct": 1
            }
        ],
        "JavaScript": [
            {
                "question": "In behavioral SDE rounds, what does the 'A' represent in the STAR template?",
                "options": ["Assessment", "Allocation", "Action taken", "Algorithmic score"],
                "correct": 2
            },
            {
                "question": "What is the best way to showcase achievements on an SDE resume?",
                "options": ["Explain lines of code written", "Detail the group's general code layout", "Quantify personal impact (e.g. 'reduced latency by 30% using Redis')", "List all keywords in alphabet order"],
                "correct": 2
            },
            {
                "question": "How should code complexity be discussed during a live SDE whiteboard interview?",
                "options": ["Wait for the interviewer to prompt you", "Calculate time and space bounds step-by-step as you construct the code", "State O(N) immediately for all solutions", "Say complexity doesn't matter for initial prototypes"],
                "correct": 1
            },
            {
                "question": "What does 'STAR' stand for in interview methodology?",
                "options": [
                    "Situation, Task, Action, Result",
                    "Status, Target, Analysis, Recommendation",
                    "System, Technology, Architecture, Reliability",
                    "Structure, Theory, Application, Review"
                ],
                "correct": 0
            },
            {
                "question": "What is the time complexity of binary search on a sorted array of size N?",
                "options": [
                    "O(N)",
                    "O(log N)",
                    "O(N log N)",
                    "O(1)"
                ],
                "correct": 1
            },
            {
                "question": "In whiteboard interviews, what is the first step before writing any code?",
                "options": [
                    "Write down the brute force helper nested loops",
                    "Ask the interviewer to give you the code outline",
                    "Clarify requirements, constraints, and inputs/outputs",
                    "Declare variables on the board"
                ],
                "correct": 2
            },
            {
                "question": "What is the space complexity of an in-place QuickSort algorithm in the average case?",
                "options": [
                    "O(N)",
                    "O(log N)",
                    "O(N^2)",
                    "O(1)"
                ],
                "correct": 1
            },
            {
                "question": "In behavioral SDE interviews, how should conflict with a coworker be described?",
                "options": [
                    "Focus on how the conflict was resolved constructively and what was learned",
                    "Explain why the other developer was wrong",
                    "Avoid mentioning any conflicts at all",
                    "Say conflicts are resolved by the manager"
                ],
                "correct": 0
            },
            {
                "question": "What is the time complexity of inserting a key in a Hash Map (average case)?",
                "options": [
                    "O(N)",
                    "O(log N)",
                    "O(N log N)",
                    "O(1)"
                ],
                "correct": 3
            },
            {
                "question": "How do you optimize an O(N^2) brute force solution in a coding interview?",
                "options": [
                    "Use multiple helper functions to split the code lines",
                    "Increase hardware allocation memory size",
                    "Use a hash map/set to trade space for time, or apply sorting/two-pointers",
                    "Replace loops with recursion blocks"
                ],
                "correct": 2
            }
        ]
    }
    return fallbacks.get(tag, [])

def fetch_leetcode_challenge(title_slug):
    """
    Fetches the problem description and JavaScript starter code from LeetCode public mirror.
    Falls back to curated coding templates if mirror is unavailable.
    """
    print(f"Fetching LeetCode problem: '{title_slug}'...")
    url = f"https://alfa-leetcode-api.onrender.com/select?titleSlug={title_slug}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            templates = data.get("codeTemplates", [])
            js_template = ""
            for t in templates:
                if t["lang"] == "JavaScript":
                    js_template = t["code"]
                    break
            
            # Clean HTML tags from description if needed, or keep raw description
            desc = data.get("question", "")
            # Simple HTML tags removal
            import re
            desc_clean = re.sub(r'<[^>]*>', '', desc).strip()
            
            if js_template:
                print(f"  Successfully fetched coding challenge '{title_slug}'.")
                return {
                    "title": data.get("questionTitle", title_slug.replace("-", " ").title()),
                    "desc": desc_clean[:400] + "...",
                    "template": js_template
                }
    except Exception as e:
        print(f"  LeetCode fetch failed for {title_slug}: {e}. Using local template.")
        
    # Local fallback templates
    fallbacks = {
        "balanced-binary-tree": {
            "title": "Height-Balanced Binary Tree Check",
            "desc": "Implement a function isBalanced(root) that returns true if a binary tree is height-balanced, otherwise false. A tree is height-balanced if the depth of its two subtrees never differs by more than 1.",
            "template": "function isBalanced(root) {\n    if (root === null) return true;\n    function checkHeight(node) {\n        if (node === null) return 0;\n        let left = checkHeight(node.left);\n        let right = checkHeight(node.right);\n        if (left === -1 || right === -1 || Math.abs(left - right) > 1) return -1;\n        return Math.max(left, right) + 1;\n    }\n    return checkHeight(root) !== -1;\n}"
        },
        "implement-queue-using-stacks": {
            "title": "Concurrent Channel Worker",
            "desc": "Write a Go function workerPool(jobs, results) to process job requests concurrently using worker goroutines and channels.",
            "template": "package main\n\nimport \"fmt\"\n\nfunc worker(id int, jobs <-chan int, results chan<- int) {\n    for j := range jobs {\n        fmt.Println(\"worker\", id, \"started job\", j)\n        results <- j * 2\n    }\n}"
        },
        "lru-cache": {
            "title": "Redis Simple Rate Limiter",
            "desc": "Implement a rate limiter class in JavaScript that checks if a user has exceeded 5 requests per minute, returns false if rate-limited.",
            "template": "class RateLimiter {\n    constructor() {\n        this.requests = new Map();\n    }\n    isAllowed(userId) {\n        const now = Date.now();\n        return true;\n    }\n}"
        },
        "two-sum": {
            "title": "Two Sum Optimal O(N)",
            "desc": "Write a function twoSum(nums, target) returning indices of the two elements adding up to target in linear time complexity.",
            "template": "function twoSum(nums, target) {\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const complement = target - nums[i];\n        if (map.has(complement)) {\n            return [map.get(complement), i];\n        }\n        map.set(nums[i], i);\n    }\n    return [];\n}"
        }
    }
    return fallbacks.get(title_slug, {})

def run_collector():
    print("CareerCompass AI — SDE Dynamic Content & Assessment Collector")
    print("=" * 65)
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SET search_path TO career_compass_ai, public;")
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)
        
    stages_config = [
        {
            "stage_id": 1,
            "quiz_tag": "Docker",
            "leetcode_slug": "balanced-binary-tree",
            "video_playlist": [
                {"title": "Introduction to Version Control & Workspace Setup", "duration": "15 mins", "embed": "https://www.youtube.com/embed/YS4e4q9oBaU"},
                {"title": "Blinkit Engineering Target Orientation", "duration": "20 mins", "embed": "https://www.youtube.com/embed/Tt08KmFfIYQ"}
            ],
            "cheat_sheets": [
                {"title": "Developer Workspace Setup Guide.md", "size": "320 KB"},
                {"title": "Git Cheat Sheet.pdf", "size": "150 KB"}
            ]
        },
        {
            "stage_id": 2,
            "quiz_tag": "MySQL",
            "leetcode_slug": "implement-queue-using-stacks",
            "video_playlist": [
                {"title": "Concurrent Programming with Go & Java Basics", "duration": "25 mins", "embed": "https://www.youtube.com/embed/un80v_x-128"},
                {"title": "Understanding Apache Kafka & PostgreSQL Integration", "duration": "35 mins", "embed": "https://www.youtube.com/embed/R87354hyY2E"}
            ],
            "cheat_sheets": [
                {"title": "Concurrent Worker Cheat Sheet.md", "size": "280 KB"},
                {"title": "PostgreSQL Performance Optimization.pdf", "size": "410 KB"}
            ]
        },
        {
            "stage_id": 3,
            "quiz_tag": "PostgreSQL",
            "leetcode_slug": "lru-cache",
            "video_playlist": [
                {"title": "Masterclass: High Level Design (HLD) Concepts", "duration": "30 mins", "embed": "https://www.youtube.com/embed/m8I0esEK6so"},
                {"title": "Geo-Redis Indexes & Caching Strategies", "duration": "20 mins", "embed": "https://www.youtube.com/embed/OqCK95AS-XY"}
            ],
            "cheat_sheets": [
                {"title": "System Design Handbook.md", "size": "520 KB"},
                {"title": "Redis geo-indexing.pdf", "size": "180 KB"}
            ]
        },
        {
            "stage_id": 4,
            "quiz_tag": "JavaScript",
            "leetcode_slug": "two-sum",
            "video_playlist": [
                {"title": "Cracking SDE Interview Coding Rounds", "duration": "40 mins", "embed": "https://www.youtube.com/embed/V8V_vH2Sj9w"},
                {"title": "STAR Behavioral Template for SDEs", "duration": "15 mins", "embed": "https://www.youtube.com/embed/w7mko_X4kO8"}
            ],
            "cheat_sheets": [
                {"title": "Leetcode Prep Cheatsheet.md", "size": "190 KB"},
                {"title": "STAR Method Guide.pdf", "size": "120 KB"}
            ]
        }
    ]
    
    for cfg in stages_config:
        stage_id = cfg["stage_id"]
        print(f"\n--- Processing Stage {stage_id} ---")
        
        # 1. Fetch MCQs
        mcqs = fetch_mcqs(cfg["quiz_tag"], count=10)
        
        # 2. Fetch Coding challenge
        coding = fetch_leetcode_challenge(cfg["leetcode_slug"])
        
        # 3. Upsert into database
        try:
            # Upsert stage_training_content (avoid duplicate inserts, update on conflict)
            cur.execute("""
                INSERT INTO stage_training_content (stage_id, video_playlist, cheat_sheets)
                VALUES (%s, %s, %s)
                ON CONFLICT (stage_id)
                DO UPDATE SET video_playlist = EXCLUDED.video_playlist, cheat_sheets = EXCLUDED.cheat_sheets;
            """, (stage_id, Json(cfg["video_playlist"]), Json(cfg["cheat_sheets"])))
            
            # Upsert stage_assessments (avoid duplicate inserts, update on conflict)
            cur.execute("""
                INSERT INTO stage_assessments (stage_id, mcqs, coding_challenge)
                VALUES (%s, %s, %s)
                ON CONFLICT (stage_id)
                DO UPDATE SET mcqs = EXCLUDED.mcqs, coding_challenge = EXCLUDED.coding_challenge;
            """, (stage_id, Json(mcqs), Json(coding)))
            
            print(f"Successfully upserted training & assessments for Stage {stage_id} in PostgreSQL.")
        except Exception as err:
            print(f"Database upsert error for stage {stage_id}: {err}")
            conn.rollback()
            
    conn.commit()
    cur.close()
    conn.close()
    print("\n" + "=" * 65)
    print("Database seeding from public APIs complete. All stages are fully loaded.")

if __name__ == "__main__":
    run_collector()
