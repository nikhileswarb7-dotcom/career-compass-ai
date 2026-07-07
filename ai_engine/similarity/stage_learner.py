# SDE Stage Sequence Learner - CareerCompass AI
# Dynamically trains on PostgreSQL employee profiles data with train-test split

import os
import sys
import logging

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.database_connector import get_db_connection

logger = logging.getLogger("StageLearner")

class StageLearner:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StageLearner, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._learned_skills_tier = {}
        self._test_accuracy = 0.0
        self._initialized = True
        self.train_model()

    def get_tier_from_exp(self, exp: float) -> int:
        if exp < 1.0:
            return 1 # Foundational / Early Explorer
        elif exp < 2.5:
            return 2 # Core Developer / Intermediate
        elif exp < 4.0:
            return 3 # Advanced / Pre-Placement
        elif exp < 5.5:
            return 4 # Placement Ready / Bootloader
        else:
            return 5 # Transitioning Professional

    def train_model(self):
        """
        Loads real SDE employee profiles from PostgreSQL database,
        splits them into 80% train and 20% test datasets,
        learns the optimal skill progression tiers, and evaluates accuracy on the test set.
        """
        conn = get_db_connection()
        if not conn:
            logger.error("Database connection unavailable. Cannot train StageLearner model!")
            return
        
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            
            # Query profiles and experience
            cur.execute("""
                SELECT p.profile_id, p.experience_years, s.skill_name
                FROM employee_profiles p
                JOIN employee_skills es ON p.profile_id = es.profile_id
                JOIN skills s ON es.skill_id = s.skill_id
                ORDER BY p.profile_id ASC;
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            if not rows:
                logger.warning("No SDE employee profiles found in PostgreSQL to train model.")
                return

            # Group skills by profile
            profiles_dict = {}
            for p_id, exp, skill_name in rows:
                if p_id not in profiles_dict:
                    profiles_dict[p_id] = {
                        "experience_years": float(exp or 0.0),
                        "skills": []
                    }
                profiles_dict[p_id]["skills"].append(skill_name.lower().strip())

            # Deterministic Train-Test Split (80/20)
            sorted_profile_ids = sorted(profiles_dict.keys())
            train_profiles = {}
            test_profiles = {}
            
            for idx, p_id in enumerate(sorted_profile_ids):
                # 80% train (idx % 5 != 0), 20% test (idx % 5 == 0)
                if idx % 5 == 0:
                    test_profiles[p_id] = profiles_dict[p_id]
                else:
                    train_profiles[p_id] = profiles_dict[p_id]

            # --- TRAINING PHASE ---
            skill_sums = {}
            skill_counts = {}
            
            for p_id, profile in train_profiles.items():
                tier = self.get_tier_from_exp(profile["experience_years"])
                for skill in profile["skills"]:
                    skill_sums[skill] = skill_sums.get(skill, 0) + tier
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1

            # Compute learned tier for each skill
            self._learned_skills_tier = {}
            for skill, count in skill_counts.items():
                self._learned_skills_tier[skill] = round(skill_sums[skill] / count, 2)

            # --- TESTING & EVALUATION PHASE ---
            # Accuracy is defined as how well the skills possessed by the test profile match their actual tier.
            # Specifically, checking what percentage of a test profile's skills fall within a close range (+/- 1.5) of their actual tier.
            test_scores = []
            for p_id, profile in test_profiles.items():
                actual_tier = self.get_tier_from_exp(profile["experience_years"])
                matches = 0
                total_skills = len(profile["skills"])
                if total_skills == 0:
                    continue
                
                for skill in profile["skills"]:
                    learned_tier = self._learned_skills_tier.get(skill, 3.0) # default to mid-tier 3
                    if abs(learned_tier - actual_tier) <= 1.5:
                        matches += 1
                test_scores.append(matches / total_skills)

            if test_scores:
                self._test_accuracy = round(sum(test_scores) / len(test_scores) * 100.0, 2)
            else:
                self._test_accuracy = 100.0

            logger.info(f"StageLearner trained successfully on real data: "
                        f"Train size: {len(train_profiles)} profiles, Test size: {len(test_profiles)} profiles. "
                        f"Test Evaluation Accuracy: {self._test_accuracy}%.")
            print(f"[*] StageLearner trained successfully: {len(train_profiles)} train, {len(test_profiles)} test. Accuracy: {self._test_accuracy}%.")

        except Exception as e:
            if conn:
                conn.close()
            logger.error(f"Error training StageLearner model: {e}")

    def get_skill_stage_index(self, skill_name: str) -> float:
        """
        Returns the learned stage index (1.0 to 5.0) of the skill.
        Defaults to 3.0 (Advanced / Pre-Placement) if the skill was not observed during training.
        """
        if not self._learned_skills_tier:
            # Lazy initialize or return default if DB is not available
            return 3.0
        return self._learned_skills_tier.get(skill_name.lower().strip(), 3.0)

    @property
    def test_accuracy(self) -> float:
        return self._test_accuracy
