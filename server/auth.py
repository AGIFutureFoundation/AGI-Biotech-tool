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
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional

SECRET_KEY = os.getenv('JWT_SECRET')
if not SECRET_KEY:
    if os.getenv('FLASK_ENV') == 'production' or os.getenv('ENV') == 'production':
        raise RuntimeError('JWT_SECRET must be set in production; refusing to start with no secret.')
    SECRET_KEY = 'dev-secret-change-in-production'
ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24

PBKDF2_ITERATIONS = 390_000

def _hash_password(password: str, salt: bytes = None) -> str:
    """PBKDF2-HMAC-SHA256 password hash, stored as 'salt_hex$hash_hex'."""
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"

def _verify_password(password: str, stored: str) -> bool:
    if not stored or '$' not in stored:
        return False
    salt_hex, _ = stored.split('$', 1)
    candidate = _hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(candidate, stored)

class User:
    """Represents a researcher or lab member."""
    def __init__(self, user_id: str, email: str, name: str, role: str = 'researcher',
                 institution: str = '', created_at: str = None, password_hash: str = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.role = role  # admin, pi, researcher, viewer
        self.institution = institution
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.password_hash = password_hash

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

# In-memory user store (replace with a real database). No accounts ship with a usable password; call
# create_user() with an explicit password to make one.
USERS_DB: Dict[str, User] = {}

def create_user(email: str, name: str, password: str, role: str = 'researcher',
                 institution: str = '') -> User:
    """Create a new user account with a hashed password."""
    user_id = f"user_{hashlib.sha256(email.encode()).hexdigest()[:16]}"
    user = User(user_id, email, name, role, institution, password_hash=_hash_password(password))
    USERS_DB[user_id] = user
    return user

def get_user(user_id: str) -> Optional[User]:
    """Fetch a user by ID."""
    return USERS_DB.get(user_id)

def authenticate_user(email: str, password: str) -> Optional[str]:
    """Authenticate a user by email + password and return a signed token, or None."""
    for user in USERS_DB.values():
        if user.email == email and _verify_password(password, user.password_hash):
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
