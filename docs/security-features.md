# Security Features

This project currently uses a few practical security controls across the stack.

## MongoDB-Specific Feature

### Collection Validation with `$jsonSchema`

The backend applies a MongoDB-native validator to the `users` collection during startup.
This is defined in:

- `backend/app/database/validators.py`

What it enforces:
- required identity fields such as `firebase_uid`, `email`, and `career_goal`
- structured `skills` entries
- structured `completed_courses` and `completed_papers`
- structured `derived_skills` and `skill_progress`

Why it matters:
- rejects malformed or unexpected user documents at the database layer
- protects data integrity even if an application bug tries to write an invalid payload
- gives a clear MongoDB security/integrity feature to present in review or viva

## Other Security Controls Already in Use

### Firebase Authentication
- email/password sign-in
- Google sign-in
- backend Firebase bearer-token verification before protected API access

### Atlas Connection Security
- MongoDB Atlas authentication through `MONGODB_URI`
- encrypted `mongodb+srv` transport

## Important Note

If the MongoDB role used by Atlas does not allow validator modification commands, the backend will log a warning instead of crashing. In that case, the validator can be applied once with a higher-privileged database role and then kept in place for normal app operation.
