# Manual End-to-End Roadmap Verification - CareerCompass AI

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.recommendation_engine import generate_recommendation

def run_verification():
    print("=" * 60)
    print("MANUAL END-TO-END ROADMAP VERIFICATION")
    print("=" * 60)

    # 3rd Year student targeting Blinkit SDE with a common set of pre-existing skills
    qualification = "3rd Year Student"
    known_skills = ["Java", "Git & GitHub"]
    dream_company = "Blinkit"
    target_role = "Software Development Engineer (SDE)"

    print(f"Generating recommendation for:\n  Qual: {qualification}\n  Known Skills: {known_skills}\n  Target: {target_role} at {dream_company}\n")

    res = generate_recommendation(
        qualification=qualification,
        known_skills=known_skills,
        dream_company=dream_company,
        target_role=target_role,
        skip_llm=True
    )

    timeline = res.get("timeline", {})
    stages = timeline.get("stages", [])
    print(f"Total Stages Generated: {len(stages)}")

    empty_stages = []
    removed_items_count = {
        "video": 0,
        "material": 0,
        "mcq": 0,
        "interview_question": 0
    }

    # Extract validation evidence from trace to count removed items
    trace = res.get("decision_trace", {})
    val_trace = trace.get("roadmap_consistency_validation_trace", [])

    for stg in stages:
        stg_num = stg["stage"]
        title = stg["title"]
        v_count = len(stg.get("videos", []))
        m_count = len(stg.get("materials", []))
        mq_count = len(stg.get("mcqs", []))
        iq_count = len(stg.get("interview_questions", []))

        print(f"Stage {stg_num}: {title}")
        print(f"  Videos:              {v_count}")
        print(f"  Materials:           {m_count}")
        print(f"  MCQs:                {mq_count}")
        print(f"  Interview Questions: {iq_count}")
        
        # Check if stage is empty for any content type
        if v_count == 0 or m_count == 0 or mq_count == 0 or iq_count == 0:
            empty_stages.append((stg_num, title))

    for evidence in val_trace:
        if evidence["prerequisite_status"] == "unsatisfied":
            removed_items_count[evidence["content_type"]] += 1

    print("\nVerification Evidence Stats:")
    print(f"  Total validation evidence logs: {len(val_trace)}")
    print(f"  Total removed/rejected items by type: {removed_items_count}")
    print(f"  Empty content stages: {empty_stages}")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
