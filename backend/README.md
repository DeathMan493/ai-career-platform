# Backend Setup

This backend uses FastAPI for APIs and now includes a first-pass ingestion scaffold for MongoDB Atlas.

## Run the API

```powershell
cd "E:\Amrita\SEMESTER 2\Projects\FSD\backend"
.\.venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

## Environment Setup

Copy the example environment file and fill in your real values:

```powershell
cd "E:\Amrita\SEMESTER 2\Projects\FSD\backend"
Copy-Item .env.example .env
```

Fill these keys in `backend/.env`:
- `ALLOWED_ORIGINS` with the exact frontend origins allowed to call the API
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `OPENALEX_API_KEY`
- `USAJOBS_API_KEY`
- `USAJOBS_USER_AGENT`
- `ONET_API_KEY`

## Ingestion Commands

Run all commands from the `backend` directory with the virtual environment active.

### 1. Dry-run course normalization

```powershell
python -m app.ingestion.load_courses --dry-run
```

### 2. Import course datasets into MongoDB Atlas

```powershell
python -m app.ingestion.load_courses
```

### 3. Dry-run OpenAlex paper fetch

```powershell
python -m app.ingestion.fetch_openalex --query "knowledge graph recommendation" --dry-run
```

### 4. Import OpenAlex papers into MongoDB Atlas

```powershell
python -m app.ingestion.fetch_openalex --query "knowledge graph recommendation"
```

### 5. Dry-run USAJOBS fetch

```powershell
python -m app.ingestion.fetch_usajobs --keyword "machine learning" --dry-run
```

### 6. Import USAJOBS jobs into MongoDB Atlas

```powershell
python -m app.ingestion.fetch_usajobs --keyword "machine learning"
```

### 7. Test O*NET credentials with the placeholder fetcher

```powershell
python -m app.ingestion.fetch_onet --endpoint "online/occupations/"
```

### 8. Dry-run normalized skill building

```powershell
python -m app.ingestion.build_skills --dry-run
```

### 9. Build the `skills` collection and tag source records

```powershell
python -m app.ingestion.build_skills
```

## Notes

- MongoDB Compass is only the GUI. Atlas is the hosted database.
- Your current course datasets are already expected at:
  - `data/coursera course and skill 2024/coursera_course_dataset_v2_no_null.csv`
  - `data/coursera course and skill 2024/coursera_course_dataset_v3.csv`
  - `data/edx Udacity courera/final_cleaned_dataset.csv`
- The normalized schema is documented in `docs/data-schema.md`.
