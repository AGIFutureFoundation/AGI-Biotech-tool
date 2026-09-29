"""User authentication and authorization for biodao.blockchain.

Supports:
- Local JWT-based auth (for self-hosted)
- Auth0 integration (for SaaS)
- GitHub OAuth (for quick onboarding)
- Role-based access control (RBAC): admin, pi, researcher, viewer
"""
import os
import secrets
import jwt
import json
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional

_env_secret = os.getenv('JWT_SECRET')
_is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('APP_ENV') == 'production'
if _env_secret:
    SECRET_KEY = _env_secret
elif _is_production:
    raise RuntimeError(
        'JWT_SECRET must be set when FLASK_ENV/APP_ENV=production. A random '
        'per-process secret is unsafe here: it would differ across worker '
        'processes and replicas, so tokens signed by one would be rejected by '
        'another.'
    )
else:
    # No hardcoded fallback: that value is public (it's in this repo's source),
    # so anyone could forge a valid token, including an admin-role one. A random
    # per-process secret invalidates tokens on restart and, under multiple
    # worker processes or replicas, means tokens signed by one are rejected by
    # another — but that's strictly better than a signing key an attacker can
    # read on GitHub. Set JWT_SECRET for a stable, multi-process deployment.
    SECRET_KEY = secrets.token_hex(32)
    print('WARNING: JWT_SECRET is not set. Using a random per-process secret; '
          'tokens will be invalidated on restart and rejected by any other '
          'worker process or replica that does not share this secret. Set the '
          'JWT_SECRET environment variable for a stable, production-safe '
          'deployment.')
ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24

class User:
    """Represents a researcher or lab member."""
    def __init__(self, user_id: str, email: str, name: str, role: str = 'researcher', 
                 institution: str = '', created_at: str = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.role = role  # admin, pi, researcher, viewer
        self.institution = institution
        self.created_at = created_at or datetime.utcnow().isoformat()

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
    def can_access_project(user: User, project_owner_id: str, project_members: List[str]) -> bool:
        """Check if a user can access a specific project."""
        if user.role == 'admin':
            return True
        if user.user_id == project_owner_id:
            return True
        if user.user_id in project_members:
            return True
        return False

# Mock database of users (replace with PostgreSQL)
USERS_DB = {
    'user_001': User('user_001', 'researcher@als.org', 'Alice Smith', 'pi', 'ALS Association'),
    'user_002': User('user_002', 'scientist@mjff.org', 'Bob Chen', 'researcher', 'MJFF'),
}

def create_user(email: str, name: str, role: str = 'researcher', institution: str = '') -> User:
    """Create a new user account."""
    user_id = f"user_{hashlib.md5(email.encode()).hexdigest()[:8]}"
    user = User(user_id, email, name, role, institution)
    USERS_DB[user_id] = user
    return user

def get_user(user_id: str) -> Optional[User]:
    """Fetch a user by ID."""
    return USERS_DB.get(user_id)

def authenticate_user(email: str, password: str) -> Optional[str]:
    """Authenticate a user and return a token.
    
    In production, use bcrypt to hash/verify passwords.
    For now, this is a stub for demo purposes.
    """
    for user in USERS_DB.values():
        if user.email == email:
            token = AuthToken.create(user)
            return token
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
