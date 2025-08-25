from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, date
from ..models.task import CareTask

router = APIRouter()

# In-memory storage (replace with database later)
tasks_db = {}

@router.get("/today", response_model=dict)
async def get_today_tasks():
    """Get today's AI-generated tasks"""
    try:
        today = date.today()
        
        # Filter tasks for today
        today_tasks = []
        for task_list in tasks_db.values():
            for task in task_list:
                if task.scheduled_date.date() == today and task.status == "pending":
                    today_tasks.append(task)
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        today_tasks.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return {"tasks": today_tasks, "date": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/complete")
async def complete_task(task_id: str, notes: str = None):
    """Mark task as completed"""
    try:
        # Find and update task
        task_found = False
        for plant_id, task_list in tasks_db.items():
            for task in task_list:
                if task.id == task_id:
                    task.status = "completed"
                    task.completed_date = datetime.now()
                    task_found = True
                    break
            if task_found:
                break
        
        if not task_found:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task_id,
            "completed_at": datetime.now(),
            "notes": notes,
            "message": "Task completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/{plant_id}")
async def generate_tasks_for_plant(plant_id: str):
    """Generate care tasks for a specific plant"""
    try:
        from .plants import plants_db
        from ..services.plant_service import PlantService
        
        if plant_id not in plants_db:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        plant = plants_db[plant_id]
        tasks = await PlantService.generate_care_schedule(plant)
        
        # Store tasks
        tasks_db[plant_id] = tasks
        
        return {
            "plant_id": plant_id,
            "tasks": tasks,
            "message": f"Generated {len(tasks)} care tasks"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))