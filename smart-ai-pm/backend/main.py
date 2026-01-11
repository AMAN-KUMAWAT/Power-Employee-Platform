from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
from database.db import get_db, Project

app = FastAPI()

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ProjectCreate(BaseModel):
    name: str
    summary: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    summary: str
    created_at: str

    class Config:
        from_attributes = True


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return HTMLResponse(content="<h1>Static files not found</h1>", status_code=404)


@app.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    db_project = Project(name=project.name, summary=project.summary)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return ProjectResponse(
        id=db_project.id,
        name=db_project.name,
        summary=db_project.summary,
        created_at=db_project.created_at.isoformat() if db_project.created_at else ""
    )


@app.get("/projects", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    projects = db.query(Project).all()
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            summary=project.summary,
            created_at=project.created_at.isoformat() if project.created_at else ""
        )
        for project in projects
    ]
