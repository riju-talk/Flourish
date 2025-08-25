from fastapi import APIRouter, HTTPException
from ..services.plant_service import PlantService

router = APIRouter()

@router.get("/plant/{plant_name}")
async def get_plant_image(plant_name: str, species: str = ""):
    """Fetch plant image from Unsplash"""
    try:
        image_url = await PlantService.fetch_plant_image(plant_name, species)
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))