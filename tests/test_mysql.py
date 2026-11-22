import pytest
from src.database.mysql_db import DatabaseManager

@pytest.fixture(scope="module")
def temp_db(tmp_path_factory):
    tmp_file = str(tmp_path_factory.mktemp("db_test") / "test_db.sqlite")
    return DatabaseManager(
        host="invalid_host_to_force_fallback",
        database="test_db",
        fallback_sqlite=True,
        sqlite_path=tmp_file
    )

def test_db_manager_initialization(temp_db):
    stats = temp_db.get_stats()
    assert "engine" in stats
    assert "total_users" in stats
    assert "total_queries" in stats

def test_add_and_retrieve_chat_history(temp_db):
    user = temp_db.create_user(
        username="dbuser1",
        email="dbuser1@test.internal",
        password_hash="mock_hash",
        role="user"
    )
    assert user is not None
    user_id = user["id"]

    entry_id = temp_db.add_chat_entry(
        user_id=user_id,
        query="How to fix NoSuchBucket?",
        response="Troubleshooting steps for S3...",
        intent="TROUBLESHOOTING",
        service="Amazon S3",
        urgency="HIGH",
        is_grounded=True,
        latency_ms=45.2,
        sources=[{"title": "S3 Guide", "source": "s3.md"}]
    )
    assert entry_id is not None

    history = temp_db.get_chat_history(user_id=user_id)
    assert len(history) == 1
    assert history[0]["query"] == "How to fix NoSuchBucket?"
    assert history[0]["service"] == "Amazon S3"
    assert history[0]["intent"] == "TROUBLESHOOTING"
    assert len(history[0]["sources"]) == 1

def test_clear_chat_history(temp_db):
    user = temp_db.get_user_by_username("dbuser1")
    assert user is not None
    temp_db.clear_chat_history(user_id=user["id"])
    history = temp_db.get_chat_history(user_id=user["id"])
    assert len(history) == 0

def test_audit_logging(temp_db):
    temp_db.log_audit_event(
        user_id=1,
        event_type="TEST_EVENT",
        details="Unit test audit entry",
        ip_address="192.168.1.1"
    )
    logs = temp_db.get_audit_logs(limit=10)
    assert len(logs) > 0
    assert any(log["event_type"] == "TEST_EVENT" for log in logs)

