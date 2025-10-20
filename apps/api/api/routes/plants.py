from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from ..models.plant import Plant, HealthCheckItem, PlantInventory, CareSchedule
from ..services.plant_service import PlantService
from ..services.ai_service import AIService
from ..services.autonomous_plant_service import AutonomousPlantService
from ..core.auth import verify_firebase_token

router = APIRouter()

# In-memory storage (replace with database later)
plants_db = {}
health_checks_db = {}
care_schedules_db = {}

@router.post("/autonomous")
async def create_autonomous_plant(
    plant_name: str,
    user_location: Optional[str] = None,
    user_id: str = Depends(verify_firebase_token)
):
    """Create a plant autonomously - just provide the name, AI figures out everything else"""
    try:
        # Use autonomous service to create complete plant profile
        plant_inventory = await AutonomousPlantService.identify_and_create_plant(plant_name, user_location)

        # Generate unique ID and set timestamps
        plant_inventory.plant.id = f"plant_{datetime.now().timestamp()}"
        plant_inventory.plant.created_at = datetime.now()
        plant_inventory.plant.updated_at = datetime.now()

        # Fetch and set plant image
        plant_inventory.plant.image_url = await PlantService.fetch_plant_image(
            plant_inventory.plant.name,
            plant_inventory.plant.species
        )

        # Store in database
        plants_db[plant_inventory.plant.id] = plant_inventory

        return {
            "success": True,
            "plant_inventory": plant_inventory,
            "message": f"Successfully created autonomous plant profile for {plant_name}. I've analyzed this plant and created a complete care schedule with {len(plant_inventory.care_schedule)} upcoming tasks."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating autonomous plant: {str(e)}")

@router.post("/", response_model=dict)
async def create_plant(plant: Plant, user_id: str = Depends(verify_firebase_token)):
    """Legacy plant creation - keeping for backward compatibility"""
    try:
        # Generate unique ID
        plant.id = f"plant_{datetime.now().timestamp()}"

        # Fetch plant image
        plant.image_url = await PlantService.fetch_plant_image(plant.name, plant.species)

        # Generate initial care schedule (legacy method)
        care_tasks = await PlantService.generate_care_schedule(plant)

        # Store plant
        plants_db[plant.id] = plant

        return {
            "plant": plant,
            "care_schedule": care_tasks,
            "message": "Plant added successfully with AI-generated care schedule"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_plants(user_id: str = Depends(verify_firebase_token)):
    """Get all plants with their complete inventories"""
    plant_inventories = []

    for plant_data in plants_db.values():
        if isinstance(plant_data, PlantInventory):
            plant_inventories.append(plant_data)
        else:
            # Convert legacy Plant objects to PlantInventory
            legacy_plant = plant_data
            plant_inventory = await AutonomousPlantService.identify_and_create_plant(
                legacy_plant.name,
                getattr(legacy_plant, 'location', None)
            )
            plant_inventory.plant.id = legacy_plant.id
            plant_inventories.append(plant_inventory)

    return {"plants": plant_inventories}

@router.get("/{plant_id}")
async def get_plant(plant_id: str, user_id: str = Depends(verify_firebase_token)):
    """Get a specific plant with complete inventory"""
    if plant_id not in plants_db:
        raise HTTPException(status_code=404, detail="Plant not found")

    plant_data = plants_db[plant_id]

    if isinstance(plant_data, PlantInventory):
        return {"plant_inventory": plant_data}
    else:
        # Convert legacy plant to inventory
        legacy_plant = plant_data
        plant_inventory = await AutonomousPlantService.identify_and_create_plant(
            legacy_plant.name,
            getattr(legacy_plant, 'location', None)
        )
        plant_inventory.plant.id = legacy_plant.id
        return {"plant_inventory": plant_inventory}

@router.get("/{plant_id}/schedule")
async def get_plant_schedule(plant_id: str, user_id: str = Depends(verify_firebase_token)):
    """Get upcoming care schedule for a specific plant"""
    if plant_id not in plants_db:
        raise HTTPException(status_code=404, detail="Plant not found")

    plant_data = plants_db[plant_id]

    if isinstance(plant_data, PlantInventory):
        schedule = plant_data.care_schedule
    else:
        # Generate schedule for legacy plants
        schedule = await PlantService.generate_care_schedule(plant_data)

    # Filter for upcoming tasks (next 30 days)
    now = datetime.now()
    upcoming_tasks = [
        task for task in schedule
        if task.scheduled_date >= now and task.scheduled_date <= now.replace(day=now.day + 30)
    ]

    return {
        "plant_id": plant_id,
        "upcoming_tasks": upcoming_tasks,
        "total_tasks": len(schedule),
        "next_task": upcoming_tasks[0] if upcoming_tasks else None
    }

@router.post("/{plant_id}/schedule/complete")
async def complete_care_task(
    plant_id: str,
    schedule_id: str,
    notes: Optional[str] = None,
    user_id: str = Depends(verify_firebase_token)
):
    """Mark a care task as completed"""
    if plant_id not in plants_db:
        raise HTTPException(status_code=404, detail="Plant not found")

    plant_data = plants_db[plant_id]

    if isinstance(plant_data, PlantInventory):
        # Find and update the task
        for task in plant_data.care_schedule:
            if task.plant_id == plant_id and str(task.scheduled_date.timestamp()) == schedule_id:
                task.completed = True
                task.completed_at = datetime.now()
                task.notes = notes
                break

        # Update plant care tracking
        now = datetime.now()
        if "watering" in schedule_id:
            plant_data.plant.last_watered = now
            plant_data.plant.days_since_watering = 0
            plant_data.plant.needs_watering = False
        elif "fertilizing" in schedule_id:
            plant_data.plant.last_fertilized = now
            plant_data.plant.days_since_fertilizing = 0
            plant_data.plant.needs_fertilizing = False

        return {
            "success": True,
            "message": "Care task completed successfully",
            "plant_updated": True
        }
    else:
        return {"success": True, "message": "Task completion recorded (legacy plant)"}

@router.post("/{plant_id}/health-check")
async def submit_health_check(
    plant_id: str,
    health_check: HealthCheckItem,
    user_id: str = Depends(verify_firebase_token)
):
    """Submit daily health check and get AI analysis"""
    try:
        if plant_id not in plants_db:
            raise HTTPException(status_code=404, detail="Plant not found")

        health_check.plant_id = plant_id
        health_check.id = f"check_{datetime.now().timestamp()}"

        # Store health check
        if plant_id not in health_checks_db:
            health_checks_db[plant_id] = []
        health_checks_db[plant_id].append(health_check)

        # Get plant and recent health checks
        plant_data = plants_db[plant_id]
        recent_checks = health_checks_db[plant_id][-5:]  # Last 5 checks

        # AI analysis
        analysis = await AIService.analyze_plant_health(plant_data.plant, recent_checks)

        # Update plant health score and last check
        if isinstance(plant_data, PlantInventory):
            plant_data.plant.health_score = analysis.health_score
            plant_data.plant.last_health_check = datetime.now()
            plant_data.plant.health_status = "Excellent" if analysis.health_score > 90 else "Good" if analysis.health_score > 70 else "Needs Attention"

        return {
            "health_check": health_check,
            "analysis": analysis,
            "message": "Health check submitted and analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/today")
async def get_today_schedule(user_id: str = Depends(verify_firebase_token)):
    """Get all care tasks scheduled for today"""
    today = datetime.now().date()
    today_tasks = []

    for plant_data in plants_db.values():
        if isinstance(plant_data, PlantInventory):
            schedule = plant_data.care_schedule
        else:
            # Generate schedule for legacy plants
            schedule = await PlantService.generate_care_schedule(plant_data)

        # Filter for today's tasks
        for task in schedule:
            if task.scheduled_date.date() == today and not task.completed:
                today_tasks.append({
                    "task": task,
                    "plant_name": plant_data.name if hasattr(plant_data, 'name') else plant_data.plant.name,
                    "plant_id": plant_data.id if hasattr(plant_data, 'id') else plant_data.plant.id
                })

    # Sort by priority
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    today_tasks.sort(key=lambda x: priority_order.get(x["task"].priority, 4))

    return {
        "date": today,
        "tasks": today_tasks,
        "total_tasks": len(today_tasks)
    }

@router.get("/calendar/week")
async def get_week_schedule(user_id: str = Depends(verify_firebase_token)):
    """Get care tasks for the next 7 days"""
    now = datetime.now()
    week_tasks = []

    for plant_data in plants_db.values():
        if isinstance(plant_data, PlantInventory):
            schedule = plant_data.care_schedule
        else:
            schedule = await PlantService.generate_care_schedule(plant_data)

        # Filter for next 7 days
        for task in schedule:
            if now <= task.scheduled_date <= now.replace(day=now.day + 7) and not task.completed:
                week_tasks.append({
                    "task": task,
                    "plant_name": plant_data.name if hasattr(plant_data, 'name') else plant_data.plant.name,
                    "plant_id": plant_data.id if hasattr(plant_data, 'id') else plant_data.plant.id
                })

    # Group by day
    tasks_by_day = {}
    for task_info in week_tasks:
        day_key = task_info["task"].scheduled_date.strftime("%Y-%m-%d")
        if day_key not in tasks_by_day:
            tasks_by_day[day_key] = []
        tasks_by_day[day_key].append(task_info)

    return {
        "week_start": now.date(),
        "tasks_by_day": tasks_by_day,
        "total_tasks": len(week_tasks)
    }