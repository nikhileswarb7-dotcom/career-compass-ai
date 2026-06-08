-- ============================================================
-- CareerCompass AI — Database Views
-- ============================================================

CREATE SCHEMA IF NOT EXISTS career_compass_ai;
SET search_path TO career_compass_ai, public;

-- View: Skills frequency list dynamically computed
CREATE OR REPLACE VIEW v_skills_frequency AS
SELECT 
    sm.skill_id,
    sm.skill_name,
    COUNT(es.profile_id) AS frequency
FROM skills_master sm
LEFT JOIN employee_skills es ON sm.skill_id = es.skill_id
GROUP BY sm.skill_id, sm.skill_name
ORDER BY frequency DESC;

-- View: Details of transition flows between companies
CREATE OR REPLACE VIEW v_career_transitions AS
SELECT 
    ct.transition_id,
    p.name AS employee_name,
    p.college,
    c_src.company_name AS source_company,
    c_tgt.company_name AS target_company
FROM career_transitions ct
JOIN employee_profiles p ON ct.profile_id = p.profile_id
JOIN companies c_src ON ct.source_company_id = c_src.company_id
JOIN companies c_tgt ON ct.target_company_id = c_tgt.company_id;

-- View: Top university SDE sources
CREATE OR REPLACE VIEW v_top_hiring_colleges AS
SELECT 
    college,
    COUNT(*) AS SDE_count,
    ROUND(AVG(experience_years)::numeric, 1) AS avg_experience
FROM employee_profiles
WHERE college IS NOT NULL AND college != ''
GROUP BY college
ORDER BY SDE_count DESC;
