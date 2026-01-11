# Phase 2: AI Backlog Generation - Text→Epics demo

## Requirements

Add AI-powered backlog generation to Phase 1 application.

## Structure

```
backend/
├── agents/
│   ├── __init__.py
│   └── backlog_agent.py
├── models/
│   └── schemas.py
└── static/
    └── index.html (updated)
```

## Database Upgrade

Added Epics table:
- id (PRIMARY KEY)
- project_id (FOREIGN KEY)
- title
- stories (JSON)
- total_story_points
- sprint
- created_at

## Backlog Agent (backlog_agent.py)

- Input: project summary text
- Output: 3 Epics → 10 Stories + story points (Fibonacci 1-13) → 3 Sprints → timeline estimate
- Uses OpenAI API (from .env) or mocks if no key

## Endpoints

- POST /generate-backlog/{project_id} → triggers agent → saves Epics
- GET /projects/{id}/backlog → shows generated backlog

## UI Updates

- "Generate Backlog" button per project
- Loading spinner
- Beautiful table: Epic | Stories | Points | Sprint
- Timeline estimate displayed
- Modal dialog for backlog view

## Test

1. Create project
2. Click "Generate Backlog"
3. See AI-generated Agile artifacts instantly

## Git Commit

```
git commit -m "Phase 2: AI Backlog Generation - Text→Epics demo"
```
