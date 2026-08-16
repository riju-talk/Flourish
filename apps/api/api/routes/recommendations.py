from fastapi import APIRouter, HTTPException, Depends
from ..core.auth import verify_firebase_token
from ..db.firestore import FirestoreDB
from ..services.groq_service import GroqService
from ..services.plant_service import PlantService
from ..services.email_service import EmailService
from ..services.notification_service import NotificationService

router = APIRouter()

@router.get("/")
async def get_recommendations(user_id: str = Depends(verify_firebase_token)):
    """List this user's pending personalized recommendations"""
    try:
        return await FirestoreDB.get_user_recommendations(user_id, status="pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_recommendations(
    count: int = 3,
    user_id: str = Depends(verify_firebase_token)
):
    """Trigger a fresh personalized recommendation pass (Groq agent + Tavily + weather)"""
    try:
        recommendations = await GroqService.generate_recommendations(user_id, count=count)

        if recommendations:
            title = "New plant picks ready!"
            message = f"We found {len(recommendations)} new plant(s) that could thrive in your garden."
            await NotificationService.notify(user_id, "recommendation_ready", title, message)
            await EmailService.send_for_notification(user_id, "recommendation_ready", title, message)

        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{rec_id}/accept")
async def accept_recommendation(
    rec_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Accept a recommendation: create the plant with real watering/sunlight (Perenual-
    first, same as the agentic add-plant flow - see PlantService.build_new_plant_document)
    and a real projected care schedule, then mark this recommendation accepted.
    """
    try:
        rec = await FirestoreDB.get_recommendation(rec_id)
        if not rec or rec.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        plant_name = rec.get("plant_name", "New Plant")
        plant_data = await PlantService.build_new_plant_document(
            user_id,
            plant_name=plant_name,
            groq_plant_info={"scientific_name": rec.get("scientific_name")},
            care_instructions=rec.get("reasoning", ""),
        )
        # A recommendation's image was already fetched from Unsplash at generation time
        # (see GroqService.generate_recommendations) - reuse it instead of searching again.
        if rec.get("image_url"):
            plant_data["image_url"] = rec["image_url"]

        plant = await FirestoreDB.create_plant(user_id, plant_data)
        tasks = await PlantService.create_projected_schedule(user_id, plant)
        await FirestoreDB.update_recommendation(rec_id, {"status": "accepted"})
        await GroqService.update_agent_profile_summary(user_id)

        return {"success": True, "plant": plant, "tasks": tasks}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{rec_id}/dismiss")
async def dismiss_recommendation(
    rec_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """Dismiss a recommendation and remember it so it isn't resurfaced"""
    try:
        rec = await FirestoreDB.get_recommendation(rec_id)
        if not rec or rec.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        await FirestoreDB.update_recommendation(rec_id, {"status": "dismissed"})

        profile = await FirestoreDB.get_profile(user_id)
        if profile:
            agent_profile = profile.get("agent_profile") or {}
            prefs = agent_profile.get("recommendation_preferences") or {"avoided_plants": [], "preferred_traits": []}
            plant_name = rec.get("plant_name")
            if plant_name and plant_name not in prefs.get("avoided_plants", []):
                prefs.setdefault("avoided_plants", []).append(plant_name)
            agent_profile["recommendation_preferences"] = prefs
            await FirestoreDB.update_profile(user_id, {"agent_profile": agent_profile})

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
