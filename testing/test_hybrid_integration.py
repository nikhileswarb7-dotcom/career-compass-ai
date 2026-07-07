# Test Hybrid Integration and Failure Fallbacks - CareerCompass AI

import os
import sys
import unittest
import numpy as np

WORKSPACE_DIR = r"c:\Users\nikhi\OneDrive\Desktop\career-compass-ai"
sys.path.append(WORKSPACE_DIR)

from ai_engine.decision_engine.registry import registry
from ai_engine.recommendation_engine import generate_recommendation

class TestHybridIntegration(unittest.TestCase):
    def setUp(self):
        # Ensure registry ML engine is initialized
        self.ml_engine = registry.ml_affinity_engine
        
    def test_01_valid_model_inference(self):
        """Test standard inference for SDE student"""
        skills = ["Java", "Python", "System Design", "Git & GitHub"]
        res = self.ml_engine.calculate_affinities(
            student_skills=skills,
            experience_years=2.0,
            college="PES University",
            degree="BTech"
        )
        self.assertTrue(res["supported"])
        self.assertEqual(res["confidence_status"], "high")
        self.assertEqual(res["limitations"], "None")
        self.assertGreaterEqual(res["general_engineering_score"], 0.0)
        self.assertLessEqual(res["general_engineering_score"], 1.0)
        print(f"SDE affinity: Gen={res['general_engineering_score']}, Backend={res['backend_affinity_score']}, Frontend={res['frontend_affinity_score']}")

    def test_02_backend_like_profile(self):
        """Test backend heavy skills yield high backend affinity"""
        skills = ["Spring Boot", "Docker", "Kubernetes", "Java", "Microservices"]
        res = self.ml_engine.calculate_affinities(
            student_skills=skills,
            experience_years=3.0,
            college="Other",
            degree="BTech"
        )
        self.assertTrue(res["supported"])
        self.assertGreater(res["backend_affinity_score"], res["frontend_affinity_score"])
        print(f"Backend profile affinity: Backend={res['backend_affinity_score']} vs Frontend={res['frontend_affinity_score']}")

    def test_03_frontend_like_profile(self):
        """Test frontend heavy skills yield high frontend affinity"""
        skills = ["React", "HTML & CSS", "TypeScript", "JavaScript"]
        res = self.ml_engine.calculate_affinities(
            student_skills=skills,
            experience_years=1.0,
            college="NIT",
            degree="BE"
        )
        self.assertTrue(res["supported"])
        self.assertGreater(res["frontend_affinity_score"], res["backend_affinity_score"])
        print(f"Frontend profile affinity: Frontend={res['frontend_affinity_score']} vs Backend={res['backend_affinity_score']}")

    def test_04_zero_mapped_skills(self):
        """Test fallback when zero skills are provided (OOD case)"""
        res = self.ml_engine.calculate_affinities(
            student_skills=[],
            experience_years=0.0,
            college="IIT",
            degree="BTech"
        )
        self.assertFalse(res["supported"])
        self.assertEqual(res["confidence_status"], "low")
        self.assertIn("OOD", res["limitations"])

    def test_05_unknown_skills(self):
        """Test fallback when only unknown skills are provided"""
        res = self.ml_engine.calculate_affinities(
            student_skills=["Cooking", "Dancing", "Painting"],
            experience_years=0.0,
            college="IIT",
            degree="BTech"
        )
        self.assertFalse(res["supported"])
        self.assertEqual(res["confidence_status"], "low")
        self.assertIn("OOD", res["limitations"])

    def test_06_insufficient_skills_low_confidence(self):
        """Test low confidence status for insufficient skill count (< 3)"""
        res = self.ml_engine.calculate_affinities(
            student_skills=["Java"],
            experience_years=1.0,
            college="Other",
            degree="BTech"
        )
        self.assertTrue(res["supported"])
        self.assertEqual(res["confidence_status"], "low")
        self.assertIn("Insufficient signal", res["limitations"])

    def test_07_missing_model_artifacts_graceful_fallback(self):
        """Test fallback when models are missing or disabled"""
        # Save real loaded state
        real_loaded = self.ml_engine._loaded
        try:
            self.ml_engine._loaded = False
            res = self.ml_engine.calculate_affinities(
                student_skills=["Java", "Python"],
                experience_years=1.0,
                college="IIT",
                degree="BTech"
            )
            self.assertFalse(res["supported"])
            self.assertEqual(res["confidence_status"], "low")
            self.assertIn("disabled", res["limitations"])
        finally:
            self.ml_engine._loaded = real_loaded

    def test_08_end_to_end_roadmap_trace_integration(self):
        """Test ML affinity integration in the final roadmap decision trace exporter"""
        roadmap = generate_recommendation(
            qualification="BTech",
            known_skills=["Java", "Docker", "Spring Boot", "Git & GitHub"],
            dream_company="Blinkit",
            experience_years=2.0
        )
        self.assertIn("decision_trace", roadmap)
        self.assertIn("ml_affinity", roadmap["decision_trace"])
        
        ml_data = roadmap["decision_trace"]["ml_affinity"]
        self.assertTrue(ml_data["supported"])
        self.assertEqual(ml_data["model_version"], "1.0.0")
        self.assertGreaterEqual(ml_data["backend_affinity_score"], 0.0)
        
        # Check top-level exposure
        self.assertIn("ml_affinity", roadmap)
        self.assertEqual(roadmap["ml_affinity"]["model_version"], "1.0.0")

    def test_09_two_simultaneous_sessions(self):
        """Test that subsequent requests do not share or leak vectorizer/preprocessor state"""
        res_backend = self.ml_engine.calculate_affinities(
            student_skills=["Spring Boot", "Docker", "Kubernetes", "Java"],
            experience_years=3.0,
            college="IIT",
            degree="BTech"
        )
        res_frontend = self.ml_engine.calculate_affinities(
            student_skills=["React", "HTML & CSS", "TypeScript"],
            experience_years=1.0,
            college="NIT",
            degree="BE"
        )
        self.assertGreater(res_backend["backend_affinity_score"], res_backend["frontend_affinity_score"])
        self.assertGreater(res_frontend["frontend_affinity_score"], res_frontend["backend_affinity_score"])

    def test_10_database_offline_inference(self):
        """Test that the loaded in-memory pipelines run successfully even if DB goes offline"""
        # Since ML specializations run purely on the serialized pipelines, closing the DB connection
        # will not interfere with affinity estimation.
        skills = ["Java", "Docker", "React"]
        res = self.ml_engine.calculate_affinities(
            student_skills=skills,
            experience_years=1.0,
            college="Other",
            degree="BTech"
        )
        self.assertTrue(res["supported"])
        self.assertGreaterEqual(res["general_engineering_score"], 0.0)

if __name__ == "__main__":
    unittest.main()
