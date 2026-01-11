# Prompt Log

This file tracks development phases and prompts.

## Phase 1: Core MVP - Web app working

Initial setup with FastAPI backend, SQLite database, and responsive web UI.

**Status**: ✅ Complete

**Files Created**:
- Project structure with backend/, data/, prompt-log/ directories
- FastAPI application (backend/main.py)
- Database models (backend/database/db.py)
- Responsive web UI (backend/static/index.html)
- Requirements.txt with all dependencies
- .env.example template
- .gitignore and .cursorignore for security

## Phase 1.1: Security Hardening

**Date**: Latest
**Status**: ✅ Complete

**Changes**:
- Comprehensive .gitignore update with secret exclusion patterns
- Created .cursorignore for privacy mode
- Secret scan performed - no real secrets detected
- Code review: All code uses environment variables (secure pattern)

**Files Updated**:
- .gitignore - Added patterns for .env*, keys, certificates, secrets directories
- .cursorignore - Created for Cursor IDE privacy mode

## Phase 1.2: Hackathon One-Click Startup

**Date**: Latest
**Status**: ✅ Complete

**Goal**: Single command → working web app at localhost:8000

**Files Created**:
- run.py - Single executable entrypoint (auto-installs deps, runs server)
- start.bat - Windows one-click launcher
- start.sh - Mac/Linux one-click launcher

**Files Updated**:
- README.md - Added "ONE-CLICK START" section with demo flow

**Usage**:
- Windows: Double-click `start.bat` or `python run.py`
- Mac/Linux: `./start.sh` or `python run.py`
- Auto-installs dependencies and starts server on port 8000

## Phase 1.3: ModuleNotFoundError Fix

**Date**: Latest
**Status**: ✅ Complete

**Problem**: ModuleNotFoundError: No module named 'database'

**Solution**: Simplified to inline SQLite (no external imports)

**Changes**:
- Rewrote backend/main.py to use inline sqlite3 (Python built-in)
- Embedded HTML directly in Python (no separate static file)
- Fixed run.py with better error handling
- Removed SQLAlchemy dependency for hackathon simplicity

**Files Updated**:
- backend/main.py - Complete rewrite with inline SQLite
- run.py - Fixed and simplified

**Result**: ✅ Working web app at localhost:8000 - Create project → instant table update

## Phase 2: AI Backlog Agent MVP

**Date**: Latest
**Status**: ✅ Complete

**Goal**: Add AI-powered backlog generation - Enter project summary → AI generates Epics/Stories/Sprints

**Files Created**:
- backend/agents/__init__.py
- backend/agents/backlog_agent.py - AI backlog generation (OpenAI or mock)
- backend/models/__init__.py
- backend/models/schemas.py - Data models (Epic, Story, BacklogResponse)
- prompt-log/phase2-prompt.md - Phase 2 documentation

**Database Updates**:
- Added Epics table (id, project_id, title, stories, total_story_points, sprint, created_at)

**Files Updated**:
- backend/main.py - Added backlog endpoints and updated HTML UI
- Database schema extended with Epics table

**New Endpoints**:
- POST /generate-backlog/{project_id} - Generate backlog using AI agent
- GET /projects/{project_id}/backlog - Get generated backlog
- GET /projects/{project_id} - Get single project

**UI Features**:
- "Generate Backlog" button per project
- "View Backlog" button per project
- Modal dialog with loading spinner
- Beautiful backlog table: Epic | Stories | Story Points | Sprint
- Timeline estimate display

**Result**: ✅ AI generates 3 Epics, 10+ Stories with Fibonacci story points, 3 Sprints, timeline estimate
