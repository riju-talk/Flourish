import asyncio
import re
import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from ..core.config import settings
from ..db.firestore import FirestoreDB
from ..models.plant import Plant
from .perenual_service import PerenualService

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

        # Independent writes - create them concurrently rather than one-at-a-time.
        return list(await asyncio.gather(*[FirestoreDB.create_task(t) for t in to_create]))

    @staticmethod
    def _parse_frequency_days(frequency: Optional[str]) -> Optional[int]:
        """Best-effort extraction of a day count from Groq's free-text frequency string."""
        if not frequency:
            return None
        match = re.search(r'(\d+)', frequency)
        if not match:
            return None
        days = int(match.group(1))
        lowered = frequency.lower()
        if "week" in lowered:
            days *= 7
        elif "month" in lowered:
            days *= 30
        return days if days > 0 else None

    @staticmethod
    async def resolve_care_info(plant_name: str, groq_plant_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deterministic-first care resolution for "add to garden" and QA: Perenual (a real
        horticultural database) takes priority over Groq's free-text guess, which is
        only a fallback for whatever Perenual doesn't cover (no API key, no match, or a
        field Perenual doesn't report). groq_plant_info, if provided, is the dict
        already produced by GroqService.get_plant_info_agentic - passed in rather than
        re-fetched, so callers that already ran the agentic lookup don't pay for it twice.
        """
        perenual = await PerenualService.get_care_info(plant_name)

        watering_days = perenual.get("watering_frequency_days") if perenual else None
        sunlight = perenual.get("sunlight") if perenual else None
        scientific_name = perenual.get("scientific_name") if perenual else None
        native_habitat = perenual.get("native_habitat") if perenual else None

        if groq_plant_info:
            if watering_days is None:
                watering_days = PlantService._parse_frequency_days(
                    (groq_plant_info.get("watering") or {}).get("frequency")
                )
            if sunlight is None:
                sunlight = (groq_plant_info.get("sunlight") or {}).get("requirement")
            if not scientific_name:
                scientific_name = groq_plant_info.get("scientific_name")

        return {
            "watering_frequency_days": watering_days or 7,
            "sunlight_requirement": sunlight or "Bright, indirect",
            "scientific_name": scientific_name or "",
            "native_habitat": native_habitat,
            "source": "perenual" if perenual and perenual.get("watering_frequency_days") else "groq",
        }

    @staticmethod
    async def build_new_plant_document(
        user_id: str,
        plant_name: str,
        location: Optional[str] = None,
        groq_plant_info: Optional[Dict[str, Any]] = None,
        care_instructions: Any = "",
    ) -> Dict[str, Any]:
        """
        Assemble a complete plant document for FirestoreDB.create_plant - watering/
        sunlight resolved deterministically (see resolve_care_info), a real Unsplash
        photo, and every other field defaulted via the Plant model so nothing renders
        blank on the dashboard (health_score, plant_type, etc.) regardless of which
        creation path (autonomous add, recommendation accept) built it.
        """
        # The image search doesn't actually need Perenual's answer - it only needs a
        # plant/species name, and Groq's guess (if any) is already good enough for
        # that. Running both concurrently instead of sequentially shaves a full
        # network round-trip off "add to garden" latency.
        best_guess_species = (groq_plant_info or {}).get("scientific_name") or ""
        care, image_url = await asyncio.gather(
            PlantService.resolve_care_info(plant_name, groq_plant_info),
            PlantService.fetch_plant_image(plant_name, best_guess_species),
        )

        plant = Plant(
            name=plant_name,
            species=care["scientific_name"] or plant_name,
            scientific_name=care["scientific_name"] or None,
            location=location or "Indoor",
            sunlight_requirement=care["sunlight_requirement"],
            watering_frequency_days=care["watering_frequency_days"],
            native_habitat=care.get("native_habitat"),
            image_url=image_url,
            care_instructions=str(care_instructions) if care_instructions else "",
        )
        return plant.dict()