import pytest
from config.settings import settings
from src.generation.llm import LLMClient

def test_settings_initialization():
    assert settings.PROJECT_NAME == "AWS Technical Support RAG Assistant"
    assert "Amazon EC2" in settings.SUPPORTED_SERVICES
    assert settings.TOP_K >= 1

def test_llm_client_demo_fallback():
    client = LLMClient(provider="openai", openai_api_key="")
    assert client.provider == "demo"
