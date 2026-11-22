import pytest
from src.auth.auth_service import AuthService
from src.database.mysql_db import DatabaseManager

@pytest.fixture(scope="module")
def temp_auth_service(tmp_path_factory):
    tmp_db_file = str(tmp_path_factory.mktemp("auth_test") / "test_auth.sqlite")
    db = DatabaseManager(
        host="invalid_host_to_force_fallback",
        database="test_db",
        fallback_sqlite=True,
        sqlite_path=tmp_db_file
    )
    return AuthService(db_manager=db)

def test_password_hashing_and_verification():
    raw_pass = "SecurePass123!"
    hashed = AuthService.hash_password(raw_pass)
    assert hashed != raw_pass
    assert AuthService.verify_password(raw_pass, hashed) is True
    assert AuthService.verify_password("WrongPassword!", hashed) is False

def test_user_registration(temp_auth_service):
    auth = temp_auth_service
    success, msg, user = auth.register_user(
        username="testengineer",
        email="engineer@example.com",
        password="MySecretPassword123!",
        role="user"
    )
    assert success is True
    assert user is not None
    assert user["username"] == "testengineer"
    assert user["email"] == "engineer@example.com"
    assert user["role"] == "user"

def test_duplicate_registration_fails(temp_auth_service):
    auth = temp_auth_service
    success, msg, user = auth.register_user(
        username="testengineer",
        email="different@example.com",
        password="Password123!"
    )
    assert success is False
    assert "already taken" in msg

def test_user_login_success(temp_auth_service):
    auth = temp_auth_service
    success, msg, user = auth.login_user(
        username_or_email="testengineer",
        password="MySecretPassword123!"
    )
    assert success is True
    assert user["username"] == "testengineer"

def test_user_login_invalid_password(temp_auth_service):
    auth = temp_auth_service
    success, msg, user = auth.login_user(
        username_or_email="testengineer",
        password="IncorrectPassword!"
    )
    assert success is False
    assert user is None

def test_user_login_by_email(temp_auth_service):
    auth = temp_auth_service
    success, msg, user = auth.login_user(
        username_or_email="engineer@example.com",
        password="MySecretPassword123!"
    )
    assert success is True
    assert user["username"] == "testengineer"

