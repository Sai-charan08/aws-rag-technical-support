import pytest
from config.settings import settings
from src.generation.llm import LLMClient
from src.models.intent_classifier import get_intent_classifier
from src.database.mysql_db import get_db_manager
from src.auth.auth_service import get_auth_service

def test_settings_initialization():
    assert settings.PROJECT_NAME == "AWS Technical Support RAG Assistant"
    assert "Amazon EC2" in settings.SUPPORTED_SERVICES
    assert settings.TOP_K >= 1
    assert settings.MYSQL_PORT in (3306, 3307)
    assert settings.MYSQL_DATABASE == "aws_support_rag"

def test_llm_client_demo_fallback():
    client = LLMClient(provider="openai", openai_api_key="")
    assert client.provider == "demo"

def test_system_core_singletons():
    db = get_db_manager()
    assert db is not None
    auth = get_auth_service()
    assert auth is not None
    classifier = get_intent_classifier()
    assert classifier is not None
