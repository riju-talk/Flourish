"""
Tests for Firebase credential handling in core/auth.py - in particular the
normalization that makes it robust to loaders that don't parse .env quoting the way
pydantic-settings/python-dotenv does (e.g. `docker run --env-file`, which passes
values through verbatim: no surrounding-quote stripping, no `\n` escape expansion).
"""
from api.core.auth import _clean_env_value, _normalize_private_key, build_service_account_dict


def test_clean_env_value_strips_surrounding_quotes():
    assert _clean_env_value('"service_account"') == "service_account"


def test_clean_env_value_passes_through_unquoted():
    assert _clean_env_value("service_account") == "service_account"


def test_clean_env_value_strips_whitespace():
    assert _clean_env_value("  service_account  ") == "service_account"


def test_normalize_private_key_expands_literal_backslash_n():
    """Simulates docker --env-file, which leaves literal \\n as two characters."""
    raw = '"-----BEGIN PRIVATE KEY-----\\nABCD\\n-----END PRIVATE KEY-----\\n"'
    normalized = _normalize_private_key(raw)
    assert "\\n" not in normalized
    assert "\n" in normalized
    assert normalized.startswith("-----BEGIN PRIVATE KEY-----\n")
    assert normalized.endswith("-----END PRIVATE KEY-----\n")


def test_normalize_private_key_passes_through_real_newlines():
    """Simulates the native path, where pydantic-settings already converted \\n to
    real newlines - must not be double-processed. (Trailing whitespace is stripped,
    which PEM parsers don't care about.)"""
    raw = "-----BEGIN PRIVATE KEY-----\nABCD\n-----END PRIVATE KEY-----\n"
    assert _normalize_private_key(raw) == raw.strip()


def test_build_service_account_dict_shape(monkeypatch):
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_TYPE", '"service_account"')
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_PROJECT_ID", '"test-project"')
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_PRIVATE_KEY_ID", "abc123")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_PRIVATE_KEY", '"-----BEGIN PRIVATE KEY-----\\nABCD\\n-----END PRIVATE KEY-----\\n"')
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_CLIENT_EMAIL", "test@test-project.iam.gserviceaccount.com")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_CLIENT_ID", "123")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_CLIENT_X509_CERT_URL", "https://example.com/cert")
    monkeypatch.setattr("api.core.auth.settings.FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")

    result = build_service_account_dict()

    assert result["type"] == "service_account"
    assert result["project_id"] == "test-project"
    assert "\n" in result["private_key"]
    assert result["client_email"] == "test@test-project.iam.gserviceaccount.com"
