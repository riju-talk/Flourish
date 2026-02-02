import os
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from .config import settings

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    # Use the path from settings, or construct the full path
    service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_KEY
    if not os.path.isabs(service_account_path):
        # If relative path, make it relative to the api directory
        service_account_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            service_account_path
        )
    
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'flourish-de908.firebasestorage.app'
    })

security = HTTPBearer()

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify Firebase authentication token and return user ID
    """
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
