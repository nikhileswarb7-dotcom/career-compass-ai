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
| **Alice Trace**<br>(1st Year Student targetting Google Software Development Engineer) | `19` | `1f29c62c-77dc-4141-8a7a-d63e7888de78` | Dynamic recalculation on GET `/api/recommendations/1f29c62c-77dc-4141-8a7a-d63e7888de78` | Dynamic timeline generation on GET `/api/roadmap/1f29c62c-77dc-4141-8a7a-d63e7888de78` | Unified state queries on GET `/api/readiness/1f29c62c-77dc-4141-8a7a-d63e7888de78` & `/api/recommendations/1f29c62c-77dc-4141-8a7a-d63e7888de78` |
| **Bob Trace**<br>(3rd Year Student targetting Amazon Backend Engineer) | `20` | `8b0f995b-77e5-4154-bd15-c37d96b1c8f9` | Dynamic recalculation on GET `/api/recommendations/8b0f995b-77e5-4154-bd15-c37d96b1c8f9` | Dynamic timeline generation on GET `/api/roadmap/8b0f995b-77e5-4154-bd15-c37d96b1c8f9` | Unified state queries on GET `/api/readiness/8b0f995b-77e5-4154-bd15-c37d96b1c8f9` & `/api/recommendations/8b0f995b-77e5-4154-bd15-c37d96b1c8f9` |
| **Charlie Trace**<br>(Junior Software Engineer targetting Microsoft SRE / DevOps Engineer) | `21` | `d0992d83-05e6-4a4e-912f-53d959d34ea1` | Dynamic recalculation on GET `/api/recommendations/d0992d83-05e6-4a4e-912f-53d959d34ea1` | Dynamic timeline generation on GET `/api/roadmap/d0992d83-05e6-4a4e-912f-53d959d34ea1` | Unified state queries on GET `/api/readiness/d0992d83-05e6-4a4e-912f-53d959d34ea1` & `/api/recommendations/d0992d83-05e6-4a4e-912f-53d959d34ea1` |


## 3. Session Isolation & Safety Assertions

- **[PASS] Student Row Verification**: Verified that a new row in the `students` table is created on every onboarding attempt.
- **[PASS] Session Row Verification**: Verified that a new session UUID is generated and saved in `analysis_sessions` for every onboarding instance.
- **[PASS] Dynamic Computation Verification**: Confirmed that GET `/api/recommendations/{session_id}` and GET `/api/roadmap/{session_id}` dynamically read the session's student parameters and run the core recommendation engine on-the-fly.
- **[PASS] Zero Cache Reuse Verification**: Verified that `analysis_sessions` does not store nested recommendation list caches, ensuring that modifications to database configurations or the student profile are immediately reflected on subsequent calls.
