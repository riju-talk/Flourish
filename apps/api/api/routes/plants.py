from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from ..models.plant import Plant, HealthCheckItem
from ..services.plant_service import PlantService
from ..services.ai_service import AIService

router = APIRouter()

# In-memory storage (replace with database later)
plants_db = {}
health_checks_db = {}

@router.post("/", response_model=dict)
async def create_plant(plant: Plant):
    """Create a new plant with AI-generated care schedule"""
    try:
        # Generate unique ID
        plant.id = f"plant_{datetime.now().timestamp()}"
        
        # Fetch plant image
        plant.image_url = await PlantService.fetch_plant_image(plant.name, plant.species)
        
        # Generate initial care schedule
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
async def get_plants():
    """Get all plants"""
    return {"plants": list(plants_db.values())}

@router.get("/{plant_id}")
async def get_plant(plant_id: str):
    """Get a specific plant"""
    if plant_id not in plants_db:
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"plant": plants_db[plant_id]}

@router.post("/{plant_id}/health-check")
async def submit_health_check(plant_id: str, health_check: HealthCheckItem):
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
        plant = plants_db[plant_id]
        recent_checks = health_checks_db[plant_id]
        
        # AI analysis
        analysis = await AIService.analyze_plant_health(plant, recent_checks)
        
        # Update plant health score
        plant.health_score = analysis.health_score
        plants_db[plant_id] = plant
        
        return {
            "health_check": health_check,
            "analysis": analysis,
            "message": "Health check submitted and analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))