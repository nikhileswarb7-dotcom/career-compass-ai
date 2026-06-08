-- ============================================================
-- CareerCompass AI — Stored Procedures & Functions
-- ============================================================

CREATE SCHEMA IF NOT EXISTS career_compass_ai;
SET search_path TO career_compass_ai, public;

-- Procedure: Insert a student assessment and automatically identify gaps
CREATE OR REPLACE PROCEDURE sp_assess_student(
    p_student_id INT,
    p_company_role_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Clear previous gaps
    DELETE FROM skill_gaps WHERE student_id = p_student_id;
    
    -- Insert new gaps: skills required by target role that are not possessed by student
    INSERT INTO skill_gaps (id, student_id, skill_id, priority)
    SELECT 
        COALESCE((SELECT MAX(id) FROM skill_gaps), 0) + ROW_NUMBER() OVER(),
        p_student_id,
        sreq.skill_id,
        sreq.priority
    FROM role_skill_requirements sreq
    WHERE sreq.company_role_id = p_company_role_id
      AND sreq.skill_id NOT IN (
          SELECT skill_id FROM student_skills WHERE student_id = p_student_id
      );
END;
$$;


-- Function: Recalculate signal weights dynamically
CREATE OR REPLACE FUNCTION fn_recalculate_signals()
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_max_skill_freq INT;
    v_max_college_freq INT;
BEGIN
    -- Get max frequency counts for normalization
    SELECT MAX(frequency) INTO v_max_skill_freq FROM v_skills_frequency;
    
    -- 1. Update Skill signals weights based on latest profile statistics
    UPDATE hiring_signals hs
    SET weight = GREATEST(4, ROUND((sf.frequency::float / v_max_skill_freq) * 10))
    FROM v_skills_frequency sf
    WHERE hs.signal_name = sf.skill_name AND hs.signal_type = 'Skill';

END;
$$;
