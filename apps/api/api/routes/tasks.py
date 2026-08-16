from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, date, timedelta
from ..models.task import CareTask
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB
from ..services.plant_service import PlantService
from ..services.notification_service import NotificationService
from ..services.groq_service import GroqService
from ..routes.leaderboard import update_user_score

router = APIRouter()

@router.get("/today")
async def get_today_tasks(user_id: str = Depends(verify_firebase_token)):
    """Get today's tasks, plus completion counts for the dashboard's Daily Rituals progress bar"""
    try:
        today = date.today()

        # All of the user's tasks, complete and incomplete - needed for the completion
        # percentage below, not just the pending list the checklist renders.
        all_tasks = await FirestoreDB.get_user_tasks(user_id)

        today_tasks = []
        completed_today = 0
        for task in all_tasks:
            due_date = task.get("due_date")
            if due_date:
                # Handle both datetime objects and ISO strings
                if isinstance(due_date, str):
                    task_date = datetime.fromisoformat(due_date.replace('Z', '+00:00')).date()
                else:
                    task_date = due_date.date() if hasattr(due_date, 'date') else due_date

                if task_date == today:
                    if task.get("completed"):
                        completed_today += 1
                    else:
                        today_tasks.append(task)

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        today_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 3))

        total_today = len(today_tasks) + completed_today
        completion_percent = round((completed_today / total_today) * 100) if total_today else 0

        return {
            "tasks": today_tasks,
            "date": today.isoformat(),
            "completed_count": completed_today,
            "total_count": total_today,
            "completion_percent": completion_percent,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/complete")
async def complete_task(
    task_id: str,
    notes: str = None,
    user_id: str = Depends(verify_firebase_token)
):
    """Mark task as completed and award points"""
    try:
        # Get task
        task = await FirestoreDB.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Verify ownership
        if task.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update task
        updates = {
            "completed": True,
            "completed_at": datetime.now().isoformat(),
            "notes": notes
        }
        await FirestoreDB.update_task(task_id, updates)
        
        # Award points
        points = task.get("points", 10)
        await update_user_score(user_id, points)

        # Create notification
        await NotificationService.notify(
            user_id, "task_completed", "Task Completed!",
            f"You earned {points} points for completing: {task.get('title')}"
        )

        # Keep PlantMind's persistent memory of this user's care habits current.
        await GroqService.update_agent_profile_summary(user_id)

        return {
            "success": True,
            "task": task,
            "points_earned": points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/snooze")
async def snooze_task(
    task_id: str,
    hours: int = 24,
    user_id: str = Depends(verify_firebase_token)
):
    """Push a task's due date forward without completing it"""
    try:
        task = await FirestoreDB.get_task(task_id)
        if not task or task.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Task not found")

        due_date = task.get("due_date")
        if due_date:
            base = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        else:
            base = datetime.now()
        new_due_date = (base + timedelta(hours=hours)).isoformat()

        await FirestoreDB.update_task(task_id, {"due_date": new_due_date})
        return {"success": True, "due_date": new_due_date}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{task_id}/reschedule")
async def reschedule_task(
    task_id: str,
    due_date: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Set a task's due date explicitly"""
    try:
        task = await FirestoreDB.get_task(task_id)
        if not task or task.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Task not found")

        await FirestoreDB.update_task(task_id, {"due_date": due_date})
        return {"success": True, "due_date": due_date}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/{plant_id}")
async def generate_tasks_for_plant(
    plant_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Generate a real forward-looking watering/fertilizing schedule for a plant"""
    try:
        plant = await FirestoreDB.get_plant(plant_id, user_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")

        existing_tasks = await FirestoreDB.get_plant_tasks(plant_id)
        existing_types = {t.get("task_type") for t in existing_tasks if not t.get("completed")}
        missing_types = [t for t in ("watering", "fertilizing") if t not in existing_types]

        created = await PlantService.create_projected_schedule(user_id, plant, types=missing_types) if missing_types else []
        return {"success": True, "tasks_created": created}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_user_tasks(
    completed: bool = None,
    user_id: str = Depends(verify_firebase_token)
):
    """Get all tasks for user"""
    try:
        tasks = await FirestoreDB.get_user_tasks(user_id, completed=completed)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_task(
    task_data: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """Create a new task"""
    try:
        task_data["user_id"] = user_id
        task_data.setdefault("completed", False)
        task_data.setdefault("points", 10)
        
        task = await FirestoreDB.create_task(task_data)
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}")
async def update_task(
    task_id: str,
    task_updates: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """Update a task"""
    try:
        # Verify ownership
        task = await FirestoreDB.get_task(task_id)
        if not task or task.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        
        await FirestoreDB.update_task(task_id, task_updates)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Delete a task"""
    try:
        # Verify ownership
        task = await FirestoreDB.get_task(task_id)
        if not task or task.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        
        await FirestoreDB.delete_task(task_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
