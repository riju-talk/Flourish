from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PlantSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class PlantType(str, Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    BOTH = "both"

class ToxicityLevel(str, Enum):
    NON_TOXIC = "non-toxic"
    MILDLY_TOXIC = "mildly-toxic"
    TOXIC = "toxic"
    HIGHLY_TOXIC = "highly-toxic"

class Plant(BaseModel):
    id: Optional[str] = None
    name: str
    species: str
    scientific_name: Optional[str] = None

    # Auto-detected properties
    plant_type: PlantType = PlantType.INDOOR
    size: PlantSize = PlantSize.MEDIUM
    toxicity: ToxicityLevel = ToxicityLevel.NON_TOXIC

    # Location and environment
    location: str = "Living Room"
    preferred_locations: List[str] = []
    sunlight_requirement: str = "Medium indirect light"
    temperature_range: Dict[str, int] = {"min": 18, "max": 24}  # Celsius

    # Care requirements
    watering_frequency_days: int = 7
    watering_amount: str = "Moderate"
    soil_type: str = "Well-draining potting mix"
    humidity_preference: str = "Moderate (40-60%)"

    # Fertilizer and chemicals
    fertilizer_type: str = "Balanced houseplant fertilizer"
    fertilizer_frequency_days: int = 30
    fertilizer_season: str = "Growing season (Spring-Summer)"
    pesticide_needs: List[str] = []
    common_pests: List[str] = []

    # Health and monitoring
    health_status: str = "Healthy"
    health_score: float = 100.0
    last_watered: Optional[datetime] = None
    last_fertilized: Optional[datetime] = None
    last_health_check: Optional[datetime] = None

    # Media and info
    image_url: Optional[str] = None
    care_instructions: str = ""
    fun_facts: List[str] = []

    # Metadata
    notes: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    # Autonomous tracking
    days_since_watering: int = 0
    days_since_fertilizing: int = 0
    needs_watering: bool = False
    needs_fertilizing: bool = False

class HealthCheckItem(BaseModel):
    id: str
    plant_id: str
    check_type: str  # "leaves", "soil", "growth", "pests", "general"
    status: str  # "excellent", "good", "fair", "poor", "critical"
    notes: Optional[str] = None
    image_url: Optional[str] = None
    symptoms: List[str] = []
    checked_at: datetime = datetime.now()

class PlantAnalysis(BaseModel):
    plant_id: str
    health_score: float
    issues: List[str]
    recommendations: List[str]
    next_actions: List[str]
    care_adjustments: Dict[str, Any] = {}
    analyzed_at: datetime = datetime.now()

class CareSchedule(BaseModel):
    plant_id: str
    schedule_type: str  # "watering", "fertilizing", "pesticide", "health_check"
    title: str
    description: str
    scheduled_date: datetime
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    estimated_time: str = "5 minutes"
    completed: bool = False
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

class PlantInventory(BaseModel):
    """Complete plant profile with all autonomous data"""
    plant: Plant
    care_schedule: List[CareSchedule]
    health_history: List[HealthCheckItem]
    inventory_summary: Dict[str, Any]