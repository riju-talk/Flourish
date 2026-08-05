from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..db.firestore import FirestoreDB
from ..core.auth import verify_firebase_token

router = APIRouter()

class ProfileCreate(BaseModel):
    email: str
    display_name: str = ""
    photo_url: str = ""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None

class PrivacyUpdate(BaseModel):
    public_profile_enabled: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None

class NotificationPreferencesUpdate(BaseModel):
    email_task_reminders: Optional[bool] = None
    email_achievements: Optional[bool] = None
    email_streak_risk: Optional[bool] = None
    email_recommendations: Optional[bool] = None

@router.post("/profile")
async def create_or_get_profile(
    profile_data: ProfileCreate,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Onboarding endpoint. Returning users get their existing profile back untouched.
    Brand-new users must supply full_name + phone_number or the profile is not created.
    """
    existing = await FirestoreDB.get_profile(user_id)
    if existing:
        return existing

    if not profile_data.full_name or not profile_data.phone_number:
        raise HTTPException(
            status_code=422,
            detail="full_name and phone_number are required to complete onboarding"
        )

    profile = await FirestoreDB.create_profile(
        user_id=user_id,
        email=profile_data.email,
        display_name=profile_data.display_name,
        photo_url=profile_data.photo_url,
        full_name=profile_data.full_name,
        phone_number=profile_data.phone_number
    )
    return profile

@router.get("/profile")
async def get_profile(user_id: str = Depends(verify_firebase_token)):
    """Get current user's profile, or 404 if onboarding hasn't happened yet"""
    profile = await FirestoreDB.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.patch("/profile")
async def update_profile(
    updates: ProfileUpdate,
    user_id: str = Depends(verify_firebase_token)
):
    """Update editable profile fields"""
    profile = await FirestoreDB.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    changes = {k: v for k, v in updates.dict().items() if v is not None}
    if changes:
        await FirestoreDB.update_profile(user_id, changes)
    return await FirestoreDB.get_profile(user_id)

@router.patch("/profile/privacy")
async def update_privacy(
    updates: PrivacyUpdate,
    user_id: str = Depends(verify_firebase_token)
):
    """Update leaderboard/public-profile privacy opt-ins"""
    profile = await FirestoreDB.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    privacy = profile.get("privacy") or {}
    for key, value in updates.dict().items():
        if value is not None:
            privacy[key] = value

    await FirestoreDB.update_profile(user_id, {"privacy": privacy})
    return await FirestoreDB.get_profile(user_id)

@router.patch("/profile/notification-preferences")
async def update_notification_preferences(
    updates: NotificationPreferencesUpdate,
    user_id: str = Depends(verify_firebase_token)
):
    """Update per-category email notification preferences"""
    profile = await FirestoreDB.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    prefs = profile.get("notification_preferences") or {}
    for key, value in updates.dict().items():
        if value is not None:
            prefs[key] = value

    await FirestoreDB.update_profile(user_id, {"notification_preferences": prefs})
    return await FirestoreDB.get_profile(user_id)
