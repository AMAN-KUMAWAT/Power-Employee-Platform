from pydantic import BaseModel
from typing import List, Optional

class Story(BaseModel):
    title: str
    story_points: int
    description: Optional[str] = None

class Epic(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None  # Can be None during generation, set when saving
    title: str
    stories: List[Story] = []
    total_story_points: int = 0
    sprint: Optional[int] = None

class BacklogResponse(BaseModel):
    epics: List[Epic]
    total_story_points: int
    estimated_sprints: int
    timeline_estimate: str
