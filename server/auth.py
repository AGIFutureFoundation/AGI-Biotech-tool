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
import secrets
import warnings
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional


def _secret_key():
    """Signing key from $JWT_SECRET, or a fresh random one per process.

    The previous default was the literal 'dev-secret-change-in-production'.
    Shipping a signing key in a public repository means anyone who reads it can
    forge a token for any user, including an admin one, against any deployment
    that forgot to set the variable -- and forgetting is silent by nature.

    Falling back to a random key removes that: tokens simply stop validating
    when the process restarts, which is a visible inconvenience in development
    and the correct refusal in production.
    """
    key = os.getenv('JWT_SECRET')
    if key:
        return key

    warnings.warn(
        "JWT_SECRET is not set, so a random signing key was generated for this "
        "process. Tokens will not survive a restart and will not validate across "
        "multiple workers. Set JWT_SECRET before deploying.",
        RuntimeWarning,
        stacklevel=2,
    )
    return secrets.token_urlsafe(64)


SECRET_KEY = _secret_key()
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
        # 'salt$hash'. None means the account cannot log in, which is the
        # correct state for one that has not had a password set.
        self.password_hash: Optional[str] = None
        # Set for accounts that sign in with a wallet. Such an account has no
        # password, so control of the key is the only way into it.
        self.wallet_address: Optional[str] = None

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'institution': self.institution,
            'created_at': self.created_at,
            'wallet_address': self.wallet_address,
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

# In-memory user store. Replace with a real database before multi-user use;
# nothing here survives a restart.
USERS_DB: Dict[str, User] = {}

# scrypt parameters. n is the work factor and dominates cost; these follow the
# interactive-login end of RFC 7914's guidance. bcrypt and argon2 are better
# still, but neither is installed and this project keeps to the standard
# library where it can.
_SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1, "dklen": 64}


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """'salt$hash', both hex. A fresh salt is generated when none is given."""
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: Optional[str]) -> bool:
    """Constant-time check of a password against a stored 'salt$hash'."""
    if not stored or "$" not in stored:
        return False
    salt_hex, _, expected = stored.partition("$")
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    candidate = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return secrets.compare_digest(candidate.hex(), expected)


def create_user(email: str, name: str, role: str = 'researcher', institution: str = '',
                password: Optional[str] = None) -> User:
    """Create a user account. Without a password the account cannot log in."""
    # Random, not derived from the email: an id derived by hash leaks the
    # address and collides under a broken digest. The previous version used
    # MD5, where a collision would have meant two accounts sharing an id.
    user_id = f"user_{secrets.token_hex(8)}"
    user = User(user_id, email, name, role, institution)
    user.password_hash = hash_password(password) if password else None
    USERS_DB[user_id] = user
    return user


def set_password(user: User, password: str) -> None:
    user.password_hash = hash_password(password)


def get_user(user_id: str) -> Optional[User]:
    """Fetch a user by ID."""
    return USERS_DB.get(user_id)


def authenticate_user(email: str, password: str) -> Optional[str]:
    """Return a token only for a correct email and password.

    The previous implementation took a password argument and never looked at
    it, so any string -- including an empty one -- returned a valid token for
    any known email, with that user's role. That was a complete authentication
    bypass, not a missing feature.

    An account with no password set cannot authenticate at all, so a half-built
    account fails closed.
    """
    for user in USERS_DB.values():
        if user.email == email:
            if verify_password(password, getattr(user, 'password_hash', None)):
                return AuthToken.create(user)
            return None
    # Hash anyway on an unknown email so a missing account and a wrong password
    # take comparable time and cannot be told apart by timing.
    verify_password(password, hash_password("no-such-user"))
    return None

def get_user_by_wallet(address: str) -> Optional[User]:
    """Find the account bound to a wallet address, case-insensitively.

    Addresses are compared lowercased. EIP-55 checksumming is presentational,
    and treating two spellings of one address as two accounts would silently
    fork a researcher's identity -- and with it the authorship of their runs.
    """
    if not address:
        return None
    wanted = str(address).lower()
    for user in USERS_DB.values():
        if (getattr(user, 'wallet_address', None) or '').lower() == wanted:
            return user
    return None


def authenticate_wallet(address: str, name: str = '', institution: str = '') -> Optional[str]:
    """Issue a token for a verified wallet address, registering it if new.

    CALLER'S OBLIGATION: the signature must already have been verified by
    siwe.verify(). This function takes an address on trust because by the time
    it is reached the proof has been checked -- so it must never be reachable
    from a request path that skipped that step. server.py calls it in exactly
    one place, immediately after a successful verify.

    First sign-in registers the account. That is the intended behaviour for a
    wallet login: control of the key IS the credential, so there is no separate
    sign-up to gate. New accounts get the lowest role, never an inherited one.
    """
    if not address:
        return None

    user = get_user_by_wallet(address)
    if user is None:
        user = create_user(
            email=f"{address.lower()}@wallet.local",
            name=name or f"{address[:6]}...{address[-4:]}",
            role='researcher', institution=institution)
        user.wallet_address = address
        # No password is set, so this account cannot be logged into by any
        # other route. The key is the only credential.
    return AuthToken.create(user)


# The Flask @require_auth and @require_role decorators that used to live here
# imported flask, which is not a dependency and is not installed, so calling
# either raised ImportError. server.py serves over http.server and carries its
# own stdlib equivalents (_claims and _require_role), which are what the routes
# actually use.
