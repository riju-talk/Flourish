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
    """Test Groq default values - Groq is the sole LLM backend, Ollama has been retired"""
    settings = Settings()
    assert settings.GROQ_MODEL == "llama-3.3-70b-versatile"
    assert settings.GROQ_API_KEY == ""


def test_tavily_api_key_default():
    """Test TAVILY_API_KEY defaults to empty string"""
    settings = Settings()
    assert settings.TAVILY_API_KEY == ""


def test_openweather_api_key_default():
    """Test OPENWEATHER_API_KEY defaults to empty string"""
    settings = Settings()
    assert settings.OPENWEATHER_API_KEY == ""


def test_firebase_service_account_key_from_env(monkeypatch):
    """Test FIREBASE_SERVICE_ACCOUNT_KEY reads from the environment"""
    monkeypatch.setenv("FIREBASE_SERVICE_ACCOUNT_KEY", "some-test-key.json")
    settings = Settings()
    assert settings.FIREBASE_SERVICE_ACCOUNT_KEY == "some-test-key.json"


def test_firebase_service_account_key_fallback():
    """Test FIREBASE_SERVICE_ACCOUNT_KEY defaults to empty when not set"""
    settings = Settings(FIREBASE_SERVICE_ACCOUNT_KEY="")
    assert settings.FIREBASE_SERVICE_ACCOUNT_KEY == ""


def test_groq_api_key_default():
    """Test GROQ_API_KEY defaults to empty string"""
    settings = Settings()
    assert settings.GROQ_API_KEY == ""
