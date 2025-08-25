from fastapi import APIRouter
from typing import List
from ..models.plant import Plant

router = APIRouter()

# In-memory storage (replace with database later)
from .plants import plants_db

@router.get("/")
async def get_dashboard_data():
    """Get comprehensive dashboard data with AI insights"""
    try:
        plants_data = list(plants_db.values())
        
        # Calculate overall health score
        if plants_data:
            overall_health_score = sum(plant.health_score for plant in plants_data) / len(plants_data)
        else:
            overall_health_score = 100.0
        
        # Generate happiness indicator
        happiness_level = "happy" if overall_health_score > 80 else "concerned" if overall_health_score > 60 else "worried"
        
        # AI insights based on plant health
        ai_insights = []
        healthy_plants = [p for p in plants_data if p.health_score > 80]
        concerning_plants = [p for p in plants_data if p.health_score <= 60]
        
        if len(healthy_plants) == len(plants_data) and plants_data:
            ai_insights.append("🌟 All your plants are thriving! Great job!")
        elif concerning_plants:
            ai_insights.append(f"⚠️ {len(concerning_plants)} plant(s) need attention")
        
        if plants_data:
            ai_insights.append(f"📊 Average plant health: {overall_health_score:.0f}%")
            ai_insights.append("🤖 AI monitoring active - schedules optimized daily")
        
        return {
            "plants": plants_data,
            "overall_health_score": overall_health_score,
            "happiness_level": happiness_level,
            "ai_insights": ai_insights,
            "stats": {
                "total_plants": len(plants_data),
                "healthy_plants": len(healthy_plants),
                "tasks_completed_today": 0,  # Implement task tracking
                "streak_days": 7  # Implement streak tracking
            }
        }
    except Exception as e:
        return {
            "plants": [],
            "overall_health_score": 100.0,
            "happiness_level": "happy",
            "ai_insights": ["Welcome to PlantMind! Add your first plant to get started."],
            "stats": {
                "total_plants": 0,
                "healthy_plants": 0,
                "tasks_completed_today": 0,
                "streak_days": 0
            }
        }