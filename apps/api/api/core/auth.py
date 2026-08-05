from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from .config import settings

security = HTTPBearer()

def _clean_env_value(value: str) -> str:
    """
    Defensively normalize a value that may have come through a loader that doesn't
    parse .env quoting the way pydantic-settings/python-dotenv does - notably
    `docker run --env-file`, which passes values through verbatim (no surrounding-quote
    stripping, no backslash-escape interpretation). Native runs (uvicorn via
    pydantic-settings) already get this right and pass through unchanged here.
    """
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return value

def _normalize_private_key(raw: str) -> str:
    """PEM keys need real newlines; strip stray quotes and expand literal `\\n`."""
    key = _clean_env_value(raw)
    if "\n" not in key and "\\n" in key:
        key = key.replace("\\n", "\n")
    return key

def build_service_account_dict() -> dict:
    """Assemble the Firebase service-account dict from individual env vars."""
    return {
        "type": _clean_env_value(settings.FIREBASE_TYPE),
        "project_id": _clean_env_value(settings.FIREBASE_PROJECT_ID),
        "private_key_id": _clean_env_value(settings.FIREBASE_PRIVATE_KEY_ID),
        "private_key": _normalize_private_key(settings.FIREBASE_PRIVATE_KEY),
        "client_email": _clean_env_value(settings.FIREBASE_CLIENT_EMAIL),
        "client_id": _clean_env_value(settings.FIREBASE_CLIENT_ID),
        "auth_uri": _clean_env_value(settings.FIREBASE_AUTH_URI),
        "token_uri": _clean_env_value(settings.FIREBASE_TOKEN_URI),
        "auth_provider_x509_cert_url": _clean_env_value(settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL),
        "client_x509_cert_url": _clean_env_value(settings.FIREBASE_CLIENT_X509_CERT_URL),
        "universe_domain": _clean_env_value(settings.FIREBASE_UNIVERSE_DOMAIN),
    }

def ensure_firebase_initialized() -> None:
    """
    Lazily initialize the Firebase Admin SDK on first use, mirroring FirestoreDB's
    lazy client pattern (db/firestore.py). Doing this eagerly at import time meant the
    entire app - including /health, which has nothing to do with auth - crashed on
    startup whenever the credentials were missing or invalid.

    Credentials come from individual FIREBASE_* env vars (see config.py), not a JSON
    key file on disk - no service-account file needs to exist anywhere in the repo or
    the deployed container.
    """
    if firebase_admin._apps:
        return

    if not settings.FIREBASE_PROJECT_ID or not settings.FIREBASE_PRIVATE_KEY or not settings.FIREBASE_CLIENT_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: FIREBASE_PROJECT_ID / FIREBASE_PRIVATE_KEY / "
                   "FIREBASE_CLIENT_EMAIL are not set."
        )

    try:
        cred = credentials.Certificate(build_service_account_dict())
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'flourish-de908.firebasestorage.app'
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server misconfiguration: could not initialize Firebase Admin ({e})"
        )

async def verify_firebase_token(auth_credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify a Firebase ID token (sent as `Authorization: Bearer <token>`) and return
    the caller's uid. The frontend must fetch a fresh token per request - see
    apps/web/src/integrations/api.ts.
    """
    ensure_firebase_initialized()

    try:
        decoded_token = auth.verify_id_token(auth_credentials.credentials)
        return decoded_token['uid']
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
