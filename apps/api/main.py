from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime, timedelta
import httpx
import os
from groq import Groq
import firebase_admin
from firebase_admin import credentials, firestore, storage
import base64
from io import BytesIO
from PIL import Image
import requests

# Initialize FastAPI
app = FastAPI(title="PlantMind AI", description="Proactive AI Plant Care Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase (you'll need to add your config)
# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# Initialize Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Pydantic models
class Plant(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    species: str
    location: str
    sunlight_requirement: str
    watering_frequency_days: int
    fertilizing_frequency_days: Optional[int] = 30
    health_status: str = "Healthy"
    health_score: float = 100.0
    last_watered: Optional[datetime] = None
    last_fertilized: Optional[datetime] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = datetime.now()

class HealthCheckItem(BaseModel):
    id: str
    plant_id: str
    check_type: str  # "leaves", "soil", "growth", "pests"
    status: str  # "good", "concerning", "bad"
    notes: Optional[str] = None
    image_url: Optional[str] = None
    checked_at: datetime = datetime.now()

class CareTask(BaseModel):
    id: Optional[str] = None
    plant_id: str
    task_type: str  # "watering", "fertilizing", "pruning", "checking"
    title: str
    description: Optional[str] = None
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    status: str = "pending"  # "pending", "completed", "skipped"
    ai_generated: bool = True

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    image_url: Optional[str] = None
    timestamp: datetime = datetime.now()

class PlantAnalysis(BaseModel):
    plant_id: str
    health_score: float
    issues: List[str]
    recommendations: List[str]
    next_actions: List[str]
    analyzed_at: datetime = datetime.now()

# AI Agent System Prompt
PLANT_AI_SYSTEM_PROMPT = """You are PlantMind, an advanced AI plant care agent. You are proactive, knowledgeable, and caring about plant health. Your responsibilities include:

1. PROACTIVE MONITORING: Analyze daily health check data and predict issues before they become serious
2. SMART SCHEDULING: Generate optimal care schedules based on plant species, environment, and health status
3. HEALTH ANALYSIS: Evaluate plant health from images and user reports, providing actionable insights
4. PERSONALIZED ADVICE: Give specific, actionable advice tailored to each plant and user's situation
5. PREVENTIVE CARE: Suggest preventive measures to maintain optimal plant health

When analyzing plant health:
- Consider species-specific needs
- Factor in environmental conditions
- Look for early warning signs
- Provide specific, actionable recommendations
- Suggest optimal timing for interventions

Be encouraging, informative, and always focus on helping plants thrive."""

# Utility functions
async def fetch_plant_image(plant_name: str, species: str) -> str:
    """Fetch a plant image from Unsplash API"""
    try:
        query = f"{plant_name} {species} plant"
        url = f"https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": 1,
            "client_id": os.getenv("UNSPLASH_ACCESS_KEY", "demo")
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

async def analyze_plant_health(plant: Plant, health_checks: List[HealthCheckItem]) -> PlantAnalysis:
    """AI-powered plant health analysis"""
    
    # Prepare context for AI analysis
    context = f"""
    Plant: {plant.name} ({plant.species})
    Location: {plant.location}
    Sunlight: {plant.sunlight_requirement}
    Last watered: {plant.last_watered}
    Last fertilized: {plant.last_fertilized}
    Current health status: {plant.health_status}
    
    Recent health checks:
    """
    
    for check in health_checks[-5:]:  # Last 5 checks
        context += f"- {check.check_type}: {check.status} ({check.notes or 'No notes'})\n"
    
    prompt = f"""
    {PLANT_AI_SYSTEM_PROMPT}
    
    Analyze this plant's health and provide:
    1. Health score (0-100)
    2. Current issues (if any)
    3. Specific recommendations
    4. Next actions to take
    
    Plant data:
    {context}
    
    Respond in JSON format:
    {{
        "health_score": float,
        "issues": [list of current issues],
        "recommendations": [list of specific recommendations],
        "next_actions": [list of immediate actions needed]
    }}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        analysis_data = json.loads(response.choices[0].message.content)
        
        return PlantAnalysis(
            plant_id=plant.id,
            health_score=analysis_data["health_score"],
            issues=analysis_data["issues"],
            recommendations=analysis_data["recommendations"],
            next_actions=analysis_data["next_actions"]
        )
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return PlantAnalysis(
            plant_id=plant.id,
            health_score=75.0,
            issues=["Unable to perform AI analysis"],
            recommendations=["Continue regular care routine"],
            next_actions=["Monitor plant closely"]
        )

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
            scheduled_date=task_date
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
                scheduled_date=task_date
            ))
    
    # Generate health check schedule
    for i in range(7):  # Daily checks for a week
        task_date = now + timedelta(days=i)
        tasks.append(CareTask(
            plant_id=plant.id,
            task_type="checking",
            title=f"Health check for {plant.name}",
            description="Daily health monitoring",
            scheduled_date=task_date
        ))
    
    return tasks

# API Routes

@app.get("/")
async def root():
    return {"message": "PlantMind AI - Your Proactive Plant Care Agent"}

@app.post("/plants/")
async def create_plant(plant: Plant):
    """Create a new plant with AI-generated care schedule"""
    try:
        # Generate unique ID
        plant.id = f"plant_{datetime.now().timestamp()}"
        
        # Fetch plant image
        plant.image_url = await fetch_plant_image(plant.name, plant.species)
        
        # Generate initial care schedule
        care_tasks = await generate_care_schedule(plant)
        
        # In a real app, save to Firebase here
        # doc_ref = db.collection('plants').document(plant.id)
        # doc_ref.set(plant.dict())
        
        return {
            "plant": plant,
            "care_schedule": care_tasks,
            "message": "Plant added successfully with AI-generated care schedule"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plants/{user_id}")
async def get_user_plants(user_id: str):
    """Get all plants for a user"""
    # In a real app, fetch from Firebase
    # plants_ref = db.collection('plants').where('user_id', '==', user_id)
    # plants = [doc.to_dict() for doc in plants_ref.stream()]
    
    # Mock data for now
    return {"plants": [], "message": "Plants retrieved successfully"}

@app.post("/plants/{plant_id}/health-check")
async def submit_health_check(plant_id: str, health_check: HealthCheckItem):
    """Submit daily health check and get AI analysis"""
    try:
        health_check.plant_id = plant_id
        health_check.id = f"check_{datetime.now().timestamp()}"
        
        # In a real app, save to Firebase and fetch plant data
        # Mock plant data for now
        mock_plant = Plant(
            id=plant_id,
            user_id="user123",
            name="Mock Plant",
            species="Mock Species",
            location="Indoor",
            sunlight_requirement="Bright indirect",
            watering_frequency_days=3
        )
        
        # Get recent health checks (mock data)
        recent_checks = [health_check]
        
        # AI analysis
        analysis = await analyze_plant_health(mock_plant, recent_checks)
        
        return {
            "health_check": health_check,
            "analysis": analysis,
            "message": "Health check submitted and analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/{user_id}")
async def get_dashboard_data(user_id: str):
    """Get comprehensive dashboard data with AI insights"""
    try:
        # In a real app, fetch from Firebase
        # Mock data for demonstration
        
        plants_data = []  # Fetch user's plants
        overall_health_score = 85.0  # Calculate from all plants
        
        # Generate happiness indicator
        happiness_level = "happy" if overall_health_score > 80 else "concerned" if overall_health_score > 60 else "worried"
        
        # Get today's tasks
        today_tasks = []  # Fetch today's pending tasks
        
        # AI insights
        ai_insights = [
            "Your Monstera is showing excellent growth patterns!",
            "Consider increasing humidity for your Fiddle Leaf Fig",
            "Perfect watering schedule maintained this week"
        ]
        
        return {
            "plants": plants_data,
            "overall_health_score": overall_health_score,
            "happiness_level": happiness_level,
            "today_tasks": today_tasks,
            "ai_insights": ai_insights,
            "stats": {
                "total_plants": len(plants_data),
                "healthy_plants": len([p for p in plants_data if p.get("health_score", 0) > 80]),
                "tasks_completed_today": 0,
                "streak_days": 7
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_ai(messages: List[ChatMessage]):
    """Multi-modal chat with PlantMind AI"""
    try:
        # Prepare messages for Groq
        groq_messages = [{"role": "system", "content": PLANT_AI_SYSTEM_PROMPT}]
        
        for msg in messages:
            groq_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=groq_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "response": ai_response,
            "timestamp": datetime.now(),
            "suggestions": [
                "Tell me about my plant's health",
                "What should I do today?",
                "Help me identify this plant issue"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-image")
async def analyze_plant_image(image_data: str, plant_id: Optional[str] = None):
    """Analyze plant image for health assessment"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(BytesIO(image_bytes))
        
        # In a real implementation, you'd use a vision model here
        # For now, return mock analysis
        
        analysis = {
            "health_assessment": "Plant appears healthy with vibrant green leaves",
            "issues_detected": [],
            "recommendations": [
                "Continue current care routine",
                "Monitor for any changes in leaf color"
            ],
            "confidence": 0.85
        }
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{user_id}/today")
async def get_today_tasks(user_id: str):
    """Get today's AI-generated tasks"""
    try:
        # In a real app, fetch from Firebase
        today = datetime.now().date()
        
        # Mock tasks
        tasks = [
            {
                "id": "task1",
                "plant_name": "Monstera Deliciosa",
                "task_type": "watering",
                "title": "Water Monstera",
                "priority": "high",
                "estimated_time": "5 minutes"
            },
            {
                "id": "task2",
                "plant_name": "Snake Plant",
                "task_type": "checking",
                "title": "Health check for Snake Plant",
                "priority": "medium",
                "estimated_time": "2 minutes"
            }
        ]
        
        return {"tasks": tasks, "date": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str, notes: Optional[str] = None):
    """Mark task as completed"""
    try:
        # In a real app, update Firebase
        completion_time = datetime.now()
        
        return {
            "task_id": task_id,
            "completed_at": completion_time,
            "notes": notes,
            "message": "Task completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task for proactive monitoring
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    asyncio.create_task(proactive_monitoring())

async def proactive_monitoring():
    """Continuous AI monitoring of all plants"""
    while True:
        try:
            # In a real app, fetch all plants and analyze their health
            # Generate alerts and recommendations
            # Update care schedules based on plant responses
            
            print("🤖 PlantMind AI: Monitoring all plants...")
            await asyncio.sleep(3600)  # Check every hour
        except Exception as e:
            print(f"Error in proactive monitoring: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)