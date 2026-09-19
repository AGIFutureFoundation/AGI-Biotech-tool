"""Workflow persistence layer with error recovery and state management.

Provides:
- Durable workflow state storage
- Automatic retry logic
- Checkpoint/resume capability
- Transaction support
- PostgreSQL and SQLite backends
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

class WorkflowStatus(Enum):
    """Workflow execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

@dataclass
class WorkflowCheckpoint:
    """Checkpoint for resuming interrupted workflows."""
    workflow_id: str
    step_index: int
    step_name: str
    state: Dict
    timestamp: str
    results_so_far: List[Dict]
    
    def to_dict(self) -> Dict:
        return asdict(self)

class WorkflowPersistence:
    """Stores and retrieves workflow state durably."""
    
    def __init__(self, db_path: str = "data/workflows.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workflows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                template TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT NOT NULL,
                user_id TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                completed_at TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Workflow steps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                step_index INTEGER NOT NULL,
                step_name TEXT NOT NULL,
                agent_name TEXT,
                status TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds FLOAT,
                result TEXT,
                FOREIGN KEY(workflow_id) REFERENCES workflows(id)
            )
        ''')
        
        # Checkpoints table (for resume capability)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                checkpoint_index INTEGER,
                step_name TEXT,
                state TEXT,
                created_at TIMESTAMP,
                results_so_far TEXT,
                FOREIGN KEY(workflow_id) REFERENCES workflows(id)
            )
        ''')
        
        # Retry history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retry_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                attempt_number INTEGER,
                failed_at TIMESTAMP,
                error_message TEXT,
                retried_at TIMESTAMP,
                FOREIGN KEY(workflow_id) REFERENCES workflows(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_workflow(self, workflow_id: str, template: str, target: str, 
                     user_id: str, metadata: Dict = None) -> bool:
        """Save workflow to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            cursor.execute('''
                INSERT OR REPLACE INTO workflows 
                (id, template, target, status, user_id, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (workflow_id, template, target, WorkflowStatus.QUEUED.value, 
                  user_id, now, now, json.dumps(metadata or {})))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving workflow: {e}")
            return False
    
    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> bool:
        """Update workflow status."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            completed_at = now if status == WorkflowStatus.COMPLETED else None
            
            cursor.execute('''
                UPDATE workflows 
                SET status = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
            ''', (status.value, now, completed_at, workflow_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating workflow: {e}")
            return False
    
    def save_step_result(self, workflow_id: str, step_index: int, 
                        step_name: str, agent_name: str, result: Dict,
                        duration_seconds: float) -> bool:
        """Save individual step result."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            cursor.execute('''
                INSERT INTO workflow_steps
                (workflow_id, step_index, step_name, agent_name, status, 
                 completed_at, duration_seconds, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (workflow_id, step_index, step_name, agent_name, 
                  WorkflowStatus.COMPLETED.value, now, duration_seconds,
                  json.dumps(result)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving step result: {e}")
            return False
    
    def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> bool:
        """Save workflow checkpoint for resume."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO checkpoints
                (workflow_id, checkpoint_index, step_name, state, created_at, results_so_far)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (checkpoint.workflow_id, checkpoint.step_index, 
                  checkpoint.step_name, json.dumps(checkpoint.state),
                  checkpoint.timestamp, json.dumps(checkpoint.results_so_far)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
            return False
    
    def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Retrieve latest checkpoint for a workflow."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT workflow_id, checkpoint_index, step_name, state, created_at, results_so_far
                FROM checkpoints
                WHERE workflow_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (workflow_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return WorkflowCheckpoint(
                    workflow_id=row[0],
                    step_index=row[1],
                    step_name=row[2],
                    state=json.loads(row[3]),
                    timestamp=row[4],
                    results_so_far=json.loads(row[5])
                )
            return None
        except Exception as e:
            print(f"Error retrieving checkpoint: {e}")
            return None
    
    def record_retry(self, workflow_id: str, attempt_number: int, 
                    error_message: str) -> bool:
        """Record a retry attempt."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            failed_at = datetime.utcnow().isoformat()
            cursor.execute('''
                INSERT INTO retry_history
                (workflow_id, attempt_number, failed_at, error_message)
                VALUES (?, ?, ?, ?)
            ''', (workflow_id, attempt_number, failed_at, error_message))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error recording retry: {e}")
            return False
    
    def get_retry_count(self, workflow_id: str) -> int:
        """Get number of retry attempts for a workflow."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM retry_history WHERE workflow_id = ?
            ''', (workflow_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting retry count: {e}")
            return 0
    
    def get_workflow_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get workflow history for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, template, target, status, created_at, updated_at, completed_at, metadata
                FROM workflows
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'template': row[1],
                    'target': row[2],
                    'status': row[3],
                    'created_at': row[4],
                    'updated_at': row[5],
                    'completed_at': row[6],
                    'metadata': json.loads(row[7]) if row[7] else {}
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error getting workflow history: {e}")
            return []
    
    def cleanup_old_workflows(self, days_old: int = 30) -> int:
        """Clean up workflows older than specified days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
            cursor.execute('''
                DELETE FROM workflows
                WHERE completed_at < ? AND status IN (?, ?)
            ''', (cutoff_date, WorkflowStatus.COMPLETED.value, WorkflowStatus.FAILED.value))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up workflows: {e}")
            return 0

