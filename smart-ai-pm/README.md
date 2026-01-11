# Smart AI PM

A smart project management application with AI integration.

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
