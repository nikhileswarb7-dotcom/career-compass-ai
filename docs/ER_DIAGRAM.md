# CareerCompass AI — Entity Relationship Diagram

## Entity Map

```
companies ──────────────────────────────────────────────────────────┐
    │                                                                │
    │ (1:many via company_roles)                                     │
    ▼                                                                │
company_roles ◄────── roles                                         │
    │                   │                                            │
    │                   │ (via role_skills)                          │
    │                   ▼                                            │
    │                skills ◄───────────────────────────────────────┤
    │                   │                                            │
    │                   │ (via stage_skills)                         │
    │                   ▼                                            │
    ├──────────► roadmaps ◄──── qualifications                      │
    │                │               │                               │
    │                │               │ (via resume/linkedin/github)  │
    │                ▼               ▼                               │
    │           roadmap_stages ──► stage_skills                     │
    │                │                                               │
    │                ├──► stage_projects ──► projects                │
    │                │                                               │
    │                └──► stage_resources ──► resources              │
    │                                                                │
    ├──────────► interview_questions                                 │
    │                                                                │
    └──────────► students ──► student_skills ──► skills             │
                    │                                                 │
                    ├──► student_progress ──► roadmap_stages        │
                    │                                                 │
                    └──► career_assessments                          │
```

## Table Relationships

### Core Chain
```
companies (1) ──< company_roles >── (1) roles
company_roles (1) ──< role_skills >── (1) skills
qualifications (1) ──< roadmaps >── (1) company_roles
roadmaps (1) ──< roadmap_stages
roadmap_stages (1) ──< stage_skills >── (1) skills
roadmap_stages (1) ──< stage_projects >── (1) projects
roadmap_stages (1) ──< stage_resources >── (1) resources
```

### Guidance Chain
```
qualifications (1) ──< resume_guidance
qualifications (1) ──< linkedin_guidance
qualifications (1) ──< github_guidance
```

### Interview Chain
```
company_roles (1) ──< interview_questions
```

### User Chain
```
students >── (1) qualifications
students >── (1) company_roles  [target]
students (1) ──< student_skills >── (1) skills
students (1) ──< student_progress >── (1) roadmap_stages
students (1) ──< career_assessments
```

## Key Design Decisions

### 1. Scalability
The `company_roles` junction table means adding Google SDE requires only:
- 1 new row in `companies`
- Reuse existing `roles` row for SDE
- 1 new row in `company_roles`
- New rows in `role_skills`, `roadmaps`, `roadmap_stages`
- No schema changes needed

### 2. JSONB for Flexible Data
Fields like `tech_stack`, `hiring_process`, `learning_goals` are stored as JSONB because:
- Their internal structure varies per record
- They don't need to be queried relationally
- They can be extended without schema migration

### 3. Qualification × Company_Role Uniqueness
`roadmaps` has a UNIQUE constraint on `(qualification_id, company_role_id)` ensuring:
- Exactly one roadmap per (qualification, target role) combination
- No duplicate roadmaps
- Clean foreign key references from `roadmap_stages`

### 4. Score Weights
Skill scoring weights are NOT stored in the database (they are in the recommendation engine) to keep them easy to tune without database migration.
```
High priority skill  = 10 points
Medium priority skill = 5 points
Low priority skill   = 2 points
Total possible       = 101 points
```

## Primary Keys
All tables use `SERIAL` (auto-increment integer) PKs except:
- `students`: Uses `UUID` (gen_random_uuid()) for future web app compatibility

## Foreign Key Strategy
All FKs use `ON DELETE CASCADE` or `ON DELETE SET NULL` to prevent orphaned records:
- Cascade: when parent is deleted, child records are also deleted
- Set Null: when parent is deleted, FK column is set to NULL (used for optional references)
