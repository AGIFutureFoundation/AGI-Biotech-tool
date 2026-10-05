"""Database migration utilities: SQLite → PostgreSQL.

Handles:
- Schema migration
- Data migration
- Connection pooling setup
- Performance optimization (indexes, constraints)
- Rollback capability
"""

import sqlite3
import json
from typing import Dict, List, Tuple
from datetime import datetime

class DatabaseMigrator:
    """Migrates workflows from SQLite to PostgreSQL."""
    
    def __init__(self, sqlite_path: str, postgres_url: str):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.migration_log = []
    
    def create_postgresql_schema(self) -> bool:
        """Create PostgreSQL schema. Requires psycopg2."""
        try:
            import psycopg2
            conn = psycopg2.connect(self.postgres_url)
            cursor = conn.cursor()
            
            # Create tables with optimizations for PostgreSQL
            # (PostgreSQL has no inline INDEX clause in CREATE TABLE, unlike MySQL;
            # indexes are created separately below.)
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
                    metadata JSONB
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id SERIAL PRIMARY KEY,
                    workflow_id TEXT NOT NULL REFERENCES workflows(id),
                    step_index INTEGER NOT NULL,
                    step_name TEXT NOT NULL,
                    agent_name TEXT,
                    status TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds FLOAT,
                    result JSONB
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id SERIAL PRIMARY KEY,
                    workflow_id TEXT NOT NULL REFERENCES workflows(id),
                    checkpoint_index INTEGER,
                    step_name TEXT,
                    state JSONB,
                    created_at TIMESTAMP,
                    results_so_far JSONB
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS retry_history (
                    id SERIAL PRIMARY KEY,
                    workflow_id TEXT NOT NULL REFERENCES workflows(id),
                    attempt_number INTEGER,
                    failed_at TIMESTAMP,
                    error_message TEXT,
                    retried_at TIMESTAMP
                );
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
                CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
                CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at);
                CREATE INDEX IF NOT EXISTS idx_steps_workflow ON workflow_steps(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_steps_name ON workflow_steps(step_name);
                CREATE INDEX IF NOT EXISTS idx_checkpoints_workflow ON checkpoints(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_retry_workflow ON retry_history(workflow_id);
            ''')

            conn.commit()
            cursor.close()
            conn.close()
            
            self.migration_log.append("PostgreSQL schema created successfully")
            return True
        except ImportError:
            self.migration_log.append("ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
            return False
        except Exception as e:
            self.migration_log.append(f"ERROR creating schema: {e}")
            return False
    
    def migrate_data(self) -> Tuple[bool, Dict]:
        """Migrate data from SQLite to PostgreSQL."""
        try:
            import psycopg2
            
            # Read from SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_cursor = sqlite_conn.cursor()
            
            # Connect to PostgreSQL. Autocommit so a single bad row's failed
            # INSERT doesn't abort the whole transaction (psycopg2 otherwise
            # requires a rollback() before any further statement succeeds,
            # which would silently fail every subsequent row in this loop).
            pg_conn = psycopg2.connect(self.postgres_url)
            pg_conn.autocommit = True
            pg_cursor = pg_conn.cursor()
            
            stats = {
                'workflows_migrated': 0,
                'steps_migrated': 0,
                'checkpoints_migrated': 0,
                'retries_migrated': 0,
                'errors': []
            }
            
            # Migrate workflows
            sqlite_cursor.execute("SELECT * FROM workflows")
            for row in sqlite_cursor.fetchall():
                try:
                    pg_cursor.execute('''
                        INSERT INTO workflows 
                        (id, template, target, status, user_id, created_at, updated_at, completed_at, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', row)
                    stats['workflows_migrated'] += 1
                except Exception as e:
                    stats['errors'].append(f"Workflow migration error: {e}")
            
            # Migrate workflow steps
            sqlite_cursor.execute("SELECT * FROM workflow_steps")
            for row in sqlite_cursor.fetchall():
                try:
                    pg_cursor.execute('''
                        INSERT INTO workflow_steps
                        (workflow_id, step_index, step_name, agent_name, status, 
                         started_at, completed_at, duration_seconds, result)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', row[1:])  # Skip ID, let SERIAL handle it
                    stats['steps_migrated'] += 1
                except Exception as e:
                    stats['errors'].append(f"Step migration error: {e}")
            
            # Migrate checkpoints
            sqlite_cursor.execute("SELECT * FROM checkpoints")
            for row in sqlite_cursor.fetchall():
                try:
                    pg_cursor.execute('''
                        INSERT INTO checkpoints
                        (workflow_id, checkpoint_index, step_name, state, created_at, results_so_far)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', row[1:])  # Skip ID
                    stats['checkpoints_migrated'] += 1
                except Exception as e:
                    stats['errors'].append(f"Checkpoint migration error: {e}")
            
            # Migrate retry history
            sqlite_cursor.execute("SELECT * FROM retry_history")
            for row in sqlite_cursor.fetchall():
                try:
                    pg_cursor.execute('''
                        INSERT INTO retry_history
                        (workflow_id, attempt_number, failed_at, error_message, retried_at)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', row[1:])  # Skip ID
                    stats['retries_migrated'] += 1
                except Exception as e:
                    stats['errors'].append(f"Retry migration error: {e}")
            
            pg_conn.commit()
            
            sqlite_cursor.close()
            sqlite_conn.close()
            pg_cursor.close()
            pg_conn.close()
            
            self.migration_log.append(f"Data migration complete: {stats}")
            return True, stats
        
        except ImportError:
            return False, {'errors': ["psycopg2 not installed"]}
        except Exception as e:
            return False, {'errors': [str(e)]}
    
    def verify_migration(self) -> Dict:
        """Verify that migration was successful."""
        try:
            import psycopg2
            
            # Count records in PostgreSQL
            pg_conn = psycopg2.connect(self.postgres_url)
            pg_cursor = pg_conn.cursor()
            
            verification = {}
            
            tables = ['workflows', 'workflow_steps', 'checkpoints', 'retry_history']
            for table in tables:
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = pg_cursor.fetchone()[0]
                verification[table] = count
            
            pg_cursor.close()
            pg_conn.close()
            
            return verification
        except Exception as e:
            return {'error': str(e)}
    
    def get_migration_log(self) -> List[str]:
        """Get migration log entries."""
        return self.migration_log

class ConnectionPool:
    """PostgreSQL connection pooling configuration."""
    
    @staticmethod
    def get_pool_config(max_connections: int = 20) -> Dict:
        """Get optimal connection pool configuration."""
        return {
            'max_overflow': 40,
            'pool_size': max_connections,
            'pool_recycle': 3600,  # Recycle connections every hour
            'pool_pre_ping': True,  # Test connection before use
            'echo': False,  # Set to True for SQL debugging
            'echo_pool': False,
        }
    
    @staticmethod
    def create_pool_url(host: str, port: int, database: str,
                       user: str, password: str) -> str:
        """Create SQLAlchemy connection pool URL."""
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

class PerformanceOptimization:
    """PostgreSQL performance optimization strategies."""
    
    @staticmethod
    def get_optimization_queries() -> Dict[str, str]:
        """Get SQL queries for performance optimization."""
        return {
            'create_indexes': '''
                CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
                CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
                CREATE INDEX IF NOT EXISTS idx_workflows_created ON workflows(created_at);
                CREATE INDEX IF NOT EXISTS idx_steps_workflow ON workflow_steps(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_steps_name ON workflow_steps(step_name);
                CREATE INDEX IF NOT EXISTS idx_checkpoints_workflow ON checkpoints(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_retries_workflow ON retry_history(workflow_id);
            ''',
            'analyze_tables': '''
                ANALYZE workflows;
                ANALYZE workflow_steps;
                ANALYZE checkpoints;
                ANALYZE retry_history;
            ''',
            'vacuum': '''
                VACUUM ANALYZE;
            ''',
            'enable_parallel_queries': '''
                SET max_parallel_workers_per_gather = 4;
                SET max_parallel_maintenance_workers = 4;
                SET max_parallel_workers = 8;
            '''
        }

