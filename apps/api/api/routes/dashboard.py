from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, date
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB

router = APIRouter()

@router.get("/")
async def get_dashboard(user_id: str = Depends(verify_firebase_token)):
    """Get dashboard overview data"""
    try:
        # Get user plants
        plants = await FirestoreDB.get_user_plants(user_id)
        
        # Get today's tasks
        today = date.today()
        all_tasks = await FirestoreDB.get_user_tasks(user_id, completed=False)
        today_tasks = []
        
        for task in all_tasks:
            due_date = task.get("due_date")
            if due_date:
                if isinstance(due_date, str):
                    task_date = datetime.fromisoformat(due_date.replace('Z', '+00:00')).date()
                else:
                    task_date = due_date.date() if hasattr(due_date, 'date') else due_date
                
                if task_date <= today:
                    today_tasks.append(task)
        
        # Get user stats
        profile = await FirestoreDB.get_profile(user_id)
        user_stats = {
            "total_score": profile.get("total_score", 0) if profile else 0,
            "level": profile.get("level", 1) if profile else 1,
            "streak_days": profile.get("streak_days", 0) if profile else 0,
            "tasks_completed": profile.get("tasks_completed", 0) if profile else 0
        }
        
        # Calculate health summary
        healthy_count = sum(1 for p in plants if p.get("health_status") == "healthy")
        attention_count = sum(1 for p in plants if p.get("health_status") == "needs_attention")
        critical_count = sum(1 for p in plants if p.get("health_status") == "critical")
        
        return {
            "total_plants": len(plants),
            "tasks_today": len(today_tasks),
            "healthy_plants": healthy_count,
            "attention_needed": attention_count,
            "critical_plants": critical_count,
            "user_stats": user_stats,
            "recent_plants": plants[:5],
            "upcoming_tasks": today_tasks[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")
