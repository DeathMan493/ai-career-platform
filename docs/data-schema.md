# Data Schema and Ingestion Plan

This document defines the normalized data shape for the first backend ingestion phase.
The immediate goal is to load free course datasets plus OpenAlex and USAJOBS into MongoDB Atlas.
Neo4j can be added later by projecting these normalized records into graph nodes and relationships.
O*NET is now prepared as a credentialed source for skill normalization and occupation enrichment.

## MongoDB Collections

### `users`
Stores Firebase-linked application users, profile state, completion history, and derived skill progress.

Suggested fields:
- `_id`
- `firebase_uid`
- `name`
- `email`
- `career_goal`
- `skills`: array of `{ skill, level }`
- `completed_courses`: array of dashboard-style course items plus `completed_at`
- `completed_papers`: array of dashboard-style paper items plus `completed_at`
- `derived_skills`: array of `{ skill, level, progress }`
- `skill_progress`: array of `{ skill, progress }`
- `last_login_at`
- `created_at`
- `updated_at`

Security/integrity guard:
- the backend now applies a MongoDB `$jsonSchema` validator to the `users` collection at startup so malformed user/profile documents are rejected before they can be written.

### `courses`
Normalized from all downloaded CSV datasets.

Fields:
- `_id`
- `source`: dataset folder name
- `source_id`: original row id when available
- `title`
- `provider`
- `skills`: string[]
- `rating`: number | null
- `review_count`: number | null
- `students_enrolled`: string | null
- `difficulty`: string | null
- `course_type`: string | null
- `duration`: string | null
- `description`: string | null
- `url`: string | null
- `normalized_skills`: string[]
- `raw`: original row object

Indexes:
- `title`
- `provider`
- `skills`

### `papers`
Normalized from OpenAlex first. arXiv and Crossref can be merged later.

Fields:
- `_id`
- `source`: `openalex`
- `source_id`
- `title`
- `abstract`
- `publication_year`
- `doi`
- `openalex_id`
- `authors`: string[]
- `concepts`: array of `{ name, score }`
- `keywords`: string[]
- `url`
- `primary_location`
- `normalized_skills`: string[]
- `raw`

Indexes:
- `title`
- `keywords`
- `publication_year`

### `jobs`
Normalized from USAJOBS.

Fields:
- `_id`
- `source`: `usajobs`
- `source_id`
- `title`
- `organization`
- `department`
- `locations`: string[]
- `minimum_salary`
- `maximum_salary`
- `qualification_summary`
- `requirements`
- `security_clearance`
- `travel_required`
- `apply_url`
- `normalized_skills`: string[]
- `raw`

Indexes:
- `title`
- `organization`
- `locations`

### `skills`
Built by extracting and deduplicating skills from courses, papers, jobs, and later O*NET.

Suggested fields:
- `_id`
- `name`
- `aliases`: string[]
- `source_tags`: string[]
- `source_counts`: object
- `occurrence_count`: number
- `examples`: object
- `onet_code`: string | null
- `category`: string | null
- `description`: string | null

## Neo4j Projection Plan

Later graph nodes:
- `(:User)`
- `(:Skill)`
- `(:Course)`
- `(:Paper)`
- `(:Job)`

Later relationships:
- `(:User)-[:HAS_SKILL]->(:Skill)`
- `(:Course)-[:TEACHES]->(:Skill)`
- `(:Paper)-[:RELATES_TO]->(:Skill)`
- `(:Job)-[:REQUIRES]->(:Skill)`
- `(:User)-[:INTERESTED_IN]->(:Job)`
- `(:Course)-[:SUPPORTS]->(:Job)`
- `(:Paper)-[:SUPPORTS]->(:Job)`

## Ingestion Scripts

Implemented scripts:
- `backend/app/ingestion/load_courses.py`
- `backend/app/ingestion/fetch_openalex.py`
- `backend/app/ingestion/fetch_usajobs.py`
- `backend/app/ingestion/fetch_onet.py` (API-key placeholder)
- `backend/app/ingestion/build_skills.py`

These scripts write to MongoDB Atlas once `backend/.env` is configured.

## Required Environment Variables

Set these in `backend/.env`:
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `OPENALEX_API_KEY`
- `USAJOBS_API_KEY`
- `USAJOBS_USER_AGENT`
- `ONET_API_KEY`

Note:
- `USAJOBS_USER_AGENT` should usually be your email address or app contact string.
- `fetch_onet.py` is a starter placeholder so you can verify your O*NET API key before building the full skill importer.
- `build_skills.py` creates the shared `skills` collection and writes `normalized_skills` back to `courses`, `papers`, and `jobs`.
- Do not commit real secrets into the repository.
