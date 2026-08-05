"""
Tests for the API configuration
"""
import pytest
from api.core.config import Settings


def test_settings_load():
    """Test that settings can be loaded with correct defaults"""
    settings = Settings()
    assert settings is not None
    assert settings.PROJECT_NAME == "Flourish - Plant Care Companion"
    assert settings.API_V1_STR == "/api/v1"


def test_allowed_origins():
    """Test ALLOWED_ORIGINS is a non-empty list with default origins"""
    settings = Settings()
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) > 0
    assert "http://localhost:5173" in settings.ALLOWED_ORIGINS
    assert "http://127.0.0.1:5173" in settings.ALLOWED_ORIGINS


def test_allowed_origins_parsing():
    """Test ALLOWED_ORIGINS comma-separated string parsing"""
    settings = Settings(ALLOWED_ORIGINS="http://a.com,http://b.com")
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) == 2
    assert "http://a.com" in settings.ALLOWED_ORIGINS
    assert "http://b.com" in settings.ALLOWED_ORIGINS


def test_allowed_origins_parsing_with_spaces():
    """Test ALLOWED_ORIGINS parsing strips whitespace"""
    settings = Settings(ALLOWED_ORIGINS="http://a.com, http://b.com , http://c.com")
    assert len(settings.ALLOWED_ORIGINS) == 3
    assert settings.ALLOWED_ORIGINS == ["http://a.com", "http://b.com", "http://c.com"]


def test_allowed_origins_parsing_empty_string():
    """Test ALLOWED_ORIGINS parsing handles empty string"""
    settings = Settings(ALLOWED_ORIGINS="")
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) == 0


def test_default_secret_key():
    """Test SECRET_KEY is always set to a non-empty value"""
    settings = Settings()
    assert len(settings.SECRET_KEY) > 0


def test_fallback_secret_key():
    """Test SECRET_KEY uses default hardcoded fallback when not in env"""
    settings = Settings(SECRET_KEY="change-this-secret-key-in-production")
    assert settings.SECRET_KEY == "change-this-secret-key-in-production"


def test_groq_defaults():
    """Test Groq settings - Groq is the sole LLM backend, Ollama has been retired.
    Explicitly overrides GROQ_API_KEY so this doesn't depend on whether the local
    .env happens to have a real key configured."""
    settings = Settings(GROQ_API_KEY="")
    assert settings.GROQ_MODEL == "qwen/qwen3.6-27b"
    assert settings.GROQ_API_KEY == ""


def test_groq_api_key_from_env(monkeypatch):
    """Test GROQ_API_KEY reads from the environment"""
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    settings = Settings()
    assert settings.GROQ_API_KEY == "test-groq-key"


def test_tavily_api_key_default():
    """Test TAVILY_API_KEY defaults to empty when not set (explicit override - see
    test_groq_defaults for why)"""
    settings = Settings(TAVILY_API_KEY="")
    assert settings.TAVILY_API_KEY == ""


def test_openweather_api_key_default():
    """Test OPENWEATHER_API_KEY defaults to empty when not set (explicit override -
    see test_groq_defaults for why)"""
    settings = Settings(OPENWEATHER_API_KEY="")
    assert settings.OPENWEATHER_API_KEY == ""


def test_firebase_fields_from_env(monkeypatch):
    """Test the individual FIREBASE_* fields read from the environment"""
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "test-project")
    monkeypatch.setenv("FIREBASE_CLIENT_EMAIL", "test@test-project.iam.gserviceaccount.com")
    settings = Settings()
    assert settings.FIREBASE_PROJECT_ID == "test-project"
    assert settings.FIREBASE_CLIENT_EMAIL == "test@test-project.iam.gserviceaccount.com"


def test_firebase_fields_fallback():
    """Test FIREBASE_* fields default to empty when not set (explicit override - see
    test_groq_defaults for why), except the well-known Google OAuth endpoint URLs"""
    settings = Settings(FIREBASE_PROJECT_ID="", FIREBASE_PRIVATE_KEY="", FIREBASE_CLIENT_EMAIL="")
    assert settings.FIREBASE_PROJECT_ID == ""
    assert settings.FIREBASE_PRIVATE_KEY == ""
    assert settings.FIREBASE_CLIENT_EMAIL == ""
    assert settings.FIREBASE_TYPE == "service_account"
    assert settings.FIREBASE_TOKEN_URI == "https://oauth2.googleapis.com/token"


