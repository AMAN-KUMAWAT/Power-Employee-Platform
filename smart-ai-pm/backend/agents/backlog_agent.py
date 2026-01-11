import os
import json
import sys
from pathlib import Path
from typing import List, Dict

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.schemas import Epic, Story, BacklogResponse

# Check if OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def mock_generate_backlog(project_summary: str) -> BacklogResponse:
    """Mock backlog generation when OpenAI API key is not available"""
    
    # Generate 3 mock epics with stories
    epics_data = [
        {
            "title": "User Authentication & Management",
            "stories": [
                {"title": "User registration system", "story_points": 5},
                {"title": "Login/logout functionality", "story_points": 3},
                {"title": "Password reset flow", "story_points": 5},
                {"title": "Profile management", "story_points": 3},
            ],
            "sprint": 1
        },
        {
            "title": "Core Features & Functionality",
            "stories": [
                {"title": "Main feature implementation", "story_points": 8},
                {"title": "Data validation and processing", "story_points": 5},
                {"title": "Search and filter capabilities", "story_points": 5},
                {"title": "Export functionality", "story_points": 3},
            ],
            "sprint": 2
        },
        {
            "title": "UI/UX & Integration",
            "stories": [
                {"title": "Responsive design improvements", "story_points": 5},
                {"title": "API integration", "story_points": 8},
                {"title": "Error handling and feedback", "story_points": 3},
            ],
            "sprint": 3
        }
    ]
    
    epics = []
    total_points = 0
    
    for epic_data in epics_data:
        stories = [Story(**s) for s in epic_data["stories"]]
        epic_points = sum(s.story_points for s in stories)
        total_points += epic_points
        
        epics.append(Epic(
            title=epic_data["title"],
            stories=stories,
            total_story_points=epic_points,
            sprint=epic_data["sprint"]
        ))
    
    return BacklogResponse(
        epics=epics,
        total_story_points=total_points,
        estimated_sprints=3,
        timeline_estimate=f"{3 * 2} weeks (3 sprints × 2 weeks each)"
    )

def generate_backlog(project_summary: str) -> BacklogResponse:
    """
    Generate backlog using OpenAI API or fallback to mock
    Input: project summary text
    Output: BacklogResponse with Epics, Stories, Story Points, Sprints
    """
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-xxx":
        # Use mock generation if no API key
        return mock_generate_backlog(project_summary)
    
    try:
        # TODO: Implement OpenAI API call when key is available
        # For now, use mock
        return mock_generate_backlog(project_summary)
    except Exception as e:
        print(f"Error generating backlog with AI: {e}")
        # Fallback to mock
        return mock_generate_backlog(project_summary)
