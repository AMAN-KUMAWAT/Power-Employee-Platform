import os
import json
import sys
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.schemas import Epic, Story, BacklogResponse

# Check if OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def extract_keywords(summary: str, epic_theme: str) -> List[str]:
    """Extract relevant keywords from summary for stories"""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', summary.lower())
    
    # Theme-specific keyword matching
    theme_keywords = {
        'auth': ['login', 'register', 'user', 'account', 'security', 'authentication'],
        'product': ['product', 'catalog', 'search', 'browse', 'item', 'inventory'],
        'cart': ['cart', 'checkout', 'payment', 'order', 'buy', 'purchase'],
        'data': ['data', 'database', 'api', 'integration', 'sync', 'storage'],
        'ui': ['interface', 'design', 'ui', 'ux', 'layout', 'responsive'],
        'mobile': ['mobile', 'app', 'ios', 'android', 'native'],
        'ai': ['ai', 'machine', 'learning', 'model', 'prediction', 'neural'],
        'chat': ['chat', 'bot', 'conversation', 'message', 'support']
    }
    
    for theme, keywords in theme_keywords.items():
        if theme in epic_theme.lower():
            relevant = [w.capitalize() for w in words if any(kw in w for kw in keywords)]
            if relevant:
                return relevant[:4]
    
    # Fallback: generic stories based on common words
    common_words = ['feature', 'system', 'functionality', 'module', 'component']
    found = [w.capitalize() for w in words if any(cw in w for cw in common_words)]
    if found:
        return found[:3]
    
    # Ultimate fallback
    return ["Core implementation", "Testing & validation", "Documentation"]

def smart_generate_backlog(project_summary: str) -> BacklogResponse:
    """AI-powered backlog generation - WORKS FOR ANY PROJECT SUMMARY"""
    
    # SMART KEYWORD ANALYSIS (No OpenAI needed)
    summary_lower = project_summary.lower()
    
    # Dynamic epic detection based on project type
    epic_templates = {
        # E-commerce keywords
        r"ecommerce|shop|store|cart|payment|product|buy|purchase|order|checkout": [
            "User Authentication & Security",
            "Product Catalog & Search", 
            "Shopping Cart & Checkout",
            "Order Management & Admin"
        ],
        # Mobile app keywords
        r"mobile|app|ios|android|native|phone": [
            "Onboarding & User Flow",
            "Core Features & Navigation",
            "User Profile & Settings",
            "Push Notifications & Analytics"
        ],
        # Web app keywords
        r"web|website|dashboard|portal|browser": [
            "User Interface & Navigation",
            "Core Business Logic", 
            "Data Management & APIs",
            "Admin Panel & Reporting"
        ],
        # AI/ML keywords
        r"ai|ml|machine learning|prediction|neural|model|training": [
            "Data Pipeline & Processing",
            "Model Training & Deployment",
            "API & Integration Layer",
            "Monitoring & Retraining"
        ],
        # Chatbot keywords
        r"chat|bot|chatbot|conversation|message|support|assistant": [
            "Conversation Engine & NLP",
            "Integration & APIs",
            "User Interface & UX",
            "Analytics & Monitoring"
        ],
        # Fitness/health keywords
        r"fitness|health|workout|exercise|tracker|monitor": [
            "User Onboarding & Profile",
            "Tracking & Analytics",
            "Social Features & Sharing",
            "Notifications & Reminders"
        ],
        # Default for any project
        "default": [
            "Core Functionality",
            "Integration & APIs", 
            "User Interface & UX",
            "Testing & Deployment"
        ]
    }
    
    # Find matching epic template
    epic_names = ["Core Functionality", "Integration & APIs", "User Interface & UX", "Testing & Deployment"]
    for pattern, names in epic_templates.items():
        if pattern != "default" and re.search(pattern, summary_lower):
            epic_names = names
            break
    
    # Generate epics dynamically
    epics = []
    story_fibonacci = [1, 2, 3, 5, 8, 13]
    
    for i, epic_name in enumerate(epic_names[:4]):
        # Dynamic stories based on epic name + summary keywords
        base_stories = extract_keywords(project_summary, epic_name)
        
        # Generate story titles with points
        story_titles = []
        for j, story_keyword in enumerate(base_stories[:3]):
            story_title = f"{story_keyword} implementation"
            points = story_fibonacci[min(j, len(story_fibonacci) - 1)]
            story_titles.append({"title": story_title, "story_points": points})
        
        # Add one more generic story
        story_titles.append({"title": f"{epic_name} additional features", "story_points": 5})
        
        # Calculate total points
        points = sum(s["story_points"] for s in story_titles)
        sprint = i + 1
        
        # Create Story objects
        stories = [Story(**s) for s in story_titles]
        
        # Create Epic (note: project_id is not needed here, will be set later)
        epics.append(Epic(
            title=epic_name,
            stories=stories,
            total_story_points=points,
            sprint=sprint,
            project_id=0  # Will be set by the caller
        ))
    
    # Timeline calculation
    total_points = sum(e.total_story_points for e in epics)
    velocity = 21  # points per sprint (team of 3-5)
    sprints = max(3, (total_points // velocity) + 1)
    weeks = sprints * 2  # 2 weeks per sprint
    
    return BacklogResponse(
        epics=epics,
        total_story_points=total_points,
        estimated_sprints=sprints,
        timeline_estimate=f"{weeks} weeks ({sprints} sprints × 2 weeks each, {velocity} pts/sprint)"
    )

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
            sprint=epic_data["sprint"],
            project_id=None  # Will be set when saving
        ))
    
    return BacklogResponse(
        epics=epics,
        total_story_points=total_points,
        estimated_sprints=3,
        timeline_estimate=f"{3 * 2} weeks (3 sprints × 2 weeks each)"
    )

def generate_backlog(project_summary: str) -> BacklogResponse:
    """
    Generate backlog using smart AI parser (keyword analysis) or OpenAI API
    Input: project summary text
    Output: BacklogResponse with Epics, Stories, Story Points, Sprints
    """
    
    # Always use smart parser for now (works for any summary)
    # Can upgrade to OpenAI API later if needed
    try:
        return smart_generate_backlog(project_summary)
    except Exception as e:
        print(f"Error generating backlog: {e}")
        # Fallback to mock
        return mock_generate_backlog(project_summary)
