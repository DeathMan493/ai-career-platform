# AI Platform Frontend API Contract

## Purpose

This document defines the backend contract expected by the React frontend.
It now reflects the implemented FastAPI + Firebase flow used by the current app and covers the core pages:

- Auth
- Profile
- Dashboard
- Skill Gap
- Graph View

The current frontend is already integrated with the backend. Local mock data remains only as a UI fallback if the backend is unavailable.

## Base URL

```text
/api/v1
```

## Response Convention

Successful responses should follow this structure when practical:

```json
{
  "success": true,
  "message": "Optional message",
  "data": {}
}
```

Error responses:

```json
{
  "success": false,
  "message": "Human readable error message",
  "errors": []
}
```

## 1. Auth

### POST `/auth/firebase`

Exchanges a Firebase ID token for an application session payload and ensures the user exists in MongoDB.

Request:

```json
{
  "id_token": "firebase-id-token"
}
```

Response:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "user_001",
      "name": "Amrita User",
      "email": "amrita@example.com"
    },
    "token": "firebase-uid"
  }
}
```

Notes:
- direct `/auth/login` and `/auth/signup` are intentionally disabled
- authentication is handled through Firebase Email/Password and Google Sign-In on the frontend

## 2. Profile

### GET `/profile/me`

Returns the logged-in user profile.

Response:

```json
{
  "success": true,
  "data": {
    "id": "user_001",
    "name": "Amrita User",
    "career_goal": "AI Researcher",
    "skills": [
      {
        "skill": "Python",
        "level": "Advanced"
      },
      {
        "skill": "Machine Learning",
        "level": "Advanced"
      }
    ]
  }
}
```

### PUT `/profile/me`

Updates user profile.

Request:

```json
{
  "career_goal": "AI Researcher",
  "skills": [
    {
      "skill": "Python",
      "level": "Advanced"
    },
    {
      "skill": "Neo4j",
      "level": "Intermediate"
    }
  ]
}
```

Response:

```json
{
  "success": true,
  "message": "Profile updated",
  "data": {
    "id": "user_001",
    "name": "Amrita User",
    "career_goal": "AI Researcher",
    "skills": [
      {
        "skill": "Python",
        "level": "Advanced"
      },
      {
        "skill": "Neo4j",
        "level": "Intermediate"
      }
    ]
  }
}
```

## 3. Dashboard

### GET `/dashboard`

Returns the full dashboard payload for the current user.

Response:

```json
{
  "success": true,
  "data": {
    "role_summary": {
      "title": "AI Researcher",
      "mission": "Blend advanced learning, research depth, and real-world problem solving into a focused AI career path.",
      "focus_areas": [
        "Representation learning",
        "Research communication",
        "Model deployment awareness"
      ]
    },
    "metrics": {
      "profile_skill_count": 4,
      "course_count": 3,
      "paper_count": 3,
      "job_count": 3,
      "high_priority_gap_count": 2,
      "readiness_score": 48
    },
    "courses": [
      {
        "id": "course_001",
        "title": "Advanced Deep Learning Systems",
        "provider": "Coursera",
        "level": "Advanced",
        "duration": "8 weeks",
        "reason": "Builds stronger model design intuition for your research-focused goal.",
        "tags": ["Neural Networks", "Optimization", "PyTorch"]
      }
    ],
    "papers": [
      {
        "id": "paper_001",
        "title": "Graph Attention Networks",
        "venue": "ICLR",
        "year": 2018,
        "reason": "Relevant to your graph-driven recommendation direction.",
        "tags": ["Graphs", "Attention", "Embeddings"]
      }
    ],
    "jobs": [
      {
        "id": "job_001",
        "title": "Applied AI Research Assistant",
        "company": "Insight AI Lab",
        "fit": "Target fit",
        "reason": "Aligns closely with your goal.",
        "tags": ["Research", "Evaluation", "Deep Learning"]
      }
    ],
    "recommendation_paths": [
      "Python -> Machine Learning -> Deep Learning Systems Course -> Applied AI Research Assistant"
    ],
    "missing_skills": [
      {
        "name": "Graph Theory",
        "priority": "High",
        "progress": 38,
        "reason": "Needed for graph traversal and graph learning."
      }
    ]
  }
}
```

## 4. Skill Gap

### GET `/skill-gap`

Returns a skill-gap specific view.

Response:

```json
{
  "success": true,
  "data": {
    "career_goal": "AI Researcher",
    "summary": "Blend advanced learning, research depth, and real-world problem solving into a focused AI career path.",
    "focus_areas": [
      "Representation learning",
      "Research communication"
    ],
    "current_skill_count": 4,
    "gap_count": 4,
    "missing_skills": [
      {
        "name": "Research Methodology",
        "priority": "High",
        "progress": 44,
        "reason": "Improves experiment design and evaluation quality."
      }
    ],
    "roadmap": [
      {
        "phase": "Strengthen foundations",
        "timeline": "Weeks 1-3",
        "action": "Focus on graph theory, ranking metrics, and graph queries."
      }
    ],
    "bridges": {
      "courses": [
        {
          "id": "course_001",
          "title": "Graph Neural Networks in Practice",
          "reason": "Supports graph-based recommendation work."
        }
      ],
      "papers": [
        {
          "id": "paper_001",
          "title": "A Survey on Knowledge Graph Embeddings",
          "reason": "Connects directly to graph learning setup."
        }
      ],
      "jobs": [
        {
          "id": "job_001",
          "title": "Knowledge Graph Engineer",
          "reason": "Great long-term fit if graph skills improve."
        }
      ]
    }
  }
}
```

## 5. Graph View

### GET `/graph`

Returns graph nodes, edges, and explainable paths.

Response:

```json
{
  "success": true,
  "data": {
    "career_goal": "AI Researcher",
    "nodes": [
      {
        "id": "user",
        "label": "User",
        "type": "user",
        "x": 10,
        "y": 50
      },
      {
        "id": "python",
        "label": "Python",
        "type": "skill",
        "x": 28,
        "y": 28
      }
    ],
    "edges": [
      {
        "from": "user",
        "to": "python",
        "label": "has skill"
      }
    ],
    "recommendation_paths": [
      "Python -> Machine Learning -> Deep Learning Systems Course -> Applied AI Research Assistant"
    ],
    "legend": {
      "user": "User profile and goal",
      "skill": "Current or missing skill",
      "course": "Recommended learning content",
      "paper": "Relevant research material",
      "job": "Career outcome or role match"
    }
  }
}
```

## 6. Optional Research/Evaluation APIs

These are not required for the first backend phase, but useful for publication-level features.

### GET `/evaluation/metrics`

Response:

```json
{
  "success": true,
  "data": {
    "precision_at_k": 0.78,
    "recall_at_k": 0.71,
    "diversity_score": 0.66,
    "cross_domain_alignment": 0.74
  }
}
```

### GET `/evaluation/recommendations/explanations`

Response:

```json
{
  "success": true,
  "data": [
    {
      "target_id": "job_001",
      "target_type": "job",
      "explanation_path": [
        "Python",
        "Machine Learning",
        "Deep Learning Systems",
        "Applied AI Research Assistant"
      ]
    }
  ]
}
```

## 7. Frontend Mapping

### Auth page

- Uses Firebase Web SDK for sign-in and sign-up
- Uses `/auth/firebase` for backend session exchange

### Profile page

- Uses `GET /profile/me`
- Uses `PUT /profile/me`

### Dashboard page

- Uses `GET /dashboard`

### Skill Gap page

- Uses `GET /skill-gap`

### Graph page

- Uses `GET /graph`

## 8. Recommended Backend Separation

### MongoDB

- users
- profiles
- saved sessions
- cached recommendation snapshots

### Neo4j

- User
- Skill
- Course
- Paper
- Job
- relationships such as `HAS_SKILL`, `REQUIRES`, `MATCHES`, `RELATES_TO`, `LEADS_TO`

## 9. Notes For Backend Phase

- Keep field names stable once backend starts.
- IDs should be explicit for all recommendable entities.
- The frontend can accept static graph coordinates initially.
- Later, graph coordinates can be generated dynamically if needed.
- Recommendation explanations should remain first-class, not optional.
