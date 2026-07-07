# NLP Classifier and Vector Similarity Matcher - CareerCompass AI
# Implements Cosine Similarity on Bag of Words (Term Frequency vectors) for intent parsing.
# Additionally integrates Google Gemini Generative AI as the primary chat coach when an API key is provided.

import re
import math
import os

# Try importing google.generativeai
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

# Standard English stop words to filter out noise from search queries
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "did", "do", 
    "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", 
    "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", 
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", 
    "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", 
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", 
    "you", "your", "yours", "yourself", "yourselves", "tell", "suggest", "good", "please", "ask", "like", 
    "want", "know", "give", "show", "get", "need", "find", "some", "questions", "topics", "concepts"
}

# Knowledge base templates for the Coach Chatbot (Fallback Engine)
KNOWLEDGE_BASE = [
    {
        "intent": "greetings",
        "keywords": ["hello", "hi", "hey", "greetings", "good morning", "yo"],
        "reply": "Hey there! Ready to level up your SDE preparation? As your Placement Coach, I'm here to guide you. What specific topics or coding challenges are on your mind regarding {dream_company}?"
    },
    {
        "intent": "dsa",
        "keywords": ["dsa", "data structures", "algorithms", "leetcode", "arrays", "trees", "graphs", "sorting", "searching", "dynamic programming", "recursion", "pointers", "stack", "queue"],
        "reply": "To crack DSA interviews, prioritize Arrays, Strings, Trees, and Dynamic Programming. Focus on solving 2-3 target problems daily. Use Striver's A2Z DSA sheet as detailed in your dashboard resources. Remember to analyze time and space complexity for every solution!"
    },
    {
        "intent": "system_design",
        "keywords": ["system design", "hld", "lld", "architecture", "load balancers", "scaling", "microservices", "replication", "sharding", "scalability", "distributed systems"],
        "reply": "System Design is critical for SDE positions at {dream_company}. Focus on: Load Balancers, Caching (Redis), Message Queues (Kafka), and Database Partitioning. A great starting blueprint is Donne Martin's System Design Primer listed in your dashboard resources!"
    },
    {
        "intent": "caching",
        "keywords": ["redis", "cache", "caching", "lru", "eviction", "memcached", "write-through", "cache-aside", "latency"],
        "reply": "Redis is essential for low-latency systems. Master: 1) Redis data types (hashes, sorted sets), 2) Cache eviction policies (LRU, LFU), and 3) Cache patterns like write-through or cache-aside."
    },
    {
        "intent": "queues",
        "keywords": ["kafka", "queue", "message queue", "pubsub", "streaming", "consumer", "producer", "partition", "broker", "event-driven"],
        "reply": "Kafka is excellent for real-time data streaming. Focus on understanding partitions, producer-consumer offsets, consumer groups, and guaranteeing message ordering within partitions."
    },
    {
        "intent": "databases",
        "keywords": ["database", "sql", "postgresql", "mysql", "dbms", "index", "indexing", "acid", "join", "query", "normalization", "nosql"],
        "reply": "Databases form the backbone of SDE work. Review index structures (B-Tree vs. Hash Index), transactional ACID properties, normalizations (1NF to 3NF), and query profiling/tuning (using EXPLAIN ANALYZE)."
    },
    {
        "intent": "resume",
        "keywords": ["resume", "project", "portfolio", "cv", "experience", "showcase", "github", "projects"],
        "reply": "Your resume needs to stand out. Highlight the active Project Blueprint from your sidebar. Describe it quantitatively: 'Implemented a scalable order dispatching system using Go, Redis Geo-indexing, and Kafka, reducing rider dispatch latency by 35%.'"
    },
    {
        "intent": "interview",
        "keywords": ["interview", "process", "rounds", "hiring", "placement", "job", "career", "rounds", "stages"],
        "reply": "The SDE interview process at {dream_company} typically includes: 1) Online Coding Assessment (2 DSA problems), 2) Technical Round 1 (DSA + LLD), 3) Technical Round 2 (System Design + DB schema design), and 4) Behavioral/Managerial round."
    }
]

def clean_and_tokenize(text):
    """
    NLP Tokenization: Cleans text, removes punctuation, downcases, filters stop words, and splits.
    """
    if not text:
        return []
    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
    tokens = [w for w in cleaned.split() if w and w not in STOP_WORDS]
    return tokens

def get_tf_vector(tokens):
    """
    Builds a Term Frequency (bag of words) dictionary.
    """
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    return tf

def cosine_similarity(vec1, vec2):
    """
    Calculates the cosine similarity between two term frequency vectors.
    """
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator

def load_env_keys():
    """
    Dynamically loads the .env file if it exists, updating os.environ.
    This ensures API key changes are picked up in real-time without server restarts.
    """
    dotenv_path = None
    for level in [".", "..", "../..", "../../.."]:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), level, ".env"))
        if os.path.exists(path):
            dotenv_path = path
            break
            
    if dotenv_path and os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except Exception as e:
            print(f"Error dynamically loading .env: {e}")

def classify_and_respond(user_message, dream_company="Blinkit", active_stage="active stage", student_context=None):
    """
    First tries to generate response using Google Gemini Large Language Model (LLM).
    If API key is missing or calls fail, gracefully falls back to the VSM Cosine Similarity matcher.
    """
    load_env_keys()
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Format a highly contextual instruction if student profile is available
    context_str = ""
    name_str = "Candidate"
    gaps_str = "None"
    role_str = "SDE"
    
    if student_context:
        name_str = student_context.get("name", "Candidate")
        role_str = student_context.get("target_role", "Software Development Engineer (SDE)")
        branch = student_context.get("branch", "")
        cgpa = student_context.get("cgpa", "")
        gaps = student_context.get("missing_skills", [])
        gaps_str = ", ".join(gaps) if gaps else "None"
        context_str = (
            f"Candidate Profile:\n"
            f"- Name: {name_str}\n"
            f"- Target SDE Role: {role_str}\n"
            f"- Branch/CGPA: {branch} (CGPA: {cgpa})\n"
            f"- Critical Missing Skills (Gaps): {gaps_str}\n"
        )

    if HAS_GEMINI_SDK and api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            system_instruction = (
                "You are an SDE Placement Coach and AI Assistant for CareerCompass AI.\n"
                "Your goal is to guide freshers and student candidates to prepare for software engineering interviews.\n"
                "You must tailor your advice to their target company, dream sector, and active preparation stage.\n"
                "Always refer to the candidate by their name if provided in context, address their branch/CGPA if relevant, "
                "and directly coach them on closing their specific missing skills (gaps).\n"
                "Be brief, encouraging, professional, and focus on practical engineering steps. Limit response to 3-4 sentences."
            )
            
            prompt = (
                f"{system_instruction}\n\n"
                f"{context_str}"
                f"Candidate Targets:\n"
                f"- Target Company: {dream_company}\n"
                f"- Active Stage: {active_stage}\n\n"
                f"User Message: {user_message}\n"
                f"Coach Response:"
            )
            
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini API invocation failed: {e}. Falling back to local NLP matching.")

    # Fallback: Cosine Similarity Matching
    user_tokens = clean_and_tokenize(user_message)
    if not user_tokens:
        user_tokens = [w for w in re.sub(r'[^\w\s]', ' ', user_message.lower()).split() if w]
        
    if not user_tokens:
        return f"Hi {name_str}! Please ask me any questions about your {role_str} roadmap stages or {dream_company} prep!"

    user_vector = get_tf_vector(user_tokens)
    
    best_intent = None
    best_score = 0.0
    
    for item in KNOWLEDGE_BASE:
        flat_keywords = []
        for kw in item["keywords"]:
            flat_keywords.extend(clean_and_tokenize(kw))
            
        intent_vector = get_tf_vector(flat_keywords)
        score = cosine_similarity(user_vector, intent_vector)
        
        if score > best_score:
            best_score = score
            best_intent = item
            
    if best_intent and best_score >= 0.12:
        reply_template = best_intent["reply"]
        reply_str = reply_template.format(dream_company=dream_company, active_stage=active_stage)
        if name_str != "Candidate":
            reply_str = f"Hi {name_str}, " + reply_str[0].lower() + reply_str[1:]
        if gaps_str != "None":
            reply_str += f" Focus on closing gaps in: {gaps_str}."
        return reply_str
        
    fallback_reply = f"Hi {name_str}, that's a vital question. For your active stage ({active_stage}), make sure to implement hands-on code rather than just reading. Try building microservices matching the SDE stack at {dream_company}."
    if gaps_str != "None":
        fallback_reply += f" Pay special attention to your gaps: {gaps_str}."
    return fallback_reply

