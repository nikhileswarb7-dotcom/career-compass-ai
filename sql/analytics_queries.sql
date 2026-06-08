-- ============================================================
-- CareerCompass AI — Analytics Queries
-- ============================================================

CREATE SCHEMA IF NOT EXISTS career_compass_ai;
SET search_path TO career_compass_ai, public;

-- Query 1: Top 5 Universities supplying SDEs to Blinkit
SELECT 
    college,
    COUNT(*) AS SDE_count,
    ROUND(AVG(experience_years)::numeric, 2) AS avg_experience_years
FROM employee_profiles
WHERE current_company = 'Blinkit' AND college IS NOT NULL AND college != ''
GROUP BY college
ORDER BY SDE_count DESC
LIMIT 5;


-- Query 2: Most Common Transition Sources (From other companies to Blinkit)
SELECT 
    source_company,
    COUNT(*) AS transition_count
FROM v_career_transitions
WHERE target_company = 'Blinkit'
GROUP BY source_company
ORDER BY transition_count DESC
LIMIT 10;


-- Query 3: Skill Density (Percentage of hired SDEs possessing specific skills)
SELECT 
    sm.skill_name,
    COUNT(es.profile_id) AS engineers_count,
    ROUND((COUNT(es.profile_id)::float / (SELECT COUNT(*) FROM employee_profiles)) * 100) AS possession_percentage
FROM skills_master sm
LEFT JOIN employee_skills es ON sm.skill_id = es.skill_id
GROUP BY sm.skill_id, sm.skill_name
ORDER BY engineers_count DESC;


-- Query 4: Specializations Breakdown
SELECT 
    r.role_name AS specialization,
    r.career_level AS domain,
    COUNT(*) AS count,
    ROUND((COUNT(*)::float / (SELECT COUNT(*) FROM employee_profiles)) * 100) AS percentage
FROM employee_profiles e
JOIN roles r ON e.role_id = r.role_id
GROUP BY r.role_name, r.career_level
ORDER BY count DESC;
