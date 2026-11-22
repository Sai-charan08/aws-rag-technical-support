import re
from typing import Optional, Tuple, Dict, Any
import bcrypt

from config.settings import settings
from src.database.mysql_db import DatabaseManager, get_db_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    """Authentication and User Security Service using bcrypt password hashing."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or get_db_manager()
        self.create_demo_users_if_not_exist()

    @staticmethod
    def hash_password(password: str) -> str:
        """Securely hashes plaintext password with bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verifies a plaintext password against a stored bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def register_user(
        self, username: str, email: str, password: str, role: str = "user"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validates input, securely hashes credentials, and stores user in MySQL database."""
        username = username.strip().lower()
        email = email.strip().lower()

        # Input validations
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long.", None
        if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores.", None

        if not email or "@" not in email or "." not in email:
            return False, "Please provide a valid email address.", None

        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long.", None

        # Check existing user
        if self.db.get_user_by_username(username):
            return False, f"Username '{username}' is already taken.", None
        if self.db.get_user_by_email(email):
            return False, f"Email '{email}' is already registered.", None

        # Hash and persist
        password_hash = self.hash_password(password)
        user = self.db.create_user(username=username, email=email, password_hash=password_hash, role=role)

        if user:
            logger.info(f"New user successfully registered: {username} ({email}) [Role: {role}]")
            self.db.log_audit_event(user_id=user["id"], event_type="REGISTER", details=f"User registered with role {role}")
            return True, "Registration successful! You can now log in.", user
        else:
            return False, "Failed to create user account in database.", None

    def login_user(
        self, username_or_email: str, password: str, ip_address: Optional[str] = "127.0.0.1"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticates user credentials and logs access event."""
        identifier = username_or_email.strip().lower()

        user = self.db.get_user_by_username(identifier)
        if not user:
            user = self.db.get_user_by_email(identifier)

        if not user:
            logger.warning(f"Failed login attempt for unknown user: '{identifier}'")
            self.db.log_audit_event(
                user_id=None, event_type="LOGIN_FAILED", details=f"Unknown identifier: {identifier}", ip_address=ip_address
            )
            return False, "Invalid username or password.", None

        if not self.verify_password(password, user["password_hash"]):
            logger.warning(f"Failed login attempt for user: '{identifier}' (incorrect password)")
            self.db.log_audit_event(
                user_id=user["id"], event_type="LOGIN_FAILED", details="Incorrect password attempt", ip_address=ip_address
            )
            return False, "Invalid username or password.", None

        # Successful login
        self.db.update_last_login(user["id"])
        self.db.log_audit_event(
            user_id=user["id"], event_type="LOGIN_SUCCESS", details="Successful login authentication", ip_address=ip_address
        )
        logger.info(f"User successfully logged in: {user['username']} [ID: {user['id']}]")
        return True, "Login successful!", user

    def create_demo_users_if_not_exist(self):
        """Initializes default demo user and administrator accounts if absent."""
        try:
            if not self.db.get_user_by_username("demouser"):
                self.register_user(
                    username="demouser",
                    email="demo@awssupport.internal",
                    password="DemoUser123!",
                    role="user"
                )
            if not self.db.get_user_by_username("admin"):
                self.register_user(
                    username="admin",
                    email="admin@awssupport.internal",
                    password="AdminRoot123!",
                    role="admin"
                )
        except Exception as e:
            logger.error(f"Error seeding demo users: {e}")

_global_auth_service = None

def get_auth_service() -> AuthService:
    global _global_auth_service
    if _global_auth_service is None:
        _global_auth_service = AuthService()
    return _global_auth_service

