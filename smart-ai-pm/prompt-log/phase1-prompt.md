# Phase 1: Core MVP - Web app working

## Requirements

Create a FastAPI web application with the following structure:

```
smart-ai-pm/
├── README.md
├── PROMPT_LOG.md  
├── .env.example
├── .gitignore
├── requirements.txt
├── backend/
│   ├── main.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   └── static/
│       └── index.html
└── data/
    └── smart_pm.db
```

## Requirements.txt

- fastapi==0.115.0
- uvicorn==0.30.6
- sqlalchemy==2.0.35
- python-multipart==0.0.9
- pydantic==2.9.2

## .env.example

```
OPENAI_API_KEY=sk-xxx
JIRA_URL=https://your-site.atlassian.net
JIRA_API_TOKEN=xxx
DATABASE_URL=sqlite:///data/smart_pm.db
```

## Database (db.py)

Projects table with columns: id, name, summary, created_at

## FastAPI (main.py)

- GET / → serves static/index.html
- POST /projects → create project (name, summary)
- GET /projects → list all projects as JSON
- Auto-creates SQLite DB

## UI (index.html)

Clean web form + projects table. Responsive. "Add Project" button → instant table update via fetch().

## Test

Run: `cd backend && uvicorn main:app --reload` → localhost:8000 = working web app MVP

## Git Commit

After setup:
```bash
git add .
git commit -m "Phase 1: Core MVP - Web app working"
```
