from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.plant import Plant, HealthCheckItem, PlantInventory, CareSchedule
from ..models.db_models import Plant as DBPlant, CareTask as DBCareTask, HealthCheck as DBHealthCheck
from ..services.plant_service import PlantService
from ..services.ai_service import AIService
from ..services.autonomous_plant_service import AutonomousPlantService
from ..core.auth import verify_firebase_token
from ..db.session import get_db

router = APIRouter()

@router.post("/autonomous")
async def create_autonomous_plant(
    plant_name: str,
    user_location: Optional[str] = None,
    user_id: str = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Create a plant autonomously - stores in Supabase"""
    try:
        # Use autonomous service to create complete plant profile
        plant_inventory = await AutonomousPlantService.identify_and_create_plant(plant_name, user_location)

        # Map to DB model
        db_plant = DBPlant(
            id=f"plant_{datetime.now().timestamp()}",
            user_id=user_id,
            name=plant_inventory.plant.name,
            species=plant_inventory.plant.species,
            location=plant_inventory.plant.location,
            image_url=await PlantService.fetch_plant_image(plant_inventory.plant.name, plant_inventory.plant.species)
        )
        
        db.add(db_plant)
        
        # Add care tasks
        for task in plant_inventory.care_schedule:
            db_task = DBCareTask(
                id=f"task_{datetime.now().timestamp()}_{task.title}",
                plant_id=db_plant.id,
                user_id=user_id,
                task_type=task.schedule_type,
                title=task.title,
                description=task.description,
                scheduled_date=task.scheduled_date,
                priority=task.priority
            )
            db.add(db_task)
            
        db.commit()

        return {
            "success": True,
            "message": f"Successfully created plant profile for {plant_name}."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating autonomous plant: {str(e)}")

@router.get("/")
async def get_plants(user_id: str = Depends(verify_firebase_token), db: Session = Depends(get_db)):
    """Get all plants for the current user from Supabase"""
    plants = db.query(DBPlant).filter(DBPlant.user_id == user_id).all()
    return {"plants": plants}

@router.get("/{plant_id}")
async def get_plant(plant_id: str, user_id: str = Depends(verify_firebase_token), db: Session = Depends(get_db)):
    """Get a specific plant from Supabase"""
    plant = db.query(DBPlant).filter(DBPlant.id == plant_id, DBPlant.user_id == user_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"plant": plant}

@router.get("/{plant_id}/schedule")
async def get_plant_schedule(plant_id: str, user_id: str = Depends(verify_firebase_token), db: Session = Depends(get_db)):
    """Get upcoming care schedule from Supabase"""
    tasks = db.query(DBCareTask).filter(DBCareTask.plant_id == plant_id, DBCareTask.completed == False).all()
    return {"upcoming_tasks": tasks}

@router.post("/{plant_id}/schedule/complete")
async def complete_care_task(
    plant_id: str,
    schedule_id: str,
    notes: Optional[str] = None,
    user_id: str = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Mark a care task as completed in Supabase"""
    task = db.query(DBCareTask).filter(DBCareTask.id == schedule_id, DBCareTask.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.completed = True
    task.completed_at = datetime.now()
    task.notes = notes
    
    # Update user points (gamification)
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if profile:
        profile.total_score += task.points
        
    db.commit()
    return {"success": True, "message": "Task completed and points awarded!"}

@router.get("/calendar/today")
async def get_today_schedule(user_id: str = Depends(verify_firebase_token), db: Session = Depends(get_db)):
    """Get all care tasks scheduled for today from Supabase"""
    today = datetime.now().date()
    tasks = db.query(DBCareTask).filter(
        DBCareTask.user_id == user_id, 
        DBCareTask.completed == False
    ).all()
    
    today_tasks = [t for t in tasks if t.scheduled_date.date() == today]
    return {"tasks": today_tasks, "date": today}