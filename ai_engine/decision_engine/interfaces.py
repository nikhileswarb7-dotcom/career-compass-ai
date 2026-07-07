# Interfaces for AI Career Decision Engine - CareerCompass AI

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ISimilarityEngine(ABC):
    @abstractmethod
    def find_similar_engineers(
        self, 
        student_skills: List[str], 
        target_company: str, 
        target_role: str, 
        experience_years: float, 
        gpa: float, 
        qualification: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Compares candidate profile variables against database SDE professional profiles.
        """
        pass

class ISkillGapEngine(ABC):
    @abstractmethod
    def analyze_gaps(
        self, 
        known_skills: List[str], 
        target_company: str, 
        target_role: str
    ) -> Dict[str, Any]:
        """
        Analyzes known skills against target role/company expectations, outputting gaps.
        """
        pass

class IReadinessEngine(ABC):
    @abstractmethod
    def evaluate_readiness(
        self, 
        student_skills: List[str], 
        linkedin_url: str, 
        github_username: str, 
        resume_text: str, 
        company_name: str, 
        role_name: str, 
        qualification: str, 
        experience_years: float, 
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Computes granular skill, project, profile, and interview strengths to obtain overall readiness.
        """
        pass

class ICareerTwinEngine(ABC):
    @abstractmethod
    def analyze_career_twins(
        self, 
        similar_engineers: List[Dict[str, Any]], 
        student_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Extracts transitions, benchmarks, and common projects from matched peer profiles.
        """
        pass

class IRoadmapPlanner(ABC):
    @abstractmethod
    def generate_roadmap(
        self, 
        qualification: str, 
        missing_skills: Dict[str, List[str]], 
        dream_company: str, 
        dream_sector: str, 
        fresh_passout: bool, 
        target_role: str, 
        similar_engineers: Optional[List[Dict[str, Any]]] = None, 
        assessment_scores: Optional[Dict[str, Any]] = None, 
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically plots the sequential study stages, durations, coding tasks, and milestones.
        """
        pass

class IInterviewPlanner(ABC):
    @abstractmethod
    def recommend_questions(
        self, 
        missing_skills: Dict[str, List[str]], 
        dream_company: str, 
        dream_sector: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top interview questions matching target company and skill gaps.
        """
        pass

class IResourceRecommender(ABC):
    @abstractmethod
    def recommend_resources(self, skill_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Selects top online video or reading resources for specified skills.
        """
        pass

# ----------------------------------------------------------------
# Future Enhancement Engine Interfaces
# ----------------------------------------------------------------

class ICareerStrategyEngine(ABC):
    @abstractmethod
    def determine_priorities(self, student_profile: Dict[str, Any], readiness_score: float) -> Dict[str, Any]:
        """
        Determines high-level career strategic priorities before roadmap generation.
        """
        pass

class IAdaptiveLearningEngine(ABC):
    @abstractmethod
    def adapt_roadmap(
        self, 
        current_roadmap: Dict[str, Any], 
        assessment_history: List[Dict[str, Any]], 
        student_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dynamically updates roadmap milestones or durations based on candidate outcomes.
        """
        pass

class IDecisionTraceExporter(ABC):
    @abstractmethod
    def build_trace(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Captures the exact evidence paths justifying recommendations for explainability.
        """
        pass

class IMLAffinityEngine(ABC):
    @abstractmethod
    def calculate_affinities(
        self,
        student_skills: List[str],
        experience_years: float,
        college: str,
        degree: str
    ) -> Dict[str, Any]:
        """
        Calculates experimental ML specialization affinity scores.
        """
        pass
