"""Project and workspace management for biodao.blockchain.

Each project owns:
- Multiple targets (proteins to dock against)
- Compound library (subset of global library)
- Docking campaigns and results
- MD simulations and trajectories
- Team members with roles
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class Project:
    """Represents a research project."""
    def __init__(self, project_id: str, name: str, owner_id: str, program: str,
                 description: str = '', status: str = 'active', created_at: str = None):
        self.project_id = project_id
        self.name = name
        self.owner_id = owner_id
        self.program = program  # 'ALS', 'Parkinson's', 'Shriners', etc.
        self.description = description
        self.status = status  # active, archived, completed
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.members = [owner_id]  # user IDs with access
        self.targets = []  # list of target IDs
        self.campaigns = []  # list of screening campaign IDs
        self.milestones = []  # list of milestones

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'name': self.name,
            'owner_id': self.owner_id,
            'program': self.program,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'members': self.members,
            'targets': self.targets,
            'campaigns': self.campaigns,
            'milestones': self.milestones,
        }

    def add_member(self, user_id: str):
        """Add a team member to the project."""
        if user_id not in self.members:
            self.members.append(user_id)

    def add_target(self, target_id: str):
        """Add a target to the project."""
        if target_id not in self.targets:
            self.targets.append(target_id)

class ScreeningCampaign:
    """Represents a docking/screening campaign."""
    def __init__(self, campaign_id: str, project_id: str, name: str, target_id: str,
                 compound_count: int = 0, status: str = 'queued', created_at: str = None):
        self.campaign_id = campaign_id
        self.project_id = project_id
        self.name = name
        self.target_id = target_id
        self.compound_count = compound_count
        self.status = status  # queued, running, complete, failed
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.started_at = None
        self.completed_at = None
        self.results = []  # list of {compound_id, score, poses}
        self.progress = 0  # 0-100%

    def to_dict(self):
        return {
            'campaign_id': self.campaign_id,
            'project_id': self.project_id,
            'name': self.name,
            'target_id': self.target_id,
            'compound_count': self.compound_count,
            'status': self.status,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'progress': self.progress,
            'results': self.results[:10],  # Return top 10 for preview
        }

class Milestone:
    """Represents a project milestone."""
    def __init__(self, milestone_id: str, project_id: str, name: str, due_date: str,
                 description: str = '', status: str = 'pending'):
        self.milestone_id = milestone_id
        self.project_id = project_id
        self.name = name
        self.due_date = due_date
        self.description = description
        self.status = status  # pending, in_progress, completed, overdue

    def to_dict(self):
        return {
            'milestone_id': self.milestone_id,
            'project_id': self.project_id,
            'name': self.name,
            'due_date': self.due_date,
            'description': self.description,
            'status': self.status,
        }

# Mock database (replace with PostgreSQL)
PROJECTS_DB = {}
CAMPAIGNS_DB = {}

def create_project(name: str, owner_id: str, program: str, description: str = '') -> Project:
    """Create a new project."""
    project_id = str(uuid.uuid4())[:8]
    project = Project(project_id, name, owner_id, program, description)
    PROJECTS_DB[project_id] = project
    return project

def get_project(project_id: str) -> Optional[Project]:
    """Fetch a project by ID."""
    return PROJECTS_DB.get(project_id)

def list_user_projects(user_id: str) -> List[Project]:
    """List all projects accessible to a user."""
    return [p for p in PROJECTS_DB.values() if user_id in p.members]

def create_campaign(project_id: str, name: str, target_id: str, 
                   compound_count: int = 0) -> ScreeningCampaign:
    """Create a new screening campaign."""
    campaign_id = str(uuid.uuid4())[:8]
    campaign = ScreeningCampaign(campaign_id, project_id, name, target_id, compound_count)
    CAMPAIGNS_DB[campaign_id] = campaign
    return campaign

def get_campaign(campaign_id: str) -> Optional[ScreeningCampaign]:
    """Fetch a campaign by ID."""
    return CAMPAIGNS_DB.get(campaign_id)

def update_campaign_progress(campaign_id: str, completed: int, total: int):
    """Update campaign progress."""
    campaign = CAMPAIGNS_DB.get(campaign_id)
    if campaign:
        campaign.progress = int(100 * completed / max(total, 1))
        if completed == total:
            campaign.status = 'complete'
            campaign.completed_at = datetime.utcnow().isoformat()
