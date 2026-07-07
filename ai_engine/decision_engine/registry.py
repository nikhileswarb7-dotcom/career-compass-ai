# Registry for Career Compass AI Decision Engines

from ai_engine.decision_engine.interfaces import (
    ISimilarityEngine, ISkillGapEngine, IReadinessEngine, ICareerTwinEngine,
    IRoadmapPlanner, IInterviewPlanner, IResourceRecommender,
    ICareerStrategyEngine, IAdaptiveLearningEngine, IDecisionTraceExporter,
    IMLAffinityEngine
)

class DecisionEngineRegistry:
    """
    Registry pattern for decision engine dependency injection and hot-swapping.
    Contains singletons of similarity, gap, readiness, career twins, planner,
    and recommender engines.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DecisionEngineRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._similarity_engine: ISimilarityEngine = None
        self._skill_gap_engine: ISkillGapEngine = None
        self._readiness_engine: IReadinessEngine = None
        self._career_twin_engine: ICareerTwinEngine = None
        self._roadmap_planner: IRoadmapPlanner = None
        self._interview_planner: IInterviewPlanner = None
        self._resource_recommender: IResourceRecommender = None
        self._career_strategy_engine: ICareerStrategyEngine = None
        self._adaptive_learning_engine: IAdaptiveLearningEngine = None
        self._decision_trace_exporter: IDecisionTraceExporter = None
        self._ml_affinity_engine: IMLAffinityEngine = None

    # Getters and setters for engine instances
    @property
    def similarity_engine(self) -> ISimilarityEngine:
        return self._similarity_engine

    @similarity_engine.setter
    def similarity_engine(self, engine: ISimilarityEngine):
        self._similarity_engine = engine

    @property
    def skill_gap_engine(self) -> ISkillGapEngine:
        return self._skill_gap_engine

    @skill_gap_engine.setter
    def skill_gap_engine(self, engine: ISkillGapEngine):
        self._skill_gap_engine = engine

    @property
    def readiness_engine(self) -> IReadinessEngine:
        return self._readiness_engine

    @readiness_engine.setter
    def readiness_engine(self, engine: IReadinessEngine):
        self._readiness_engine = engine

    @property
    def career_twin_engine(self) -> ICareerTwinEngine:
        return self._career_twin_engine

    @career_twin_engine.setter
    def career_twin_engine(self, engine: ICareerTwinEngine):
        self._career_twin_engine = engine

    @property
    def roadmap_planner(self) -> IRoadmapPlanner:
        return self._roadmap_planner

    @roadmap_planner.setter
    def roadmap_planner(self, planner: IRoadmapPlanner):
        self._roadmap_planner = planner

    @property
    def interview_planner(self) -> IInterviewPlanner:
        return self._interview_planner

    @interview_planner.setter
    def interview_planner(self, planner: IInterviewPlanner):
        self._interview_planner = planner

    @property
    def resource_recommender(self) -> IResourceRecommender:
        return self._resource_recommender

    @resource_recommender.setter
    def resource_recommender(self, recommender: IResourceRecommender):
        self._resource_recommender = recommender

    @property
    def career_strategy_engine(self) -> ICareerStrategyEngine:
        return self._career_strategy_engine

    @career_strategy_engine.setter
    def career_strategy_engine(self, engine: ICareerStrategyEngine):
        self._career_strategy_engine = engine

    @property
    def adaptive_learning_engine(self) -> IAdaptiveLearningEngine:
        return self._adaptive_learning_engine

    @adaptive_learning_engine.setter
    def adaptive_learning_engine(self, engine: IAdaptiveLearningEngine):
        self._adaptive_learning_engine = engine

    @property
    def decision_trace_exporter(self) -> IDecisionTraceExporter:
        return self._decision_trace_exporter

    @decision_trace_exporter.setter
    def decision_trace_exporter(self, exporter: IDecisionTraceExporter):
        self._decision_trace_exporter = exporter

    @property
    def ml_affinity_engine(self) -> IMLAffinityEngine:
        return self._ml_affinity_engine

    @ml_affinity_engine.setter
    def ml_affinity_engine(self, engine: IMLAffinityEngine):
        self._ml_affinity_engine = engine

# Global registry instance
registry = DecisionEngineRegistry()
