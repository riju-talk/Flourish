import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.config import settings
from ..db.firestore import FirestoreDB

class PlantService:
    @staticmethod
    async def fetch_plant_image(plant_name: str, species: str) -> str:
        """Fetch a plant image from Unsplash API, used when adding a plant to the garden"""
        try:
            query = f"{plant_name} {species} plant"
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": 1,
                "client_id": settings.UNSPLASH_ACCESS_KEY or "demo"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data["results"]:
                        photo = data["results"][0]
                        download_location = photo.get("links", {}).get("download_location")
                        await PlantService._track_unsplash_download(client, download_location)
                        return photo["urls"]["regular"]
                else:
                    print(f"Unsplash API returned {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"Error fetching image: {e}")

        # Fallback to a default plant image
        return "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop"

    @staticmethod
    async def _track_unsplash_download(client: httpx.AsyncClient, download_location: Optional[str]) -> None:
        """
        Unsplash API Guidelines require pinging a photo's download_location whenever
        it's actually used (not just searched) - see https://unsplash.com/documentation#track-a-photo-download.
        Best-effort: a tracking failure should never block adding the plant.
        """
        if not download_location or not settings.UNSPLASH_ACCESS_KEY:
            return
        try:
            await client.get(download_location, params={"client_id": settings.UNSPLASH_ACCESS_KEY})
        except Exception:
            pass

    @staticmethod
    async def create_projected_schedule(
        user_id: str,
        plant: dict,
        types: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Persist a real forward-looking care schedule (several upcoming watering/
        fertilizing occurrences, not just a single "due now" task) so the Calendar has
        actual future dates to render as soon as a plant is added. Called by both the
        agentic autonomous-create flow and the manual "generate tasks" endpoint.
        """
        types = types or ["watering", "fertilizing"]
        now = datetime.now()
        plant_id = plant["id"]
        plant_name = plant.get("name", "your plant")
        to_create = []

        if "watering" in types:
            watering_days = plant.get("watering_frequency_days") or 7
            occurrences = max(1, min(6, -(-30 // watering_days)))  # cover ~30 days ahead, capped
            for i in range(occurrences):
                due = now + timedelta(days=i * watering_days)
                to_create.append({
                    "user_id": user_id,
                    "plant_id": plant_id,
                    "task_type": "watering",
                    "title": f"Water {plant_name}",
                    "description": plant.get("watering_amount") or "Water thoroughly",
                    "due_date": due.isoformat(),
                    "priority": "high" if i == 0 else "medium",
                    "completed": False,
                    "points": 10,
                    "recurring": True,
                    "recurring_days": watering_days
                })

        if "fertilizing" in types:
            fertilizer_days = plant.get("fertilizer_frequency_days") or 30
            occurrences = max(1, min(4, -(-90 // fertilizer_days)))  # cover ~90 days ahead, capped
            for i in range(occurrences):
                due = now + timedelta(days=i * fertilizer_days)
                to_create.append({
                    "user_id": user_id,
                    "plant_id": plant_id,
                    "task_type": "fertilizing",
                    "title": f"Fertilize {plant_name}",
                    "description": plant.get("fertilizer_type") or "Apply fertilizer",
                    "due_date": due.isoformat(),
                    "priority": "low",
                    "completed": False,
                    "points": 15,
                    "recurring": True,
                    "recurring_days": fertilizer_days
                })

        return [await FirestoreDB.create_task(t) for t in to_create]