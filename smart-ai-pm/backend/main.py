import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Add root to path

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime
from agents.backlog_agent import generate_backlog

# Get project root directory (parent of backend/)
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_PATH = DB_DIR / "smart_pm.db"

# Inline DB (no external imports needed)
def init_db():
    """Initialize database - creates data directory and tables if needed"""
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, summary TEXT, created_at TEXT)''')
    # Epics table
    c.execute('''CREATE TABLE IF NOT EXISTS epics 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER,
                  title TEXT,
                  stories TEXT,
                  total_story_points INTEGER,
                  sprint INTEGER,
                  created_at TEXT,
                  FOREIGN KEY (project_id) REFERENCES projects(id))''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with correct path"""
    DB_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(str(DB_PATH))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

class Project(BaseModel):
    name: str
    summary: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>Smart AI PM Tool 🚀</title>
    <style>body{font-family:Arial,sans-serif;padding:20px;max-width:1200px;margin:auto;background:#f5f5f5;}
    .card{background:white;border-radius:8px;padding:20px;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}
    input,textarea{width:100%;padding:10px;margin:10px 0;box-sizing:border-box;border:1px solid #ddd;border-radius:4px;}
    button{background:#007bff;color:white;padding:10px 20px;border:none;cursor:pointer;font-size:14px;border-radius:4px;margin:5px;}
    button:hover{background:#0056b3;}
    .btn-sm{padding:5px 10px;font-size:12px;}
    .btn-success{background:#28a745;}
    .btn-success:hover{background:#218838;}
    table{width:100%;border-collapse:collapse;margin-top:20px;}
    th,td{border:1px solid #ddd;padding:12px;text-align:left;}
    th{background:#f4f4f4;font-weight:600;}
    tr:hover{background:#f9f9f9;}
    .modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.5);}
    .modal-content{background:white;margin:5% auto;padding:20px;border-radius:8px;width:90%;max-width:1000px;max-height:80vh;overflow-y:auto;}
    .close{color:#aaa;float:right;font-size:28px;font-weight:bold;cursor:pointer;}
    .close:hover{color:#000;}
    .spinner{display:inline-block;width:20px;height:20px;border:3px solid #f3f3f3;border-top:3px solid #007bff;border-radius:50%;animation:spin 1s linear infinite;margin-right:10px;}
    @keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
    .backlog-table{margin-top:20px;}
    .backlog-table th{background:#667eea;color:white;}
    .timeline{background:#e7f3ff;padding:15px;border-radius:4px;margin:20px 0;border-left:4px solid #007bff;}
    .story-list{list-style:none;padding:0;margin:5px 0;}
    .story-item{padding:5px 0;border-bottom:1px solid #eee;}
    .story-item:last-child{border-bottom:none;}
    </style>
    </head>
    <body>
    <h1>🚀 Smart AI PM Tool - Phase 2: AI Backlog Agent</h1>
    
    <div class="card">
    <h2>Create New Project</h2>
    <form id="projectForm">
        <input type="text" id="name" placeholder="Project Name" required>
        <textarea id="summary" placeholder="Project Summary (used for AI backlog generation)..." rows="4" required></textarea>
        <button type="submit">Create Project</button>
    </form>
    </div>
    
    <div class="card">
    <h2>Projects</h2>
    <table id="projectsTable">
        <thead><tr><th>ID</th><th>Name</th><th>Summary</th><th>Created</th><th>Actions</th></tr></thead>
        <tbody></tbody>
    </table>
    </div>
    
    <div id="backlogModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeBacklogModal()">&times;</span>
        <h2 id="modalProjectName">Backlog</h2>
        <div id="backlogLoading" style="text-align:center;padding:20px;">
            <div class="spinner"></div> Generating backlog...
        </div>
        <div id="backlogContent" style="display:none;">
            <div class="timeline" id="timelineEstimate"></div>
            <table class="backlog-table">
                <thead><tr><th>Epic</th><th>Stories</th><th>Story Points</th><th>Sprint</th></tr></thead>
                <tbody id="backlogTableBody"></tbody>
            </table>
        </div>
    </div>
    </div>

    <script>
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async function loadProjects() {
        const res = await fetch('/projects');
        const projects = await res.json();
        const tbody = document.querySelector('#projectsTable tbody');
        tbody.innerHTML = projects.map(p => 
            `<tr>
                <td>${p.id}</td>
                <td><strong>${escapeHtml(p.name)}</strong></td>
                <td>${escapeHtml(p.summary)}</td>
                <td>${new Date(p.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn-sm btn-success" onclick="generateBacklog(${p.id}, '${escapeHtml(p.name).replace(/'/g, "\\'")}')">
                        ✨ Generate Backlog
                    </button>
                    <button class="btn-sm" onclick="viewBacklog(${p.id}, '${escapeHtml(p.name).replace(/'/g, "\\'")}')">
                        📋 View Backlog
                    </button>
                </td>
            </tr>`
        ).join('');
    }

    async function generateBacklog(projectId, projectName) {
        document.getElementById('modalProjectName').textContent = projectName + ' - Generating Backlog...';
        document.getElementById('backlogModal').style.display = 'block';
        document.getElementById('backlogLoading').style.display = 'block';
        document.getElementById('backlogContent').style.display = 'none';
        
        try {
            const res = await fetch('/generate-backlog/' + projectId, {method: 'POST'});
            const backlog = await res.json();
            displayBacklog(backlog, projectName);
        } catch (error) {
            console.error('Error generating backlog:', error);
            document.getElementById('backlogLoading').innerHTML = '<p style="color:red;">Error generating backlog. Please try again.</p>';
        }
    }

    async function viewBacklog(projectId, projectName) {
        document.getElementById('modalProjectName').textContent = projectName + ' - Backlog';
        document.getElementById('backlogModal').style.display = 'block';
        document.getElementById('backlogLoading').style.display = 'block';
        document.getElementById('backlogContent').style.display = 'none';
        
        try {
            const res = await fetch('/projects/' + projectId + '/backlog');
            const backlog = await res.json();
            displayBacklog(backlog, projectName);
        } catch (error) {
            console.error('Error loading backlog:', error);
            document.getElementById('backlogLoading').innerHTML = '<p>No backlog generated yet. Click "Generate Backlog" to create one.</p>';
        }
    }

    function displayBacklog(backlog, projectName) {
        document.getElementById('backlogLoading').style.display = 'none';
        document.getElementById('backlogContent').style.display = 'block';
        document.getElementById('modalProjectName').textContent = projectName + ' - Backlog';
        
        document.getElementById('timelineEstimate').innerHTML = 
            '<strong>⏱ Timeline Estimate:</strong> ' + (backlog.timeline_estimate || 'N/A') + ' | ' +
            '<strong>📊 Total Story Points:</strong> ' + (backlog.total_story_points || 0) + ' | ' +
            '<strong>🏃 Sprints:</strong> ' + (backlog.estimated_sprints || 0);
        
        const tbody = document.getElementById('backlogTableBody');
        tbody.innerHTML = backlog.epics.map(epic => {
            const storiesHtml = epic.stories.map(s => 
                '<li class="story-item">' + escapeHtml(s.title) + ' <span style="color:#666;">(' + s.story_points + ' pts)</span></li>'
            ).join('');
            return '<tr>' +
                '<td><strong>' + escapeHtml(epic.title) + '</strong></td>' +
                '<td><ul class="story-list">' + storiesHtml + '</ul></td>' +
                '<td><strong>' + epic.total_story_points + '</strong></td>' +
                '<td><strong>Sprint ' + epic.sprint + '</strong></td>' +
                '</tr>';
        }).join('');
    }

    function closeBacklogModal() {
        document.getElementById('backlogModal').style.display = 'none';
    }

    document.getElementById('projectForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const summary = document.getElementById('summary').value;
        
        await fetch('/projects', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, summary})
        });
        loadProjects();
        e.target.reset();
    });

    window.onclick = function(event) {
        const modal = document.getElementById('backlogModal');
        if (event.target == modal) {
            closeBacklogModal();
        }
    }

    loadProjects();
    </script>
    </body>
    </html>
    """)

@app.post("/projects")
async def create_project(project: Project):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO projects (name, summary, created_at) VALUES (?, ?, ?)",
              (project.name, project.summary, datetime.now().isoformat()))
    conn.commit()
    project_id = c.lastrowid
    conn.close()
    return {"id": project_id, "message": "Project created!"}

@app.get("/projects")
async def list_projects():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = [{"id": row[0], "name": row[1], "summary": row[2], "created_at": row[3]} 
                for row in c.fetchall()]
    conn.close()
    return projects

@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": row[0], "name": row[1], "summary": row[2], "created_at": row[3]}

@app.post("/generate-backlog/{project_id}")
async def generate_project_backlog(project_id: int):
    """Generate backlog for a project using AI agent"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT summary FROM projects WHERE id = ?", (project_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_summary = row[0]
    
    # Generate backlog using agent
    backlog_response = generate_backlog(project_summary)
    
    # Save epics to database
    for epic in backlog_response.epics:
        stories_json = json.dumps([{"title": s.title, "story_points": s.story_points, "description": s.description} 
                                   for s in epic.stories])
        c.execute('''INSERT INTO epics (project_id, title, stories, total_story_points, sprint, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (project_id, epic.title, stories_json, epic.total_story_points, 
                   epic.sprint, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return backlog_response.dict()

@app.get("/projects/{project_id}/backlog")
async def get_project_backlog(project_id: int):
    """Get generated backlog for a project"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if project exists
    c.execute("SELECT summary FROM projects WHERE id = ?", (project_id,))
    project = c.fetchone()
    if not project:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get epics
    c.execute("SELECT * FROM epics WHERE project_id = ? ORDER BY sprint, id", (project_id,))
    epics_rows = c.fetchall()
    conn.close()
    
    epics = []
    total_points = 0
    
    for row in epics_rows:
        epic_id, proj_id, title, stories_json, story_points, sprint, created_at = row
        stories = json.loads(stories_json) if stories_json else []
        epics.append({
            "id": epic_id,
            "project_id": proj_id,
            "title": title,
            "stories": stories,
            "total_story_points": story_points,
            "sprint": sprint,
            "created_at": created_at
        })
        total_points += story_points
    
    sprints = max([e["sprint"] for e in epics], default=0)
    timeline = f"{sprints * 2} weeks ({sprints} sprints × 2 weeks each)" if sprints > 0 else "Not estimated"
    
    return {
        "epics": epics,
        "total_story_points": total_points,
        "estimated_sprints": sprints,
        "timeline_estimate": timeline
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
