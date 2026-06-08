# Engineer Similarity Engine - CareerCompass AI

import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai_engine.similarity.engineer_similarity_engine import EngineerSimilarityEngine as RealEngine

class EngineerSimilarityEngine:
    """
    Wrapper class for calculating peer similarity.
    Delegates to the active similarity engine using vector search/cosine similarity.
    """

    @staticmethod
    def find_similar_engineers(student_skills: list, target_role: str, limit: int = 5) -> list:
        """
        Delegates similarity search to the active DB-based similarity engine.
        """
        return RealEngine.find_similar_engineers(
            student_skills=student_skills,
            target_company="Blinkit",
            target_role=target_role,
            limit=limit
        )
