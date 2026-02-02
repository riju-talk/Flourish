from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from ..models.plant import Plant, HealthCheckItem, PlantInventory, CareSchedule
from ..services.plant_service import PlantService
from ..services.ai_service import AIService
from ..services.autonomous_plant_service import AutonomousPlantService
from ..services.ollama_service import OllamaService
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB
from ..routes.leaderboard import update_user_score

router = APIRouter()

@router.post("/lookup")
async def agentic_plant_lookup(
    plant_name: str,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Agentic Plant Lookup: Type a plant name and get comprehensive information
    Uses Ollama LLM + external APIs to retrieve all relevant data
    """
    try:
        # Get comprehensive plant info using Ollama
        plant_info = await OllamaService.get_plant_info_agentic(plant_name)
        
        # Fetch image from Unsplash
        try:
            image_url = await PlantService.fetch_plant_image(
                plant_info.get("common_name", plant_name),
                plant_info.get("scientific_name", "")
            )
            plant_info["image_url"] = image_url
        except:
            plant_info["image_url"] = None
        
        return {
            "success": True,
            "plant_info": plant_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lookup plant: {str(e)}")

@router.post("/autonomous")
async def create_autonomous_plant(
    plant_name: str,
    user_location: Optional[str] = None,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Create a plant with AI-generated care schedule
    """
    try:
        # Get plant info from agentic lookup
        plant_info = await OllamaService.get_plant_info_agentic(plant_name)
        
        # Fetch image
        image_url = None
        try:
            image_url = await PlantService.fetch_plant_image(
                plant_info.get("common_name", plant_name),
                plant_info.get("scientific_name", "")
            )
        except:
            pass
        
        # Create plant
        plant_data = {
            "name": plant_info.get("common_name", plant_name),
            "species": plant_info.get("scientific_name", ""),
            "location": user_location or "Indoor",
            "image_url": image_url,
            "care_instructions": plant_info,
            "health_status": "healthy",
            "last_watered": None,
            "next_watering": None
        }
        
        plant = await FirestoreDB.create_plant(user_id, plant_data)
        
        # Create initial care tasks based on plant info
        care_schedule = plant_info.get("care_schedule", {})
        tasks = []
        
        if care_schedule.get("watering"):
            task_data = {
                "user_id": user_id,
                "plant_id": plant["id"],
                "task_type": "watering",
                "title": f"Water {plant['name']}",
                "description": care_schedule["watering"],
                "due_date": datetime.now().isoformat(),
                "recurring": True,
                "recurring_days": 7,
                "completed": False,
                "points": 10
            }
            task = await FirestoreDB.create_task(task_data)
            tasks.append(task)
        
        return {
            "success": True,
            "plant": plant,
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plant: {str(e)}")

@router.post("/")
async def create_plant(
    plant: Plant,
    user_id: str = Depends(verify_firebase_token)
):
    """Create a new plant"""
    try:
        plant_data = plant.dict()
        plant_data.pop("id", None)
        new_plant = await FirestoreDB.create_plant(user_id, plant_data)
        return new_plant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plant: {str(e)}")

@router.get("/")
async def get_plants(user_id: str = Depends(verify_firebase_token)):
    """Get all plants for user"""
    try:
        plants = await FirestoreDB.get_user_plants(user_id)
        return {"plants": plants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plants: {str(e)}")

@router.get("/{plant_id}")
async def get_plant(
    plant_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Get a specific plant"""
    plant = await FirestoreDB.get_plant(plant_id, user_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@router.put("/{plant_id}")
async def update_plant(
    plant_id: str,
    plant_updates: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """Update a plant"""
    try:
        # Verify ownership
        plant = await FirestoreDB.get_plant(plant_id, user_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        await FirestoreDB.update_plant(plant_id, plant_updates)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update plant: {str(e)}")

@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Delete a plant"""
    try:
        # Verify ownership
        plant = await FirestoreDB.get_plant(plant_id, user_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        await FirestoreDB.delete_plant(plant_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete plant: {str(e)}")

@router.get("/{plant_id}/tasks")
async def get_plant_tasks(
    plant_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Get all tasks for a plant"""
    # Verify ownership
    plant = await FirestoreDB.get_plant(plant_id, user_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    tasks = await FirestoreDB.get_plant_tasks(plant_id)
    return tasks

@router.post("/{plant_id}/health-check")
async def create_health_check(
    plant_id: str,
    health_data: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """Create a health check for a plant"""
    # Verify ownership
    plant = await FirestoreDB.get_plant(plant_id, user_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    health_data["plant_id"] = plant_id
    health_data["user_id"] = user_id
    
    health_check = await FirestoreDB.create_health_check(health_data)
    return health_check

@router.get("/{plant_id}/health-checks")
async def get_plant_health_checks(
    plant_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Get health check history for a plant"""
    # Verify ownership
    plant = await FirestoreDB.get_plant(plant_id, user_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    health_checks = await FirestoreDB.get_plant_health_checks(plant_id)
    return health_checks
