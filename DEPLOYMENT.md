# Free Deployment Guide

This project can be deployed for free with:

- Backend: Render free web service
- Frontend: Vercel Hobby plan
- Existing hosted databases: MongoDB Atlas and Neo4j Aura

## 1. Push to GitHub

Create a private GitHub repository and push this project. Do not commit local secret files:

- `.env`
- `backend/.env`
- `backend/*firebase-adminsdk*.json`
- `*creds*.txt`

## 2. Deploy Backend on Render

In Render, create a new Blueprint or Web Service from the GitHub repository.

If using the `render.yaml` blueprint, Render will create `ai-platform-api` with:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set these Render environment variables:

- `SECRET_KEY`
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_SERVICE_ACCOUNT_JSON`
- `ALLOWED_ORIGINS`

Use your full frontend URL for `ALLOWED_ORIGINS`, for example:

```text
["https://your-vercel-project.vercel.app"]
```

For `FIREBASE_SERVICE_ACCOUNT_JSON`, paste the full Firebase service account JSON contents as one environment value.

## 3. Deploy Frontend on Vercel

Import the same GitHub repository in Vercel.

Use:

- Framework preset: `Vite`
- Build command: `npm run build`
- Output directory: `dist`

Set this Vercel environment variable:

```text
VITE_API_BASE_URL=https://your-render-service.onrender.com/api/v1
```

Also add the existing Firebase web environment variables from your local root `.env`.

## 4. Update Firebase Authorized Domains

In Firebase Console, go to Authentication -> Settings -> Authorized domains.

Add:

- Your Vercel frontend domain
- Your Render backend domain is not required for browser auth, but keeping the backend project ID aligned is required.

## 5. Final Smoke Test

After both deployments finish:

- Open `https://your-render-service.onrender.com/health`
- Open the Vercel site
- Sign in with Google
- Visit Dashboard, Courses, Papers, Profile, Graph

Render free services can sleep after inactivity, so the first backend request may take a little while.
