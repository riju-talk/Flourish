from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, date
from ..models.task import CareTask
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB
from ..routes.leaderboard import update_user_score

router = APIRouter()

@router.get("/today")
async def get_today_tasks(user_id: str = Depends(verify_firebase_token)):
    """Get today's tasks"""
    try:
        today = date.today()
        
        # Get all incomplete tasks for the user
        tasks = await FirestoreDB.get_user_tasks(user_id, completed=False)
        
        # Filter tasks for today
        today_tasks = []
        for task in tasks:
            due_date = task.get("due_date")
            if due_date:
                # Handle both datetime objects and ISO strings
                if isinstance(due_date, str):
                    task_date = datetime.fromisoformat(due_date.replace('Z', '+00:00')).date()
                else:
                    task_date = due_date.date() if hasattr(due_date, 'date') else due_date
                
                if task_date == today:
                    today_tasks.append(task)
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        today_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 3))
        
        return {"tasks": today_tasks, "date": today.isoformat()}
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
        await FirestoreDB.create_notification({
            "user_id": user_id,
            "type": "task_completed",
            "title": "Task Completed!",
            "message": f"You earned {points} points for completing: {task.get('title')}",
            "read": False
        })
        
        return {
            "success": True,
            "task": task,
            "points_earned": points
        }
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
