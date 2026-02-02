from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..db.firestore import FirestoreDB
from ..core.auth import verify_firebase_token

router = APIRouter()

class ProfileCreate(BaseModel):
    email: str
    display_name: str = ""
    photo_url: str = ""

@router.post("/profile")
async def create_or_get_profile(
    profile_data: ProfileCreate,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Create user profile on first sign in or return existing profile
    """
    print("="*60)
    print("🔐 PROFILE CREATION REQUEST")
    print("="*60)
    print(f"👤 User ID: {user_id}")
    print(f"📧 Email: {profile_data.email}")
    print(f"👤 Display Name: {profile_data.display_name}")
    print(f"🖼️  Photo URL: {profile_data.photo_url}")
    print("="*60)
    
    profile = await FirestoreDB.get_or_create_profile(
        user_id=user_id,
        email=profile_data.email,
        display_name=profile_data.display_name,
        photo_url=profile_data.photo_url
    )
    
    print("✅ PROFILE RESULT:")
    print(f"📊 Profile: {profile}")
    print("="*60)
    
    return profile

@router.get("/profile")
async def get_profile(user_id: str = Depends(verify_firebase_token)):
    """Get current user's profile"""
    profile = await FirestoreDB.get_profile(user_id)
    if not profile:
        return {
            "id": user_id,
            "total_score": 0,
            "level": 1,
            "tasks_completed": 0,
            "streak_days": 0,
            "achievements": []
        }
    return profile
