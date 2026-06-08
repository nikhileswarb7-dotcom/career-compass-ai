# CareerCompass AI — Backend Session Onboarding Audit & Trace Report

This report details the audit trace of student registration, session creation, and recommendation retrieval for three distinct brand-new onboarding runs.

## 1. Onboarding Pipeline Trace Stages
For any new student registering on the platform:
1. **Profile Submission (`student_form.html`)**: Form inputs (name, branch, qualification, target role, known skills) are captured and passed to the parsing agent.
2. **Parsing & DB Insert (`/api/student/analyze`)**: 
   - A new student row is created in `students` with a unique generated email signature (to prevent namespace collisions).
   - A new session row is created in `analysis_sessions` in the `uploaded` status linked directly to the `student_id`.
3. **Skill Confirmation (`profile_analysis.html`)**: Known skills are verified, triggering `/api/recommend` which deletes previous skills, inserts the confirmed ones, and updates the session status to `skills_confirmed`.
4. **Dynamic On-the-fly Computation**: All subsequent data calls for dashboard, recommendations, interview prep, and roadmaps are resolved dynamically on GET requests via `session_id`, ensuring no stale or cached recommendation JSON lists are stored/reused.

## 2. Onboarding Trace Log Table

| User Profile | Student ID | Session ID (UUID) | Recommendation Source | Roadmap Source | Career Report Source |
| --- | --- | --- | --- | --- | --- |
| **Alice Trace**<br>(1st Year Student targetting Google Software Development Engineer) | `53` | `15901f3b-e1c2-4a1d-97db-402dcbf00eed` | Dynamic recalculation on GET `/api/recommendations/15901f3b-e1c2-4a1d-97db-402dcbf00eed` | Dynamic timeline generation on GET `/api/roadmap/15901f3b-e1c2-4a1d-97db-402dcbf00eed` | Unified state queries on GET `/api/readiness/15901f3b-e1c2-4a1d-97db-402dcbf00eed` & `/api/recommendations/15901f3b-e1c2-4a1d-97db-402dcbf00eed` |
| **Bob Trace**<br>(3rd Year Student targetting Amazon Backend Engineer) | `54` | `a36bbba6-cacd-47f8-a919-7ebc154fb8df` | Dynamic recalculation on GET `/api/recommendations/a36bbba6-cacd-47f8-a919-7ebc154fb8df` | Dynamic timeline generation on GET `/api/roadmap/a36bbba6-cacd-47f8-a919-7ebc154fb8df` | Unified state queries on GET `/api/readiness/a36bbba6-cacd-47f8-a919-7ebc154fb8df` & `/api/recommendations/a36bbba6-cacd-47f8-a919-7ebc154fb8df` |
| **Charlie Trace**<br>(Junior Software Engineer targetting Microsoft SRE / DevOps Engineer) | `55` | `2ef8ecf6-a9b0-49fd-bf9b-2ca7c1e0d2c7` | Dynamic recalculation on GET `/api/recommendations/2ef8ecf6-a9b0-49fd-bf9b-2ca7c1e0d2c7` | Dynamic timeline generation on GET `/api/roadmap/2ef8ecf6-a9b0-49fd-bf9b-2ca7c1e0d2c7` | Unified state queries on GET `/api/readiness/2ef8ecf6-a9b0-49fd-bf9b-2ca7c1e0d2c7` & `/api/recommendations/2ef8ecf6-a9b0-49fd-bf9b-2ca7c1e0d2c7` |


## 3. Session Isolation & Safety Assertions

- **[PASS] Student Row Verification**: Verified that a new row in the `students` table is created on every onboarding attempt.
- **[PASS] Session Row Verification**: Verified that a new session UUID is generated and saved in `analysis_sessions` for every onboarding instance.
- **[PASS] Dynamic Computation Verification**: Confirmed that GET `/api/recommendations/{session_id}` and GET `/api/roadmap/{session_id}` dynamically read the session's student parameters and run the core recommendation engine on-the-fly.
- **[PASS] Zero Cache Reuse Verification**: Verified that `analysis_sessions` does not store nested recommendation list caches, ensuring that modifications to database configurations or the student profile are immediately reflected on subsequent calls.
