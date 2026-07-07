# Interview Question Recommender - CareerCompass AI
# Loads interview questions directly from PostgreSQL database

import os
import sys
import logging
from api.database_connector import get_db_connection

logger = logging.getLogger("InterviewRecommender")

def load_all_questions():
    """
    Loads all interview questions directly from PostgreSQL.
    """
    questions = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT q.question_id, q.category, q.difficulty, q.question, q.answer, q.explanation, q.tags, q.frequency
                FROM interview_questions q;
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            import json
            for r in rows:
                tags = r[6]
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except Exception:
                        tags = [t.strip() for t in tags.split(",") if t.strip()]
                elif not isinstance(tags, list):
                    tags = []
                    
                questions.append({
                    "id": r[0],
                    "category": r[1],
                    "difficulty": r[2],
                    "question": r[3],
                    "tags": tags,
                    "solution": r[4],
                    "explanation": r[5],
                    "frequency": r[7]
                })
            return questions
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error loading questions from DB: {e}")
            
    # Raise exception if database is completely offline
    raise RuntimeError("PostgreSQL database unavailable to load SDE interview questions!")

def recommend_questions(missing_skills: dict, dream_company: str, dream_sector: str) -> list:
    """
    Selects actual interview questions matching the target company and targets
    any specific skill gaps identified in missing_skills.
    """
    flat_missing = []
    for priority, skills in missing_skills.items():
        flat_missing += [s.lower().strip() for s in skills]

    questions_pool = load_all_questions()
    matched_questions = []

    # Score each question based on target company and skill gap matches
    for q in questions_pool:
        score = 0
        q_text_low = q["question"].lower()
        company_clean = dream_company.lower().strip()
        
        # Check company name match in question text or tags
        if company_clean in q_text_low or any(company_clean in tag.lower() for tag in q.get("tags", [])):
            score += 5
            
        # Check gap skills match in tags
        for tag in q.get("tags", []):
            if tag.lower().strip() in flat_missing:
                score += 3
                
        if score > 0:
            matched_questions.append((score, q))

    # Sort by score descending
    matched_questions.sort(key=lambda x: x[0], reverse=True)
    sorted_matched = [q for score, q in matched_questions]

    # If we don't have enough matched questions, append others from the pool
    for q in questions_pool:
        if q not in sorted_matched:
            sorted_matched.append(q)

    # Return at most 8 questions
    return sorted_matched[:8]
