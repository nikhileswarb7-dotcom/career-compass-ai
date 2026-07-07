# Knowledge Layer - CareerCompass AI
# Provides a clean interface between the database and decision engines,
# packaging relational data into normalized Python knowledge objects.

import logging
from typing import List, Dict, Any, Optional
from api.database_connector import get_db_connection

logger = logging.getLogger("KnowledgeLayer")

class SkillKnowledge:
    def __init__(self, skill_id: int, skill_name: str, category: str, difficulty: str):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.category = category
        self.difficulty = difficulty

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "category": self.category,
            "difficulty": self.difficulty
        }

class RoleKnowledge:
    def __init__(self, role_id: int, role_name: str, description: str, responsibilities: List[str], experience_levels: List[str]):
        self.role_id = role_id
        self.role_name = role_name
        self.description = description
        self.responsibilities = responsibilities
        self.experience_levels = experience_levels

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "experience_levels": self.experience_levels
        }

class HiringPatternKnowledge:
    def __init__(self, company_name: str, role_name: str, cgpa_cutoff: float, backlogs_allowed: bool, salary_range: Dict[str, Any], tech_stack: List[str], hiring_process: List[str]):
        self.company_name = company_name
        self.role_name = role_name
        self.cgpa_cutoff = cgpa_cutoff
        self.backlogs_allowed = backlogs_allowed
        self.salary_range = salary_range
        self.tech_stack = tech_stack
        self.hiring_process = hiring_process

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "role_name": self.role_name,
            "cgpa_cutoff": self.cgpa_cutoff,
            "backlogs_allowed": self.backlogs_allowed,
            "salary_range": self.salary_range,
            "tech_stack": self.tech_stack,
            "hiring_process": self.hiring_process
        }

class KnowledgeLayer:
    """
    Acts as the single source of truth for decision engines to query knowledge models.
    """

    @staticmethod
    def load_all_skills() -> List[SkillKnowledge]:
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("SELECT skill_id, skill_name, category, difficulty FROM skills")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [SkillKnowledge(r[0], r[1], r[2], r[3]) for r in rows]
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error loading skills in KnowledgeLayer: {e}")
            return []

    @staticmethod
    def get_role_knowledge(role_name: str) -> Optional[RoleKnowledge]:
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT role_id, role_name, description, responsibilities, experience_levels
                FROM roles
                WHERE LOWER(role_name) = %s LIMIT 1;
            """, (role_name.lower().strip(),))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                import json
                resp = row[3]
                if isinstance(resp, str):
                    resp = json.loads(resp)
                exp = row[4]
                if isinstance(exp, str):
                    exp = json.loads(exp)
                return RoleKnowledge(row[0], row[1], row[2], resp or [], exp or [])
            return None
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error loading role in KnowledgeLayer: {e}")
            return None

    @staticmethod
    def get_hiring_pattern(company_name: str, role_name: str) -> Optional[HiringPatternKnowledge]:
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            cur.execute("""
                SELECT c.company_name, r.role_name, cr.cgpa_cutoff, cr.backlogs_allowed, c.salary_range, c.tech_stack, c.hiring_process
                FROM company_roles cr
                JOIN companies c ON cr.company_id = c.company_id
                JOIN roles r ON cr.role_id = r.role_id
                WHERE LOWER(c.company_name) = %s AND LOWER(r.role_name) = %s LIMIT 1;
            """, (company_name.lower().strip(), role_name.lower().strip()))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                import json
                salary = row[4]
                if isinstance(salary, str):
                    salary = json.loads(salary)
                stack = row[5]
                if isinstance(stack, str):
                    stack = json.loads(stack)
                process = row[6]
                if isinstance(process, str):
                    process = json.loads(process)
                return HiringPatternKnowledge(
                    company_name=row[0],
                    role_name=row[1],
                    cgpa_cutoff=row[2] or 0.0,
                    backlogs_allowed=bool(row[3]),
                    salary_range=salary or {},
                    tech_stack=stack or [],
                    hiring_process=process or []
                )
            return None
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error loading hiring pattern in KnowledgeLayer: {e}")
            return None

    @staticmethod
    def get_resources_by_skill_ids(skill_ids: List[int]) -> List[Dict[str, Any]]:
        if not skill_ids:
            return []
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT r.resource_id, r.title, r.resource_type, r.topic, rsm.skill_id, r.url, r.platform, r.difficulty, r.duration_hours
                FROM resources r
                JOIN resource_skill_mapping rsm ON r.resource_id = rsm.resource_id
                WHERE rsm.skill_id IN ({placeholders})
            """, tuple(skill_ids))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [{
                "id": r[0],
                "title": r[1],
                "type": r[2],
                "topic": r[3],
                "skill_id": r[4],
                "url": r[5],
                "platform": r[6],
                "difficulty": r[7],
                "duration_hours": r[8] or 4.0
            } for r in rows]
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error loading resources in KnowledgeLayer: {e}")
            return []

    @staticmethod
    def get_projects_by_skill_ids(skill_ids: List[int]) -> List[Dict[str, Any]]:
        if not skill_ids:
            return []
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SET search_path TO career_compass_ai, public;")
            placeholders = ",".join(["%s"] * len(skill_ids))
            cur.execute(f"""
                SELECT DISTINCT p.project_id, p.project_name, p.description, p.difficulty, p.skills_covered
                FROM projects p
                JOIN project_skill_mapping psm ON p.project_id = psm.project_id
                WHERE psm.skill_id IN ({placeholders})
            """, tuple(skill_ids))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            import json
            res = []
            for r in rows:
                skills = r[4]
                if isinstance(skills, str):
                    try: skills = json.loads(skills)
                    except Exception: skills = []
                res.append({
                    "id": r[0],
                    "name": r[1],
                    "details": r[2],
                    "difficulty": r[3],
                    "skills": skills if isinstance(skills, list) else []
                })
            return res
        except Exception as e:
            if conn: conn.close()
            logger.error(f"Error loading projects in KnowledgeLayer: {e}")
            return []
