from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta
from ..db.firestore import FirestoreDB
from ..core.auth import verify_firebase_token
from ..services.email_service import EmailService
from ..services.notification_service import NotificationService

router = APIRouter()

def calculate_level(score: int) -> int:
    """Calculate user level based on score (1000 points per level)"""
    return max(1, score // 1000 + 1)

async def update_user_score(user_id: str, points: int):
    """Update user's score and gamification stats"""
    try:
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            return
        
        # Update score and level
        new_score = profile.get("total_score", 0) + points
        new_level = calculate_level(new_score)
        tasks_completed = profile.get("tasks_completed", 0) + 1
        
        # Update streak
        last_activity = profile.get("last_activity")
        streak_days = profile.get("streak_days", 0)
        today = datetime.now().date()
        
        if last_activity:
            if isinstance(last_activity, str):
                last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
            else:
                last_date = last_activity.date() if hasattr(last_activity, 'date') else last_activity
            
            days_diff = (today - last_date).days
            if days_diff == 1:
                streak_days += 1
            elif days_diff > 1:
                streak_days = 1
        else:
            streak_days = 1
        
        # Check for achievements
        achievements = profile.get("achievements", [])
        
        # Achievement: First task
        if tasks_completed == 1 and "first_task" not in achievements:
            achievements.append("first_task")
            title, message = "Achievement Unlocked!", "First Steps - Completed your first task!"
            await NotificationService.notify(user_id, "achievement", title, message)
            await EmailService.send_for_notification(user_id, "achievement", title, message)

        # Achievement: Level up
        if new_level > profile.get("level", 1):
            achievements.append(f"level_{new_level}")
            title, message = "Level Up!", f"You've reached Level {new_level}!"
            await NotificationService.notify(user_id, "achievement", title, message)
            await EmailService.send_for_notification(user_id, "achievement", title, message)

        # Achievement: 7 day streak
        if streak_days >= 7 and "streak_7" not in achievements:
            achievements.append("streak_7")
            title, message = "Achievement Unlocked!", "Week Warrior - Maintained a 7 day streak!"
            await NotificationService.notify(user_id, "achievement", title, message)
            await EmailService.send_for_notification(user_id, "achievement", title, message)
        
        # Update profile
        updates = {
            "total_score": new_score,
            "level": new_level,
            "tasks_completed": tasks_completed,
            "streak_days": streak_days,
            "last_activity": datetime.now().isoformat(),
            "achievements": achievements
        }
        
        await FirestoreDB.update_profile(user_id, updates)
        
    except Exception as e:
        print(f"Error updating user score: {e}")

def _public_leaderboard_entry(entry: Dict, rank: int, viewer_id: str) -> Dict:
    """
    Privacy-safe leaderboard row. email/phone_number are only included when the
    entry's owner opted in via profiles.privacy, or the viewer is looking at their
    own row. See docs/01-PRD.md §5.10 and docs/04-Rules-of-Engagement.md Rule 12.
    """
    privacy = entry.get("privacy") or {}
    is_self = entry.get("id") == viewer_id

    row = {
        "id": entry.get("id"),
        "display_name": entry.get("display_name"),
        "photo_url": entry.get("photo_url"),
        "total_score": entry.get("total_score", 0),
        "level": entry.get("level", 1),
        "streak_days": entry.get("streak_days", 0),
        "achievements": entry.get("achievements", []),
        "rank": rank
    }

    if is_self or privacy.get("show_email"):
        row["email"] = entry.get("email")
    if is_self or privacy.get("show_phone"):
        row["phone_number"] = entry.get("phone_number")

    return row

@router.get("/leaderboard")
async def get_leaderboard(
    period: str = "all_time",  # all_time, monthly, weekly
    limit: int = 100,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Get leaderboard showing top 100 users by points/tasks completed.
    Privacy-safe by default: contact info is only included for users who opted in.
    Note: For simplicity, Firebase version shows all-time leaderboard
    Period filtering requires additional task tracking
    """
    try:
        raw_leaderboard = await FirestoreDB.get_leaderboard(100)

        leaderboard = [
            _public_leaderboard_entry(entry, i, user_id)
            for i, entry in enumerate(raw_leaderboard, 1)
        ]

        # Get current user's stats
        user_profile = await FirestoreDB.get_profile(user_id)
        user_rank = await FirestoreDB.get_user_rank(user_id)

        user_stats = {
            "rank": user_rank,
            "total_score": user_profile.get("total_score", 0) if user_profile else 0,
            "level": user_profile.get("level", 1) if user_profile else 1,
            "tasks_completed": user_profile.get("tasks_completed", 0) if user_profile else 0,
            "streak_days": user_profile.get("streak_days", 0) if user_profile else 0
        }

        return {
            "leaderboard": leaderboard,
            "user_stats": user_stats,
            "period": period
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")

@router.get("/leaderboard/me")
async def get_my_leaderboard_entry(user_id: str = Depends(verify_firebase_token)):
    """Current user's own rank + full stats (always includes their own contact info)"""
    try:
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        rank = await FirestoreDB.get_user_rank(user_id)
        return {
            "id": user_id,
            "display_name": profile.get("display_name"),
            "photo_url": profile.get("photo_url"),
            "email": profile.get("email"),
            "phone_number": profile.get("phone_number"),
            "total_score": profile.get("total_score", 0),
            "level": profile.get("level", 1),
            "streak_days": profile.get("streak_days", 0),
            "achievements": profile.get("achievements", []),
            "rank": rank
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard entry: {str(e)}")

@router.get("/stats")
async def get_user_stats(user_id: str = Depends(verify_firebase_token)):
    """Get detailed stats for current user"""
    try:
        profile = await FirestoreDB.get_profile(user_id)
        if not profile:
            return {
                "total_score": 0,
                "level": 1,
                "tasks_completed": 0,
                "streak_days": 0,
                "achievements": [],
                "rank": 0
            }
        
        rank = await FirestoreDB.get_user_rank(user_id)
        
        # Get completion rate
        all_tasks = await FirestoreDB.get_user_tasks(user_id)
        completed_tasks = [t for t in all_tasks if t.get("completed")]
        completion_rate = (len(completed_tasks) / len(all_tasks) * 100) if all_tasks else 0
        
        return {
            "total_score": profile.get("total_score", 0),
            "level": profile.get("level", 1),
            "tasks_completed": profile.get("tasks_completed", 0),
            "streak_days": profile.get("streak_days", 0),
            "achievements": profile.get("achievements", []),
            "rank": rank,
            "completion_rate": round(completion_rate, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")
