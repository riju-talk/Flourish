from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) # UUID from Firebase/Auth
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    photo_url = Column(String)
    total_score = Column(Integer, default=0)
    level = Column(Integer, default=1)
    tasks_completed = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True))
    achievements = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    plants = relationship("Plant", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("CareTask", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class Plant(Base):
    __tablename__ = "plants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    scientific_name = Column(String)
    plant_type = Column(String, default="indoor")
    size = Column(String, default="medium")
    toxicity = Column(String, default="non-toxic")
    location = Column(String, default="Living Room")
    sunlight_requirement = Column(String)
    watering_frequency_days = Column(Integer, default=7)
    fertilizer_frequency_days = Column(Integer, default=30)
    health_status = Column(String, default="Healthy")
    health_score = Column(Float, default=100.0)
    image_url = Column(String)
    care_instructions = Column(JSON)
    last_watered = Column(DateTime(timezone=True))
    last_fertilized = Column(DateTime(timezone=True))
    last_health_check = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    owner = relationship("Profile", back_populates="plants")
    care_tasks = relationship("CareTask", back_populates="plant", cascade="all, delete-orphan")
    health_checks = relationship("HealthCheck", back_populates="plant", cascade="all, delete-orphan")

class CareTask(Base):
    __tablename__ = "care_tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id = Column(String, ForeignKey("plants.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"))
    task_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    priority = Column(String, default="medium")
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    points = Column(Integer, default=10)
    recurring = Column(Boolean, default=False)
    recurrence_days = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    plant = relationship("Plant", back_populates="care_tasks")
    user = relationship("Profile", back_populates="tasks")

class HealthCheck(Base):
    __tablename__ = "health_checks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plant_id = Column(String, ForeignKey("plants.id", ondelete="CASCADE"))
    check_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text)
    image_url = Column(String)
    symptoms = Column(ARRAY(String))
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    plant = relationship("Plant", back_populates="health_checks")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="info")  # info, reminder, achievement, alert
    read = Column(Boolean, default=False)
    action_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("Profile", back_populates="notifications")
    
    plant = relationship("Plant", back_populates="health_checks")
