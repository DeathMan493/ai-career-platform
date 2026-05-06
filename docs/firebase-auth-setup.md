# Firebase Auth Setup

This project now supports Firebase Authentication on the frontend and Firebase Admin token verification on the FastAPI backend.
MongoDB remains the source of truth for user profiles, goals, skills, and recommendation data.

## What to do in Firebase Console

### 1. Create or open a Firebase project
In Firebase Console, create a project or use an existing one.

### 2. Add a Web App
Go to Project Settings -> General -> Your apps -> Add app -> Web.
Register the app and Firebase will show you a config snippet.

Copy these values into the project root `.env` file:
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`

A root `.env.example` file already exists with the expected keys.

### 3. Enable Sign-in Providers
Go to Build -> Authentication -> Sign-in method.
Enable:
- `Email/Password`
- `Google`

For Google sign-in, keep the default provider enabled and make sure your app domain is allowed.
During local development, `localhost` is usually fine.

### 4. Create a Service Account Key
Go to Project Settings -> Service Accounts.
Choose `Firebase Admin SDK` and click `Generate new private key`.
Download the JSON file.

Place it at:
- `backend/firebase-service-account.json`

A placeholder example file exists at:
- `backend/firebase-service-account.example.json`

### 5. Fill backend environment values
In `backend/.env`, set:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CREDENTIALS_PATH=backend/firebase-service-account.json`

## Install dependencies

Frontend:
```powershell
cd "E:\Amrita\SEMESTER 2\Projects\FSD"
npm install firebase
```

Backend:
```powershell
cd "E:\Amrita\SEMESTER 2\Projects\FSD\backend"
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the app

Backend:
```powershell
cd "E:\Amrita\SEMESTER 2\Projects\FSD\backend"
.\.venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

Frontend:
```powershell
cd "E:\Amrita\SEMESTER 2\Projects\FSD"
npm run dev
```

## Auth flow now

1. React signs the user in with Firebase Auth using email/password or Google popup.
2. React gets the Firebase ID token.
3. React sends that token to `POST /api/v1/auth/firebase`.
4. FastAPI verifies the token with Firebase Admin.
5. FastAPI creates or updates a MongoDB `users` record.
6. Protected profile and recommendation endpoints use the same Firebase bearer token.
