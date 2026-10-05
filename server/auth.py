"""User authentication and authorization for biodao.blockchain.

Supports:
- Local JWT-based auth (for self-hosted)
- Auth0 integration (for SaaS)
- GitHub OAuth (for quick onboarding)
- Role-based access control (RBAC): admin, pi, researcher, viewer
"""
import os
import jwt
import json
import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_env_secret = os.getenv('JWT_SECRET')
if _env_secret:
    SECRET_KEY = _env_secret
else:
    # No persistent secret configured: generate a random one for this process
    # rather than falling back to a well-known hardcoded string that would let
    # anyone forge tokens. Tokens won't survive a restart, but can't be forged.
    SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "JWT_SECRET is not set; using a random per-process secret. "
        "Set JWT_SECRET in the environment for stable sessions across restarts."
    )
ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24

PBKDF2_ITERATIONS = 200_000

def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    """Hash a password with PBKDF2-HMAC-SHA256 and a random salt."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return {'salt': salt, 'hash': digest.hex()}

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verify a password against a stored salt/hash using a constant-time comparison."""
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return hmac.compare_digest(digest.hex(), expected_hash)

class User:
    """Represents a researcher or lab member."""
    def __init__(self, user_id: str, email: str, name: str, role: str = 'researcher',
                 institution: str = '', created_at: str = None,
                 password_hash: str = None, password_salt: str = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.role = role  # admin, pi, researcher, viewer
        self.institution = institution
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.password_hash = password_hash
        self.password_salt = password_salt

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'institution': self.institution,
            'created_at': self.created_at,
        }

class AuthToken:
    """JWT token management."""
    
    @staticmethod
    def create(user: User, expires_in_hours: int = TOKEN_EXPIRE_HOURS) -> str:
        """Create a JWT token for a user."""
        payload = {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow(),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify(token: str) -> Optional[Dict]:
        """Verify and decode a JWT token."""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

class Permission:
    """Role-based access control."""
    
    ROLES = {
        'admin': {'view_all', 'edit_all', 'manage_users', 'delete_projects'},
        'pi': {'view_all', 'edit_all', 'manage_team'},
        'researcher': {'view_own', 'edit_own', 'run_jobs'},
        'viewer': {'view_own'},
    }

    @staticmethod
    def has_permission(role: str, action: str) -> bool:
        """Check if a role has permission for an action."""
        return action in Permission.ROLES.get(role, set())

    @staticmethod
    def can_access_project(role: str, user_id: str, project_owner_id: str, project_members: List[str]) -> bool:
        """Check if a user can access a specific project."""
        if role == 'admin':
            return True
        if user_id == project_owner_id:
            return True
        if user_id in project_members:
            return True
        return False

def _seed_user(user_id: str, email: str, name: str, role: str, institution: str, password: str) -> User:
    creds = hash_password(password)
    return User(user_id, email, name, role, institution,
                password_hash=creds['hash'], password_salt=creds['salt'])

# Mock database of users (replace with PostgreSQL). Seed passwords are for
# local demo use only and must not be reused in a real deployment.
USERS_DB = {
    'user_001': _seed_user('user_001', 'researcher@als.org', 'Alice Smith', 'pi',
                            'ALS Association', os.getenv('DEMO_USER_001_PASSWORD', 'demo-password-change-me')),
    'user_002': _seed_user('user_002', 'scientist@mjff.org', 'Bob Chen', 'researcher',
                            'MJFF', os.getenv('DEMO_USER_002_PASSWORD', 'demo-password-change-me')),
}

def create_user(email: str, name: str, password: str, role: str = 'researcher', institution: str = '') -> User:
    """Create a new user account with a hashed password."""
    user_id = f"user_{hashlib.md5(email.encode()).hexdigest()[:8]}"
    creds = hash_password(password)
    user = User(user_id, email, name, role, institution,
                password_hash=creds['hash'], password_salt=creds['salt'])
    USERS_DB[user_id] = user
    return user

def get_user(user_id: str) -> Optional[User]:
    """Fetch a user by ID."""
    return USERS_DB.get(user_id)

def authenticate_user(email: str, password: str) -> Optional[str]:
    """Authenticate a user by email + password and return a signed token."""
    if not email or not password:
        return None
    for user in USERS_DB.values():
        if user.email == email:
            if not user.password_hash or not verify_password(password, user.password_salt, user.password_hash):
                return None
            return AuthToken.create(user)
    return None

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, jsonify
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        payload = AuthToken.verify(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Inject user into request context
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated

def require_role(*roles):
    """Decorator to require specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import request, jsonify
            
            if not hasattr(request, 'user'):
                return jsonify({'error': 'User not authenticated'}), 401
            
            if request.user.get('role') not in roles:
                return jsonify({'error': f'Requires one of: {", ".join(roles)}'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator
