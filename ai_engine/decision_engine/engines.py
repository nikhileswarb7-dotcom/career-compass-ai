# Concrete Decision Engines implementing Career Compass AI Interfaces

import os
import logging
from typing import List, Dict, Any, Optional
from ai_engine.decision_engine.interfaces import (
    ISimilarityEngine, ISkillGapEngine, IReadinessEngine, ICareerTwinEngine,
    IRoadmapPlanner, IInterviewPlanner, IResourceRecommender,
    ICareerStrategyEngine, IAdaptiveLearningEngine, IDecisionTraceExporter,
    IMLAffinityEngine
)
from ai_engine.decision_engine.knowledge_layer import KnowledgeLayer

# Import existing implementations
from ai_engine.similarity.engineer_similarity_engine import EngineerSimilarityEngine
from ai_engine.skill_gap_engine import analyze_gaps
from ai_engine.assessment.readiness_engine import evaluate_career_readiness
from ai_engine.roadmap_generator import generate_timeline
from ai_engine.interview_recommender import recommend_questions

logger = logging.getLogger("DecisionEngines")

class HeuristicSimilarityEngine(ISimilarityEngine):
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
        return EngineerSimilarityEngine.find_similar_engineers(
            student_skills=student_skills,
            target_company=target_company,
            target_role=target_role,
            experience_years=experience_years,
            gpa=gpa,
            qualification=qualification,
            limit=limit
        )

class HeuristicSkillGapEngine(ISkillGapEngine):
    def analyze_gaps(
        self, 
        known_skills: List[str], 
        target_company: str, 
        target_role: str
    ) -> Dict[str, Any]:
        return analyze_gaps(known_skills, target_company, target_role)

class HeuristicReadinessEngine(IReadinessEngine):
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
        return evaluate_career_readiness(
            student_skills=student_skills,
            linkedin_url=linkedin_url,
            github_username=github_username,
            resume_text=resume_text,
            company_name=company_name,
            role_name=role_name,
            qualification=qualification,
            experience_years=experience_years,
            candidate_profile=candidate_profile
        )

class HeuristicCareerTwinEngine(ICareerTwinEngine):
    def analyze_career_twins(
        self, 
        similar_engineers: List[Dict[str, Any]], 
        student_skills: List[str]
    ) -> Dict[str, Any]:
        from ai_engine.similarity.career_path_analyzer import analyze_career_paths
        return analyze_career_paths(similar_engineers, student_skills)

class HeuristicRoadmapPlanner(IRoadmapPlanner):
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
        return generate_timeline(
            qualification=qualification,
            missing_skills=missing_skills,
            dream_company=dream_company,
            dream_sector=dream_sector,
            fresh_passout=fresh_passout,
            target_role=target_role,
            similar_engineers=similar_engineers,
            assessment_scores=assessment_scores,
            candidate_profile=candidate_profile
        )

class HeuristicInterviewPlanner(IInterviewPlanner):
    def recommend_questions(
        self, 
        missing_skills: Dict[str, List[str]], 
        dream_company: str, 
        dream_sector: str
    ) -> List[Dict[str, Any]]:
        return recommend_questions(missing_skills, dream_company, dream_sector)

class HeuristicResourceRecommender(IResourceRecommender):
    def recommend_resources(self, skill_ids: List[int]) -> List[Dict[str, Any]]:
        return KnowledgeLayer.get_resources_by_skill_ids(skill_ids)


# ----------------------------------------------------------------
# Future Extensions Concrete Stubs
# ----------------------------------------------------------------

class HeuristicCareerStrategyEngine(ICareerStrategyEngine):
    def determine_priorities(self, student_profile: Dict[str, Any], readiness_score: float) -> Dict[str, Any]:
        """
        Calculates student prep strategy (e.g. prioritize core DS over frameworks).
        """
        gpa = student_profile.get("gpa", 8.0)
        skills = student_profile.get("skills", [])
        
        priorities = []
        if len(skills) < 3:
            priorities.append("Core Languages & Syntax")
        if gpa < 7.0:
            priorities.append("Academic GPA / Core CS Concepts")
        if not priorities:
            priorities.append("System Design & Scale Projects")
            
        return {
            "strategy": "Systematic Skill Acquisition" if readiness_score < 50 else "Interview Sprint Focus",
            "strategic_priorities": priorities,
            "notes": "Strategically mapped baseline based on academic and profile completeness parameters."
        }

class HeuristicAdaptiveLearningEngine(IAdaptiveLearningEngine):
    def adapt_roadmap(
        self, 
        current_roadmap: Dict[str, Any], 
        assessment_history: List[Dict[str, Any]], 
        student_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modifies timeline stage duration or weekly hour recommendations.
        """
        adapted = dict(current_roadmap)
        if not assessment_history:
            return adapted
            
        avg_score = sum(h.get("score", 0.0) for h in assessment_history) / len(assessment_history)
        if avg_score < 40.0:
            # Slow down stages by 20%
            for stage in adapted.get("stages", []):
                stage["duration_weeks"] = int(stage["duration_weeks"] * 1.2)
                
        return adapted

class HeuristicDecisionTraceExporter(IDecisionTraceExporter):
    def build_trace(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the decision trace containing the factual database evidence.
        """
        target_company = inputs.get("dream_company", "Blinkit")
        target_role = inputs.get("target_role", "SDE")
        readiness_score = outputs.get("readiness_score", 0)
        similar_engineers = outputs.get("similar_engineers", [])
        
        peer_count = len(similar_engineers)
        peer_transitions = [e.get("career_path_str") for e in similar_engineers if e.get("career_path_str")]
        
        timeline = outputs.get("timeline", {})
        validation_trace = timeline.pop("_validation_evidence", []) if isinstance(timeline, dict) else []
        
        # Pull ML affinity if present in outputs
        ml_trace = outputs.get("ml_affinity")
        
        trace = {
            "target_alignment": f"Targeting {target_company} {target_role} SDE preparation path.",
            "readiness_justification": f"Overall SDE readiness calculated at {readiness_score}% using 40% skills, 25% projects, 20% interview, and 15% profile benchmarks.",
            "evidence_peers": f"Identified {peer_count} similar peers targetting/working at {target_company} SDE roles.",
            "evidence_patterns": peer_transitions[:3],
            "roadmap_consistency_validation_trace": validation_trace
        }
        if ml_trace:
            trace["ml_affinity"] = ml_trace
            
        return trace

class MLSpecializationAffinityEngine(IMLAffinityEngine):
    def __init__(self):
        self._loaded = False
        self._general_pipeline = None
        self._backend_pipeline = None
        self._frontend_pipeline = None
        self._feature_builder = None
        self._load_pipelines()

    def _load_pipelines(self):
        try:
            import joblib
            from ai_engine.similarity.feature_builder import ProfessionalFeatureBuilder
            
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            similarity_dir = os.path.join(base_dir, "ai_engine", "similarity")
            
            general_path = os.path.join(similarity_dir, "general_affinity_pipeline.joblib")
            backend_path = os.path.join(similarity_dir, "backend_affinity_pipeline.joblib")
            frontend_path = os.path.join(similarity_dir, "frontend_affinity_pipeline.joblib")
            
            if os.path.exists(general_path) and os.path.exists(backend_path) and os.path.exists(frontend_path):
                self._general_pipeline = joblib.load(general_path)
                self._backend_pipeline = joblib.load(backend_path)
                self._frontend_pipeline = joblib.load(frontend_path)
                self._feature_builder = ProfessionalFeatureBuilder()
                self._loaded = True
            else:
                logger.warning("One or more model pipeline artifacts are missing. ML engine disabled.")
        except Exception as e:
            logger.error(f"Error loading ML pipelines: {e}")

    def calculate_affinities(
        self,
        student_skills: List[str],
        experience_years: float,
        college: str,
        degree: str
    ) -> Dict[str, Any]:
        result = {
            "general_engineering_score": 0.0,
            "backend_affinity_score": 0.0,
            "frontend_affinity_score": 0.0,
            "model_version": "1.0.0",
            "dataset_version": "1.0.0",
            "ontology_version": "1.1.0",
            "supported": False,
            "confidence_status": "low",
            "limitations": "Model pipeline not loaded or error during inference."
        }
        
        if not self._loaded:
            result["limitations"] = "Inference disabled: Pipeline models failed to load."
            return result
            
        try:
            # 1. Validation & OOD / Confidence check
            if not student_skills or len(student_skills) == 0:
                result["limitations"] = "OOD: Zero mapped skills provided."
                return result
                
            normalized_user_skills = {self._feature_builder.normalize_skill_name(s) for s in student_skills}
            ontology_normalized = {self._feature_builder.normalize_skill_name(s) for s in self._feature_builder.skill_names}
            
            overlap = normalized_user_skills.intersection(ontology_normalized)
            if not overlap:
                result["limitations"] = "OOD: Profile has zero overlap with the 53 master ontology skills."
                return result
                
            X_inference = self._feature_builder.build_features(
                skills=student_skills,
                experience_years=experience_years,
                college=college,
                degree=degree
            )
            
            gen_prob = self._general_pipeline.predict_proba(X_inference)[0, 1]
            back_prob = self._backend_pipeline.predict_proba(X_inference)[0, 1]
            front_prob = self._frontend_pipeline.predict_proba(X_inference)[0, 1]
            
            result["general_engineering_score"] = float(round(gen_prob, 4))
            result["backend_affinity_score"] = float(round(back_prob, 4))
            result["frontend_affinity_score"] = float(round(front_prob, 4))
            result["supported"] = True
            
            if len(student_skills) < 3:
                result["confidence_status"] = "low"
                result["limitations"] = "Insufficient signal: Less than 3 student skills."
            elif len(overlap) / len(student_skills) < 0.2:
                result["confidence_status"] = "low"
                result["limitations"] = "Low confidence: Less than 20% of student's skills are in master ontology."
            else:
                result["confidence_status"] = "high"
                result["limitations"] = "None"
                
            return result
            
        except Exception as e:
            logger.error(f"Error during ML Specialization Affinity inference: {e}")
            result["limitations"] = f"Inference failure: {e}"
            return result

# ----------------------------------------------------------------
# Initialize and inject concrete implementations into registry
# ----------------------------------------------------------------
from ai_engine.decision_engine.registry import registry

registry.similarity_engine = HeuristicSimilarityEngine()
registry.skill_gap_engine = HeuristicSkillGapEngine()
registry.readiness_engine = HeuristicReadinessEngine()
registry.career_twin_engine = HeuristicCareerTwinEngine()
registry.roadmap_planner = HeuristicRoadmapPlanner()
registry.interview_planner = HeuristicInterviewPlanner()
registry.resource_recommender = HeuristicResourceRecommender()
registry.career_strategy_engine = HeuristicCareerStrategyEngine()
registry.adaptive_learning_engine = HeuristicAdaptiveLearningEngine()
registry.decision_trace_exporter = HeuristicDecisionTraceExporter()
registry.ml_affinity_engine = MLSpecializationAffinityEngine()
