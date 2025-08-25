from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    priority: str = "medium"  # "low", "medium", "high"
    estimated_time: str = "5 minutes"