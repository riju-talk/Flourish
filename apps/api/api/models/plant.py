from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Plant(BaseModel):
    id: Optional[str] = None
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

class PlantAnalysis(BaseModel):
    plant_id: str
    health_score: float
    issues: List[str]
    recommendations: List[str]
    next_actions: List[str]
    analyzed_at: datetime = datetime.now()