"""
Sample test for the API configuration
"""
import pytest
from api.core.config import Settings


def test_settings_load():
    """Test that settings can be loaded"""
    settings = Settings()
    assert settings is not None
    assert settings.PROJECT_NAME == "Flourish API"


def test_allowed_origins():
    """Test ALLOWED_ORIGINS parsing"""
    settings = Settings()
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) > 0
