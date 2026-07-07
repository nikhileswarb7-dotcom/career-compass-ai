-- ============================================================
--  CareerCompass AI — Seed Data
--  Blinkit × Software Development Engineer
-- ============================================================

-- ============================================================
-- 1. COMPANY — Blinkit
-- ============================================================
INSERT INTO companies (company_name, industry, founded_year, description, mission, work_culture, tech_stack, hiring_process, salary_range, career_growth)
VALUES (
    'Blinkit',
    'Quick Commerce',
    2013,
    'Blinkit (formerly Grofers) is India''s leading instant delivery platform delivering groceries and essentials in 10 minutes.',
    'To deliver everything in minutes.',
    'Fast-paced product engineering culture. Data-driven decisions. Ownership mindset. Engineers are expected to design scalable systems at high traffic.',
    '["Java","Python","Spring Boot","Kafka","MySQL","Redis","AWS","Docker","Kubernetes","Elasticsearch"]',
    '["Online Assessment (DSA)","DSA Interview Round","Low Level Design (LLD)","High Level Design (HLD)","HR Round"]',
    '{"intern":"20,000-50,000/month","sde1":"10-18 LPA","sde2":"18-30 LPA","senior_sde":"30-50 LPA"}',
    'Intern → SDE-1 → SDE-2 → Senior SDE → Tech Lead → Engineering Manager'
);

-- ============================================================
-- 2. ROLE — Software Development Engineer
-- ============================================================
INSERT INTO roles (role_id, role_name, description, responsibilities, experience_levels)
VALUES (
    99,
    'Software Development Engineer',
    'Designs, builds, and maintains backend services and APIs at scale. Responsible for system reliability, performance, and feature development.',
    '["Design and develop scalable backend services","Write clean, tested, production-ready code","Design REST APIs and microservices","Database design and query optimization","Participate in system design and architecture reviews","Code reviews and mentoring juniors","On-call responsibility for critical services"]',
    '["Intern","SDE-1","SDE-2","Senior SDE","Tech Lead","Engineering Manager"]'
);

-- ============================================================
-- 3. COMPANY ROLE MAPPING
-- ============================================================
INSERT INTO company_roles (company_id, role_id, cgpa_cutoff, backlogs_allowed, notes)
VALUES (
    (SELECT company_id FROM companies WHERE company_name = 'Blinkit'),
    (SELECT role_id FROM roles WHERE role_name = 'Software Development Engineer'),
    6.5,
    FALSE,
    'Blinkit SDE hiring is placement + off-campus. Focus on DSA + System Design + Backend.'
);

-- ============================================================
-- 4. QUALIFICATIONS
-- ============================================================
INSERT INTO qualifications (qualification_name, level_order, available_time, learning_speed, urgency, typical_duration_months, description) VALUES
('1st Year Student',          1, 'Very High', 'Slow',      'Low',      48, 'Maximum time available. Build strong fundamentals. No rush.'),
('2nd Year Student',          2, 'High',      'Medium',    'Low',      36, 'Good time window. Start DSA and core subjects.'),
('3rd Year Student',          3, 'Medium',    'Fast',      'High',     18, 'Placement season approaching. Accelerated preparation required.'),
('4th Year Student',          4, 'Low',       'Very Fast', 'Critical',  6, 'Final year. Interview-ready mode. Maximum focus on DSA + System Design.'),
('Fresh Graduate',            5, 'Low',       'Very Fast', 'Critical',  6, 'Recently graduated. Needs focused interview sprint preparation.'),
('Trainee Engineer',          6, 'Very Low',  'Fast',      'High',      9, 'Working professional. Limited time. Production-level skills needed.'),
('Junior Software Engineer',  7, 'Very Low',  'Fast',      'Medium',   12, 'Already working. Needs to strengthen System Design and advanced skills.');

-- ============================================================
-- 5. SKILLS
-- ============================================================
INSERT INTO skills (skill_name, category, difficulty) VALUES
-- Programming
('C Programming',       'Programming', 'Beginner'),
('C++',                 'Programming', 'Intermediate'),
('Java',                'Programming', 'Intermediate'),
('Python',              'Programming', 'Beginner'),
('SQL',                 'Programming', 'Intermediate'),
-- Core CS
('Data Structures',             'Core CS', 'Intermediate'),
('Algorithms',                  'Core CS', 'Advanced'),
('DSA (Combined)',               'Core CS', 'Advanced'),
('DBMS',                        'Core CS', 'Intermediate'),
('Operating Systems',           'Core CS', 'Intermediate'),
('Computer Networks',           'Core CS', 'Intermediate'),
('Object Oriented Programming', 'Core CS', 'Intermediate'),
-- Backend
('Spring Boot',         'Backend', 'Intermediate'),
('REST APIs',           'Backend', 'Intermediate'),
('Microservices',       'Backend', 'Advanced'),
('Message Queues (Kafka)', 'Backend', 'Advanced'),
-- Databases
('MySQL',               'Database', 'Intermediate'),
('PostgreSQL',          'Database', 'Intermediate'),
('Redis',               'Database', 'Intermediate'),
-- Cloud & DevOps
('Git & GitHub',        'DevOps',  'Beginner'),
('Docker',              'DevOps',  'Intermediate'),
('AWS Basics',          'Cloud',   'Intermediate'),
('Linux Basics',        'DevOps',  'Beginner'),
-- Design
('Low Level Design',    'System Design', 'Advanced'),
('High Level Design',   'System Design', 'Advanced'),
('System Design',       'System Design', 'Advanced'),
('Go',                  'Programming',   'Intermediate'),
('Kubernetes',          'DevOps',        'Advanced');

-- ============================================================
-- 6. ROLE SKILLS (Blinkit SDE Requirements)
-- ============================================================
INSERT INTO role_skills (company_role_id, skill_id, priority) VALUES
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Java'),                    'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='DSA (Combined)'),            'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='DBMS'),                      'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Operating Systems'),         'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Computer Networks'),         'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Spring Boot'),               'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='System Design'),             'High'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='SQL'),                       'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='MySQL'),                     'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Git & GitHub'),              'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Low Level Design'),          'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='High Level Design'),         'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Object Oriented Programming'),'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='REST APIs'),                 'Medium'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Docker'),                    'Low'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Redis'),                     'Low'),
((SELECT company_role_id FROM company_roles cr JOIN companies c ON cr.company_id=c.company_id JOIN roles r ON cr.role_id=r.role_id WHERE c.company_name='Blinkit' AND r.role_name='Software Development Engineer'), (SELECT skill_id FROM skills WHERE skill_name='Microservices'),             'Low');

-- ============================================================
-- 7. INTERACTIVE TRAINING LECTURE VIDEOS & BLUEPRINTS
-- ============================================================

INSERT INTO stage_training_content (stage_id, video_playlist, cheat_sheets) VALUES
(1, '[
    {"title": "Introduction to Version Control & Workspace Setup", "duration": "15 mins", "embed": "https://www.youtube.com/embed/YS4e4q9oBaU"},
    {"title": "Blinkit Engineering Target Orientation", "duration": "20 mins", "embed": "https://www.youtube.com/embed/Tt08KmFfIYQ"}
]', '[
    {"title": "Developer Workspace Setup Guide.md", "size": "320 KB"},
    {"title": "Git Cheat Sheet.pdf", "size": "150 KB"}
]'),
(2, '[
    {"title": "Concurrent Programming with Go & Java Basics", "duration": "25 mins", "embed": "https://www.youtube.com/embed/un80v_x-128"},
    {"title": "Understanding Apache Kafka & PostgreSQL Integration", "duration": "35 mins", "embed": "https://www.youtube.com/embed/R87354hyY2E"}
]', '[
    {"title": "Concurrent Worker Cheat Sheet.md", "size": "280 KB"},
    {"title": "PostgreSQL Performance Optimization.pdf", "size": "410 KB"}
]'),
(3, '[
    {"title": "Masterclass: High Level Design (HLD) Concepts", "duration": "30 mins", "embed": "https://www.youtube.com/embed/m8I0esEK6so"},
    {"title": "Geo-Redis Indexes & Caching Strategies", "duration": "20 mins", "embed": "https://www.youtube.com/embed/OqCK95AS-XY"}
]', '[
    {"title": "System Design Handbook.md", "size": "520 KB"},
    {"title": "Redis geo-indexing.pdf", "size": "180 KB"}
]'),
(4, '[
    {"title": "Cracking SDE Interview Coding Rounds", "duration": "40 mins", "embed": "https://www.youtube.com/embed/V8V_vH2Sj9w"},
    {"title": "STAR Behavioral Template for SDEs", "duration": "15 mins", "embed": "https://www.youtube.com/embed/w7mko_X4kO8"}
]', '[
    {"title": "Leetcode Prep Cheatsheet.md", "size": "190 KB"},
    {"title": "STAR Method Guide.pdf", "size": "120 KB"}
]');

-- ============================================================
-- 8. CHECKPOINT ASSESSMENTS (MCQS & CODING TEMPLATES)
-- ============================================================

INSERT INTO stage_assessments (stage_id, mcqs, coding_challenge) VALUES
(1, '[
    {"question": "What is the primary purpose of version control systems like Git?", "options": ["To automate backend deployments", "To track change history and collaborate on source code", "To host SQL databases in the cloud", "To speed up local machine boot times"], "correct": 1},
    {"question": "Which technology is primarily used to isolate and run microservices in uniform containers?", "options": ["Kafka", "Docker", "Redis", "Elasticsearch"], "correct": 1},
    {"question": "What is the average search complexity in a balanced Binary Search Tree (BST)?", "options": ["O(N)", "O(N log N)", "O(log N)", "O(1)"], "correct": 2},
    {"question": "In Git, how do you record changes to the repository?", "options": ["git push", "git commit", "git checkout", "git stage"], "correct": 1},
    {"question": "What is the difference between git fetch and git pull?", "options": ["fetch only downloads changes without merging; pull downloads and merges", "pull only downloads changes; fetch merges", "fetch deletes local branches; pull updates them", "they are exact aliases"], "correct": 0},
    {"question": "In Docker, what represents a read-only template containing instructions for creating a container?", "options": ["Docker Volumes", "Docker Compose", "Docker Image", "Docker Daemon"], "correct": 2},
    {"question": "Which Docker command lists active running containers?", "options": ["docker ps", "docker run", "docker images", "docker logs"], "correct": 0},
    {"question": "What is the Git command to create a new branch named ''feature''?", "options": ["git branch -d feature", "git merge feature", "git checkout -b feature", "git push feature"], "correct": 2},
    {"question": "In Docker, how do you persist data generated by a container after the container is deleted?", "options": ["Using Docker Commit", "Using Docker Volumes", "Using Docker Port mapping", "Using Docker ENV variables"], "correct": 1},
    {"question": "What does the HEAD pointer in Git represent?", "options": ["The main branch of the remote server", "The currently active local commit/branch", "The first commit in the repository", "The staging index"], "correct": 1}
]', '{
    "title": "Height-Balanced Binary Tree Check",
    "desc": "Implement a function isBalanced(root) that returns true if a binary tree is height-balanced, otherwise false. A tree is height-balanced if the depth of its two subtrees never differs by more than 1.",
    "template": "function isBalanced(root) {\\n    if (root === null) return true;\\n    function checkHeight(node) {\\n        if (node === null) return 0;\\n        let left = checkHeight(node.left);\\n        let right = checkHeight(node.right);\\n        if (left === -1 || right === -1 || Math.abs(left - right) > 1) return -1;\\n        return Math.max(left, right) + 1;\\n    }\\n    return checkHeight(root) !== -1;\\n}"
}'),
(2, '[
    {"question": "In Go, what is the idiomatic way to safely pass data between concurrent goroutines?", "options": ["Writing to local text files", "Using global shared variables", "Communicating via Go channels", "Using database transactions"], "correct": 2},
    {"question": "How does Apache Kafka guarantee message ordering?", "options": ["Ordering is guaranteed across all topics globally", "Ordering is guaranteed within a single partition", "Ordering is guaranteed by consumer group offsets", "Ordering is guaranteed using system timestamps"], "correct": 1},
    {"question": "Which indexing model in PostgreSQL is most appropriate for high-concurrency range queries?", "options": ["Hash Index", "B-Tree Index", "GIN Index", "BRIN Index"], "correct": 1},
    {"question": "What is a goroutine in Go?", "options": ["A thread managed by the operating system kernel", "A lightweight execution thread managed by the Go runtime", "A database transaction block", "A network routing protocol"], "correct": 1},
    {"question": "In Kafka, what components consume messages from partitions?", "options": ["Producers", "Brokers", "Consumers", "Zookeeper nodes"], "correct": 2},
    {"question": "What is the default isolation level in MySQL InnoDB?", "options": ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"], "correct": 2},
    {"question": "In Go, what is the purpose of the ''defer'' statement?", "options": ["Postpones execution of a function until the surrounding function returns", "Speeds up compile-time performance", "Defers variable allocation to heap", "Launches a new concurrent thread"], "correct": 0},
    {"question": "In Kafka, what is a Consumer Group?", "options": ["A set of consumers cooperating to consume data from a topic", "A cluster of Kafka brokers", "A registry of topics and partitions", "A security policy for producers"], "correct": 0},
    {"question": "What does ACID stand for in database transactions?", "options": ["Accuracy, Consistency, Interoperability, Durability", "Atomicity, Consistency, Isolation, Durability", "Atomicity, Concurrency, Isolation, Dependency", "Access, Control, Indexing, Distribution"], "correct": 1},
    {"question": "In Go, how do you handle errors object-orientedly or idiomatically?", "options": ["Using try-catch-finally blocks", "Throwing exceptions up the stack", "Returning an error value as the last return parameter", "System exit on any failure"], "correct": 2}
]', '{
    "title": "Concurrent Channel Worker",
    "desc": "Write a Go function workerPool(jobs, results) to process job requests concurrently using worker goroutines and channels.",
    "template": "package main\\n\\nimport \"fmt\"\\n\\nfunc worker(id int, jobs <-chan int, results chan<- int) {\\n    for j := range jobs {\\n        fmt.Println(\"worker\", id, \"started job\", j)\\n        results <- j * 2\\n    }\\n}"
}'),
(3, '[
    {"question": "Which caching design pattern updates both cache and DB in a single atomic transaction block?", "options": ["Cache-Aside pattern", "Write-Through pattern", "Write-Behind/Write-Back pattern", "Read-Through pattern"], "correct": 1},
    {"question": "Which Redis command is optimal for tracking geo-coordinates of quick-commerce riders?", "options": ["HSET", "GEOADD", "ZADD", "LPUSH"], "correct": 1},
    {"question": "What is the primary benefit of read-replicas in PostgreSQL?", "options": ["Decrease writing response latency", "Improve database schema normalizations", "Scale read transactions and handle node failure redundancy", "Increase network packet compression"], "correct": 2},
    {"question": "What does the CAP theorem state?", "options": ["A distributed system can guarantee at most two of Consistency, Availability, and Partition Tolerance", "Caching always beats direct database execution in latency", "All databases must support atomic transactions", "Concurrency increases CPU allocation parameters"], "correct": 0},
    {"question": "What is the primary difference between SQL and NoSQL databases?", "options": ["SQL databases only run on Windows; NoSQL runs on Linux", "SQL databases are typically relational/schematized; NoSQL are non-relational/flexible-schema", "NoSQL databases don''t support indexes", "SQL databases cannot scale vertically"], "correct": 1},
    {"question": "In Redis, what does the TTL property of a key represent?", "options": ["Transaction Thread Limit", "Total Transaction Latency", "Time To Live (expiration duration)", "Table Transient Link"], "correct": 2},
    {"question": "Which load balancing algorithm distributes requests sequentially across a list of servers?", "options": ["Least Connections", "Round Robin", "IP Hashing", "Weighted Response Time"], "correct": 1},
    {"question": "What is the purpose of a CDN (Content Delivery Network)?", "options": ["To cache static assets closer to end users to reduce latency", "To manage relational database backups", "To containerize microservices", "To encrypt user password keys"], "correct": 0},
    {"question": "What is consistent hashing primarily used for?", "options": ["Securing web passwords", "Optimizing SQL query index queries", "Minimizing key reorganization in distributed hash tables/caching during node changes", "Calculating similarity scores of candidates"], "correct": 2},
    {"question": "What is a single point of failure (SPOF) in system design?", "options": ["A bug that crashes the browser client", "A component whose failure stops the entire system from working", "A database query that takes > 10 seconds", "An unhandled promise rejection in node"], "correct": 1}
]', '{
    "title": "Redis Simple Rate Limiter",
    "desc": "Implement a rate limiter class in JavaScript that checks if a user has exceeded 5 requests per minute, returns false if rate-limited.",
    "template": "class RateLimiter {\\n    constructor() {\\n        this.requests = new Map();\\n    }\\n    isAllowed(userId) {\\n        const now = Date.now();\\n        return true;\\n    }\\n}"
}'),
(4, '[
    {"question": "In behavioral SDE rounds, what does the ''A'' represent in the STAR template?", "options": ["Assessment", "Allocation", "Action taken", "Algorithmic score"], "correct": 2},
    {"question": "What is the best way to showcase achievements on an SDE resume?", "options": ["Explain lines of code written", "Detail the group''s general code layout", "Quantify personal impact (e.g. ''reduced latency by 30% using Redis'')", "List all keywords in alphabet order"], "correct": 2},
    {"question": "How should code complexity be discussed during a live SDE whiteboard interview?", "options": ["Wait for the interviewer to prompt you", "Calculate time and space bounds step-by-step as you construct the code", "State O(N) immediately for all solutions", "Say complexity doesn''t matter for initial prototypes"], "correct": 1},
    {"question": "What does ''STAR'' stand for in interview methodology?", "options": ["Situation, Task, Action, Result", "Status, Target, Analysis, Recommendation", "System, Technology, Architecture, Reliability", "Structure, Theory, Application, Review"], "correct": 0},
    {"question": "What is the time complexity of binary search on a sorted array of size N?", "options": ["O(N)", "O(log N)", "O(N log N)", "O(1)"], "correct": 1},
    {"question": "In whiteboard interviews, what is the first step before writing any code?", "options": ["Write down the brute force helper nested loops", "Ask the interviewer to give you the code outline", "Clarify requirements, constraints, and inputs/outputs", "Declare variables on the board"], "correct": 2},
    {"question": "What is the space complexity of an in-place QuickSort algorithm in the average case?", "options": ["O(N)", "O(log N)", "O(N^2)", "O(1)"], "correct": 1},
    {"question": "In behavioral SDE interviews, how should conflict with a coworker be described?",
    "options": ["Focus on how the conflict was resolved constructively and what was learned", "Explain why the other developer was wrong", "Avoid mentioning any conflicts at all", "Say conflicts are resolved by the manager"], "correct": 0},
    {"question": "What is the time complexity of inserting a key in a Hash Map (average case)?", "options": ["O(N)", "O(log N)", "O(N log N)", "O(1)"], "correct": 3},
    {"question": "How do you optimize an O(N^2) brute force solution in a coding interview?", "options": ["Use multiple helper functions to split the code lines", "Increase hardware allocation memory size", "Use a hash map/set to trade space for time, or apply sorting/two-pointers", "Replace loops with recursion blocks"], "correct": 2}
]', '{
    "title": "Two Sum Optimal O(N)",
    "desc": "Write a function twoSum(nums, target) returning indices of the two elements adding up to target in linear time complexity.",
    "template": "function twoSum(nums, target) {\\n    const map = new Map();\\n    for (let i = 0; i < nums.length; i++) {\\n        const complement = target - nums[i];\\n        if (map.has(complement)) {\\n            return [map.get(complement), i];\\n        }\\n        map.set(nums[i], i);\\n    }\\n    return [];\\n}"
}');

-- ============================================================
-- 9. SDE PROFILE BUILDER OPTIMIZATION BLUEPRINTS
-- ============================================================

INSERT INTO profile_builder_templates (role_name, resume_bullets, linkedin_summary, github_readme) VALUES
('Software Development Engineer', '[
    "Designed and implemented a high-concurrency order dispatching service using Go, reducing rider allocation latency by 35%.",
    "Integrated Apache Kafka for real-time status updates broadcast, handling peak loads of 15,000 requests/sec with zero message drop.",
    "Structured transactional indexes on PostgreSQL and Redis cache-aside caching, lowering database read latency by 45% during peak hours.",
    "Developed a local rate-limiter service in JavaScript, protecting downstream microservices from spike traffic."
]', 
'SDE Candidate | Aspiring Backend Developer | System Design Enthusiast. Passionate about building high-throughput, low-latency microservices using Go, Java, and Spring Boot. Proficient in relational query optimization, Redis caching patterns, and Apache Kafka message queues.',
'# High-Concurrency Quick-Commerce Geo-Dispatch Engine

A scalable, low-latency backend engine tailored for instant grocery deliveries.

## Tech Stack
- **Languages**: Go / Java (Spring Boot)
- **Database**: PostgreSQL (indexing range queries)
- **Caching**: Redis (Geo-indexing coordinates via GEOADD)
- **Messaging**: Apache Kafka (status broadcast topic)

## Features
- Real-time rider tracking with geo-fencing.
- Cache-aside caching strategy to reduce database load.
- Monotonically ordered delivery updates.

## Getting Started
1. Start Redis and Kafka.
2. Run `go run main.go`.
');
