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
| **Alice Trace**<br>(1st Year Student targetting Google Software Development Engineer (SDE)) | `277` | `9cb5d64a-a094-4a6a-93a9-750406e2f7a4` | Dynamic recalculation on GET `/api/recommendations/9cb5d64a-a094-4a6a-93a9-750406e2f7a4` | Dynamic timeline generation on GET `/api/roadmap/9cb5d64a-a094-4a6a-93a9-750406e2f7a4` | Unified state queries on GET `/api/readiness/9cb5d64a-a094-4a6a-93a9-750406e2f7a4` & `/api/recommendations/9cb5d64a-a094-4a6a-93a9-750406e2f7a4` |
| **Bob Trace**<br>(3rd Year Student targetting Amazon Backend Developer) | `278` | `b6a13a33-b7ac-41eb-a991-1cf5936fc889` | Dynamic recalculation on GET `/api/recommendations/b6a13a33-b7ac-41eb-a991-1cf5936fc889` | Dynamic timeline generation on GET `/api/roadmap/b6a13a33-b7ac-41eb-a991-1cf5936fc889` | Unified state queries on GET `/api/readiness/b6a13a33-b7ac-41eb-a991-1cf5936fc889` & `/api/recommendations/b6a13a33-b7ac-41eb-a991-1cf5936fc889` |
| **Charlie Trace**<br>(Junior Software Engineer targetting Microsoft DevOps Engineer) | `279` | `43594b5c-ae1e-45fc-96f0-d99835186ad5` | Dynamic recalculation on GET `/api/recommendations/43594b5c-ae1e-45fc-96f0-d99835186ad5` | Dynamic timeline generation on GET `/api/roadmap/43594b5c-ae1e-45fc-96f0-d99835186ad5` | Unified state queries on GET `/api/readiness/43594b5c-ae1e-45fc-96f0-d99835186ad5` & `/api/recommendations/43594b5c-ae1e-45fc-96f0-d99835186ad5` |


## 3. Session Isolation & Safety Assertions

- **[PASS] Student Row Verification**: Verified that a new row in the `students` table is created on every onboarding attempt.
- **[PASS] Session Row Verification**: Verified that a new session UUID is generated and saved in `analysis_sessions` for every onboarding instance.
- **[PASS] Dynamic Computation Verification**: Confirmed that GET `/api/recommendations/{session_id}` and GET `/api/roadmap/{session_id}` dynamically read the session's student parameters and run the core recommendation engine on-the-fly.
- **[PASS] Zero Cache Reuse Verification**: Verified that `analysis_sessions` does not store nested recommendation list caches, ensuring that modifications to database configurations or the student profile are immediately reflected on subsequent calls.
