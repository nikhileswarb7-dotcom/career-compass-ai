# Candidate Builder - CareerCompass AI
# Single Source of Truth Profile Generator

import re
import psycopg2
from profile_analyzer.skill_extractor import SkillExtractor
from profile_analyzer.resume_parser import ResumeParser

class CandidateBuilder:
    """
    Consolidates data from Resume Parser, GitHub Analyzer, LinkedIn Analyzer,
    and Manual selections into a single, normalized candidate profile structure.
    """

    @staticmethod
    def get_all_db_skills() -> list:
        try:
            return ResumeParser.get_all_db_skills()
        except Exception:
            return []

    @classmethod
    def build_profile(cls, manual_skills: list, parsed_res: dict, parsed_gh: dict, parsed_li: dict) -> dict:
        """
        Merges all candidate data inputs and builds a normalized profile.
        """
        skill_metadata = {} # skill_name -> {"sources": set(), "github_frequency": 0}

        # 1. Manual Skills
        for s in manual_skills:
            if s:
                s_name = s.strip()
                if s_name not in skill_metadata:
                    skill_metadata[s_name] = {"sources": set(), "github_frequency": 0}
                skill_metadata[s_name]["sources"].add("Manual")

        # 2. LinkedIn Skills
        if parsed_li and "error" not in parsed_li:
            for s in parsed_li.get("skills_raw", []):
                if s:
                    s_name = s.strip()
                    if s_name not in skill_metadata:
                        skill_metadata[s_name] = {"sources": set(), "github_frequency": 0}
                    skill_metadata[s_name]["sources"].add("LinkedIn")

        # 3. GitHub Skills
        if parsed_gh and "error" not in parsed_gh:
            freq_map = parsed_gh.get("frequency_map", {})
            for s in parsed_gh.get("skills_raw", []):
                if s:
                    s_name = s.strip()
                    if s_name not in skill_metadata:
                        skill_metadata[s_name] = {"sources": set(), "github_frequency": 0}
                    skill_metadata[s_name]["sources"].add("GitHub")
                    skill_metadata[s_name]["github_frequency"] = max(skill_metadata[s_name]["github_frequency"], freq_map.get(s_name, 0))

        # 4. Resume Skills
        if parsed_res and "error" not in parsed_res:
            for s in parsed_res.get("skills_raw", []):
                if s:
                    s_name = s.strip()
                    if s_name not in skill_metadata:
                        skill_metadata[s_name] = {"sources": set(), "github_frequency": 0}
                    skill_metadata[s_name]["sources"].add("Resume")

        # Normalize and filter skills against database master list
        db_skills = cls.get_all_db_skills()
        normalized_skill_metadata = {}

        for skill_name, meta in skill_metadata.items():
            canonical_name = None
            for db_s in db_skills:
                if db_s.lower() == skill_name.lower():
                    canonical_name = db_s
                    break
            if not canonical_name:
                # Fallback mapping from SkillExtractor if available
                canon_res = SkillExtractor.extract_and_normalize([skill_name])
                if canon_res:
                    canonical_name = canon_res[0]
                else:
                    canonical_name = skill_name.strip().title()

            if canonical_name not in normalized_skill_metadata:
                normalized_skill_metadata[canonical_name] = {"sources": set(), "github_frequency": 0}
            normalized_skill_metadata[canonical_name]["sources"].update(meta["sources"])
            normalized_skill_metadata[canonical_name]["github_frequency"] = max(
                normalized_skill_metadata[canonical_name]["github_frequency"], 
                meta["github_frequency"]
            )

        # Calculate confidence score, confidence rating, and profile vector
        candidate_profile_vector = {}
        candidate_skill_confidence = {}

        for s_name, meta in normalized_skill_metadata.items():
            sources = sorted(list(meta["sources"]))
            freq = meta["github_frequency"]

            scores = []
            if "Manual" in sources:
                scores.append(0.85)
            if "Resume" in sources:
                scores.append(0.70)
            if "GitHub" in sources:
                scores.append(0.60)
            if "LinkedIn" in sources:
                scores.append(0.70)

            base_score = max(scores) if scores else 0.50

            # Boosts
            source_count = len(sources)
            if source_count == 2:
                base_score += 0.10
            elif source_count >= 3:
                base_score += 0.15

            if "GitHub" in sources and freq > 0:
                base_score += min(0.20, freq * 0.05)

            confidence_score = min(1.0, base_score)
            
            if confidence_score >= 0.80:
                confidence = "High"
            elif confidence_score >= 0.65:
                confidence = "Medium"
            else:
                confidence = "Low"

            candidate_profile_vector[s_name] = round(confidence_score, 3)
            candidate_skill_confidence[s_name] = {
                "confidence": confidence,
                "confidence_score": round(confidence_score * 100),
                "sources": sources,
                "github_frequency": freq
            }

        # Consolidate candidate projects
        candidate_projects = []
        # A. GitHub Repos
        if parsed_gh and "pinned_projects" in parsed_gh:
            for repo in parsed_gh["pinned_projects"]:
                candidate_projects.append({
                    "title": repo.get("name"),
                    "technologies": repo.get("extracted_skills", []),
                    "description": repo.get("description") or "",
                    "source": "GitHub"
                })
        # B. Resume Projects
        if parsed_res and "projects" in parsed_res:
            for proj in parsed_res.get("projects", []):
                candidate_projects.append({
                    "title": proj.get("title"),
                    "technologies": proj.get("technologies", []),
                    "description": proj.get("description") or "",
                    "source": "Resume"
                })

        # C. LinkedIn Projects (if any)
        if parsed_li and "experience" in parsed_li:
            for exp in parsed_li.get("experience", []):
                desc = exp.get("description") or ""
                # Infer technical competencies/skills for this experience
                exp_skills = []
                for s in db_skills:
                    if re.search(r'\b' + re.escape(s.lower()) + r'\b', desc.lower()):
                        exp_skills.append(s)
                if exp_skills:
                    candidate_projects.append({
                        "title": f"Experience: {exp.get('role')} at {exp.get('company')}",
                        "technologies": exp_skills,
                        "description": desc,
                        "source": "LinkedIn"
                    })

        # Compile candidate metadata
        certifications = parsed_res.get("certifications", [])
        if not certifications and parsed_res.get("certifications_extracted"):
            certifications = [parsed_res.get("certifications_extracted")]

        candidate_metadata = {
            "name": parsed_res.get("name") or parsed_li.get("name") or "SDE Candidate",
            "education": parsed_res.get("education") or parsed_li.get("education") or "B.Tech Computer Science",
            "cgpa": parsed_res.get("cgpa") or 8.0,
            "experience": parsed_res.get("experience") or parsed_li.get("experience") or [],
            "certifications": certifications,
            "linkedin_source": parsed_li.get("source", "N/A"),
            "github_source": parsed_gh.get("source", "N/A"),
            "resume_source": parsed_res.get("source", "N/A"),
            "github_details": {
                "public_repos": parsed_gh.get("public_repos", 0),
                "pinned_projects": parsed_gh.get("pinned_projects", []),
                "skills_raw": parsed_gh.get("skills_raw", []),
                "frequency_map": parsed_gh.get("frequency_map", {})
            } if parsed_gh and "error" not in parsed_gh else None
        }

        return {
            "candidate_profile_vector": candidate_profile_vector,
            "candidate_projects": candidate_projects,
            "candidate_skill_confidence": candidate_skill_confidence,
            "candidate_metadata": candidate_metadata
        }
