import httpx
from typing import List
from datetime import datetime, timedelta
from ..models.plant import Plant
from ..models.task import CareTask

class PlantService:
    @staticmethod
    async def fetch_plant_image(plant_name: str, species: str) -> str:
        """Fetch a plant image from Unsplash API"""
        try:
            query = f"{plant_name} {species} plant"
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": 1,
                "client_id": "demo"  # Replace with actual Unsplash API key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data["results"]:
                        return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"Error fetching image: {e}")
        
        # Fallback to a default plant image
        return "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop"

    @staticmethod
    async def generate_care_schedule(plant: Plant) -> List[CareTask]:
        """Generate AI-optimized care schedule"""
        tasks = []
        now = datetime.now()
        
        # Generate watering schedule
        for i in range(14):  # Next 2 weeks
            task_date = now + timedelta(days=i * plant.watering_frequency_days)
            tasks.append(CareTask(
                plant_id=plant.id,
                task_type="watering",
                title=f"Water {plant.name}",
                description=f"Regular watering for {plant.species}",
                scheduled_date=task_date,
                priority="high" if i == 0 else "medium"
            ))
        
        # Generate fertilizing schedule
        if plant.fertilizing_frequency_days:
            for i in range(4):  # Next few months
                task_date = now + timedelta(days=i * plant.fertilizing_frequency_days)
                tasks.append(CareTask(
                    plant_id=plant.id,
                    task_type="fertilizing",
                    title=f"Fertilize {plant.name}",
                    description=f"Nutrient boost for {plant.species}",
                    scheduled_date=task_date,
                    priority="medium"
                ))
        
        # Generate health check schedule
        for i in range(7):  # Daily checks for a week
            task_date = now + timedelta(days=i)
            tasks.append(CareTask(
                plant_id=plant.id,
                task_type="checking",
                title=f"Health check for {plant.name}",
                description="Daily health monitoring",
                scheduled_date=task_date,
                priority="low",
                estimated_time="2 minutes"
            ))
        
        return tasks