import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;padding:0;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);background-size:400% 400%;animation:gradient 15s ease infinite;min-height:100vh;position:relative;overflow-x:hidden;}
    @keyframes gradient{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
    .bg-particles{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;}
    .particle{position:absolute;width:4px;height:4px;background:rgba(255,255,255,0.5);border-radius:50%;animation:float 20s infinite linear;}
    @keyframes float{0%{transform:translateY(100vh) translateX(0);opacity:0;}10%{opacity:1;}90%{opacity:1;}100%{transform:translateY(-100vh) translateX(100px);opacity:0;}}
    .container{max-width:1400px;margin:0 auto;padding:40px 20px;position:relative;z-index:1;}
    .header{text-align:center;color:white;margin-bottom:50px;padding:30px;background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:20px;box-shadow:0 8px 32px rgba(0,0,0,0.1);animation:fadeInDown 0.8s ease;}
    @keyframes fadeInDown{from{opacity:0;transform:translateY(-30px);}to{opacity:1;transform:translateY(0);}}
    .header h1{font-size:3.5rem;margin-bottom:15px;text-shadow:2px 2px 4px rgba(0,0,0,0.3);background:linear-gradient(45deg,#fff,#f0f0f0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .header p{font-size:1.3rem;opacity:0.95;margin-top:10px;}
    .header-icon{font-size:4rem;display:block;margin-bottom:10px;animation:bounce 2s infinite;}
    @keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
    .card{background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);border-radius:20px;padding:35px;margin-bottom:30px;box-shadow:0 20px 60px rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.3);animation:fadeInUp 0.8s ease;transition:transform 0.3s ease,box-shadow 0.3s ease;}
    .card:hover{transform:translateY(-5px);box-shadow:0 25px 70px rgba(0,0,0,0.4);}
    @keyframes fadeInUp{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
    .card h2{color:#333;font-size:2rem;margin-bottom:25px;display:flex;align-items:center;gap:10px;}
    .card h2::before{content:'✨';font-size:1.5rem;}
    input,textarea{width:100%;padding:15px;margin:12px 0;box-sizing:border-box;border:2px solid #e0e0e0;border-radius:12px;font-size:1rem;transition:all 0.3s ease;background:#fff;color:#333;font-family:inherit;}
    input:focus,textarea:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 4px rgba(102,126,234,0.1);transform:scale(1.02);color:#333;}
    input::placeholder,textarea::placeholder{color:#999;opacity:1;}
    button{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px 30px;border:none;cursor:pointer;font-size:1rem;font-weight:600;border-radius:12px;margin:8px 5px;box-shadow:0 4px 15px rgba(102,126,234,0.4);transition:all 0.3s ease;position:relative;overflow:hidden;}
    button::before{content:'';position:absolute;top:50%;left:50%;width:0;height:0;border-radius:50%;background:rgba(255,255,255,0.3);transform:translate(-50%,-50%);transition:width 0.6s,height 0.6s;}
    button:hover::before{width:300px;height:300px;}
    button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(102,126,234,0.6);}
    button:active{transform:translateY(0);}
    .btn-sm{padding:10px 18px;font-size:0.9rem;}
    .btn-success{background:linear-gradient(135deg,#28a745 0%,#20c997 100%);box-shadow:0 4px 15px rgba(40,167,69,0.4);}
    .btn-success:hover{box-shadow:0 6px 20px rgba(40,167,69,0.6);}
    table{width:100%;border-collapse:separate;border-spacing:0;margin-top:25px;background:white;border-radius:15px;overflow:hidden;box-shadow:0 4px 15px rgba(0,0,0,0.1);}
    th,td{border:none;padding:18px;text-align:left;}
    th{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;font-weight:600;font-size:1rem;text-transform:uppercase;letter-spacing:0.5px;}
    td{background:#fff;border-bottom:1px solid #f0f0f0;}
    tr:last-child td{border-bottom:none;}
    tr:hover td{background:#f8f9ff;transform:scale(1.01);transition:all 0.2s ease;}
    .modal{display:none;position:fixed;z-index:2000;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.7);backdrop-filter:blur(5px);animation:fadeIn 0.3s ease;}
    @keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
    .modal-content{background:white;margin:3% auto;padding:35px;border-radius:25px;width:95%;max-width:1100px;max-height:85vh;overflow-y:auto;box-shadow:0 30px 80px rgba(0,0,0,0.5);animation:slideIn 0.4s ease;position:relative;}
    @keyframes slideIn{from{opacity:0;transform:translateY(-50px) scale(0.9);}to{opacity:1;transform:translateY(0) scale(1);}}
    .close{color:#aaa;float:right;font-size:35px;font-weight:bold;cursor:pointer;transition:all 0.3s ease;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;}
    .close:hover{color:#000;background:#f0f0f0;transform:rotate(90deg);}
    .spinner{display:inline-block;width:50px;height:50px;border:5px solid #f3f3f3;border-top:5px solid #667eea;border-radius:50%;animation:spin 1s linear infinite;margin:20px auto;}
    @keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
    .backlog-table{margin-top:25px;background:white;border-radius:15px;overflow:hidden;}
    .backlog-table th{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;font-size:1.1rem;padding:20px;}
    .timeline{background:linear-gradient(135deg,#e7f3ff 0%,#f0f8ff 100%);padding:25px;border-radius:15px;margin:25px 0;border-left:6px solid #667eea;box-shadow:0 4px 15px rgba(102,126,234,0.2);font-size:1.1rem;}
    .story-list{list-style:none;padding:0;margin:8px 0;}
    .story-item{padding:10px 0;border-bottom:2px solid #f0f0f0;transition:all 0.2s ease;padding-left:25px;position:relative;}
    .story-item::before{content:'📌';position:absolute;left:0;top:10px;}
    .story-item:hover{background:#f8f9ff;padding-left:30px;border-left:4px solid #667eea;}
    .story-item:last-child{border-bottom:none;}
    .icon-large{font-size:3rem;margin:10px;}
    .action-buttons{display:flex;gap:10px;flex-wrap:wrap;}
    .pulse{animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.5;}}
    .loading-text{font-size:1.2rem;color:#667eea;font-weight:600;margin-top:15px;}
    @media(max-width:768px){.header h1{font-size:2rem;}.card{padding:20px;}.action-buttons{flex-direction:column;width:100%;}button{width:100%;margin:5px 0;}}
    </style>
    </head>
    <body>
    <div class="bg-particles" id="particles"></div>
    <div class="container">
    <div class="header">
        <span class="header-icon">🚀</span>
        <h1>Smart AI PM Tool</h1>
        <p>✨ AI-Powered Project Management & Backlog Generation ✨</p>
        <p style="font-size:1rem;margin-top:15px;opacity:0.9;">Transform your project ideas into structured Agile backlogs instantly</p>
    </div>
    
    <div class="card">
    <h2><span>✨</span>Create New Project</h2>
    <form id="projectForm">
        <input type="text" id="name" placeholder="🎯 Enter Project Name" required>
        <textarea id="summary" placeholder="📝 Describe your project... Our AI will generate Epics, Stories, and Sprints automatically!" rows="5" required></textarea>
        <button type="submit">✨ Create Project</button>
    </form>
    </div>
    
    <div class="card">
    <h2><span>📁</span>Your Projects</h2>
    <table id="projectsTable">
        <thead><tr><th>#</th><th>📁 Name</th><th>📄 Summary</th><th>📅 Created</th><th>⚡ Actions</th></tr></thead>
        <tbody></tbody>
    </table>
    </div>
    </div>
    
    <div id="backlogModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeBacklogModal()">&times;</span>
        <h2 id="modalProjectName" style="margin-bottom:25px;color:#333;display:flex;align-items:center;gap:10px;"><span class="icon-large">📋</span><span>Backlog</span></h2>
        <div id="backlogLoading" style="text-align:center;padding:40px;">
            <div class="spinner"></div>
            <div class="loading-text pulse">🤖 AI is generating your backlog...</div>
            <p style="color:#666;margin-top:15px;">Creating Epics, Stories, and Sprint assignments</p>
        </div>
        <div id="backlogContent" style="display:none;">
            <div class="timeline" id="timelineEstimate"></div>
            <table class="backlog-table">
                <thead><tr><th>🎯 Epic</th><th>📝 Stories</th><th>📊 Points</th><th>🏃 Sprint</th></tr></thead>
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
    
    function createParticles() {
        const particlesContainer = document.getElementById('particles');
        for(let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (15 + Math.random() * 10) + 's';
            particlesContainer.appendChild(particle);
        }
    }
    
    createParticles();

    async function loadProjects() {
        const res = await fetch('/projects');
        const projects = await res.json();
        const tbody = document.querySelector('#projectsTable tbody');
        if(projects.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:40px;color:#999;"><div style="font-size:3rem;margin-bottom:15px;">📭</div><p>No projects yet. Create your first project above!</p></td></tr>';
            return;
        }
        tbody.innerHTML = projects.map(p => 
            `<tr>
                <td><strong style="color:#667eea;font-size:1.2rem;">${p.id}</strong></td>
                <td><strong style="font-size:1.1rem;color:#333;">${escapeHtml(p.name)}</strong></td>
                <td style="max-width:400px;">${escapeHtml(p.summary)}</td>
                <td>${new Date(p.created_at).toLocaleString()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-sm btn-success" onclick="generateBacklog(${p.id}, '${escapeHtml(p.name).replace(/'/g, "\\'")}')">
                            ✨ Generate Backlog
                        </button>
                        <button class="btn-sm" onclick="viewBacklog(${p.id}, '${escapeHtml(p.name).replace(/'/g, "\\'")}')">
                            📋 View Backlog
                        </button>
                    </div>
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
            '<div style="display:flex;flex-wrap:wrap;gap:20px;align-items:center;">' +
            '<div><strong>⏱ Timeline:</strong> ' + (backlog.timeline_estimate || 'N/A') + '</div>' +
            '<div><strong>📊 Story Points:</strong> <span style="color:#667eea;font-size:1.2rem;">' + (backlog.total_story_points || 0) + '</span></div>' +
            '<div><strong>🏃 Sprints:</strong> <span style="color:#764ba2;font-size:1.2rem;">' + (backlog.estimated_sprints || 0) + '</span></div>' +
            '</div>';
        
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
