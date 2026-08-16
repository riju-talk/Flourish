from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..models.plant import Plant, HealthCheckItem, PlantInventory, CareSchedule
from ..services.plant_service import PlantService
from ..services.ai_service import AIService
from ..services.autonomous_plant_service import AutonomousPlantService
from ..services.groq_service import GroqService
from ..services.perenual_service import PerenualService
from ..services.tavily_service import TavilyService
from ..services.plant_lookup_service import curate_plant_info
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB
from ..services.notification_service import NotificationService
from ..routes.leaderboard import update_user_score

router = APIRouter()

class PlantLookupRequest(BaseModel):
    plant_name: str

class AutonomousPlantRequest(BaseModel):
    plant_name: str
    user_location: Optional[str] = None

@router.post("/lookup")
async def agentic_plant_lookup(
    payload: PlantLookupRequest,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Explore/Plant Lookup: internet-first, not internet-only. Perenual (deterministic
    plant-care database) and Tavily (live web search) are the sole sources of fact;
    Groq then synthesizes them into one coherent, well-organized profile
    (GroqService.curate_plant_lookup) instead of the raw keyword/sentence extraction
    a purely rule-based pass produces. If that synthesis call fails for any reason
    (the underlying model's json_mode is occasionally unreliable - see
    groq_json_mode_flaky memory note), curate_plant_info's deterministic extraction is
    the fallback, so a lookup never comes back empty just because Groq had a bad turn.
    """
    plant_name = payload.plant_name
    try:
        perenual_info = await PerenualService.get_care_info(plant_name)
        # If "plant_name" is a known-ambiguous colloquial name (e.g. "money plant"),
        # search the web using the same disambiguated species Perenual resolved to,
        # so Tavily and Perenual are grounded in the same plant rather than each
        # independently guessing which of several common plants the query means.
        search_query = PerenualService.resolve_alias(plant_name) or plant_name
        tavily_results = await TavilyService.search_raw(
            f"{search_query} plant care guide watering sunlight toxicity propagation native habitat"
        )

        plant_info = await GroqService.curate_plant_lookup(plant_name, perenual_info, tavily_results)
        if not plant_info:
            plant_info = curate_plant_info(plant_name, perenual_info, tavily_results)

        try:
            image_url = await PlantService.fetch_plant_image(
                plant_info.get("common_name", plant_name),
                plant_info.get("scientific_name", "")
            )
            plant_info["image_url"] = image_url
        except Exception:
            plant_info["image_url"] = None

        return {
            "success": True,
            "plant_info": plant_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lookup plant: {str(e)}")

@router.post("/autonomous")
async def create_autonomous_plant(
    payload: AutonomousPlantRequest,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Create a plant with AI-generated care info, grounded in Perenual's real plant-care
    database wherever available (watering cadence, sunlight) rather than relying on
    Groq's guess for those specific fields - see PlantService.resolve_care_info.
    """
    plant_name = payload.plant_name
    user_location = payload.user_location
    try:
        plant_info = await GroqService.get_plant_info_agentic(plant_name)

        plant_data = await PlantService.build_new_plant_document(
            user_id,
            plant_name=plant_info.get("common_name") or plant_name,
            location=user_location,
            groq_plant_info=plant_info,
            care_instructions=plant_info.get("interesting_facts") or "",
        )
        fertilizing = plant_info.get("fertilizing") or {}
        fertilizing_days = PlantService._parse_frequency_days(fertilizing.get("frequency")) or 30
        plant_data["fertilizer_frequency_days"] = fertilizing_days
        plant_data["fertilizer_type"] = fertilizing.get("type") or plant_data["fertilizer_type"]

        plant = await FirestoreDB.create_plant(user_id, plant_data)

        tasks = await PlantService.create_projected_schedule(user_id, plant)

        # Keep PlantMind's persistent memory of this user's garden current the moment
        # it changes, rather than waiting for the next chat turn to notice.
        await GroqService.update_agent_profile_summary(user_id)

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

@router.get("/{plant_id}/schedule")
async def get_plant_schedule(
    plant_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Get this plant's care schedule (its care_tasks)"""
    plant = await FirestoreDB.get_plant(plant_id, user_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return await FirestoreDB.get_plant_tasks(plant_id)

@router.post("/{plant_id}/schedule/complete")
async def complete_schedule_item(
    plant_id: str,
    payload: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """Complete a care-schedule item (a care_task) for this plant"""
    plant = await FirestoreDB.get_plant(plant_id, user_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    schedule_id = payload.get("schedule_id")
    if not schedule_id:
        raise HTTPException(status_code=400, detail="schedule_id is required")

    task = await FirestoreDB.get_task(schedule_id)
    if not task or task.get("user_id") != user_id or task.get("plant_id") != plant_id:
        raise HTTPException(status_code=404, detail="Schedule item not found")

    updates = {
        "completed": True,
        "completed_at": datetime.now().isoformat()
    }
    notes = payload.get("notes")
    if notes is not None:
        updates["notes"] = notes
    await FirestoreDB.update_task(schedule_id, updates)

    points = task.get("points", 10)
    await update_user_score(user_id, points)

    await NotificationService.notify(
        user_id, "task_completed", "Task Completed!",
        f"You earned {points} points for completing: {task.get('title')}"
    )

    return {"success": True, "points_earned": points}

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
