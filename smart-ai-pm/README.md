# Smart AI PM

A smart project management application with AI integration.

## 🎯 ONE-CLICK START (Hackathon Demo)

**Windows**: Double-click `start.bat`
**Mac/Linux**: `./start.sh`
**Or**: `python run.py`

**Auto-installs everything** → Web app live at http://localhost:8000

## ✅ Demo Flow
1. Open http://localhost:8000
2. Fill "Project Name" + "Summary" 
3. Click "Create Project" → See in table instantly
4. 🎉 MVP Working!

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

3. Run the application:
```bash
cd backend
uvicorn main:app --reload
```

4. Open your browser to `http://localhost:8000`

## Features

- Create and manage projects
- Clean, responsive web interface
- SQLite database for data persistence
