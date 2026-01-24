from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True) # UUID from Firebase/Auth
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    photo_url = Column(String)
    total_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    plants = relationship("Plant", back_populates="owner")
    tasks = relationship("CareTask", back_populates="user")

class Plant(Base):
    __tablename__ = "plants"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("profiles.id"))
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
    last_watered = Column(DateTime(timezone=True))
    last_fertilized = Column(DateTime(timezone=True))
    last_health_check = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    owner = relationship("Profile", back_populates="plants")
    care_tasks = relationship("CareTask", back_populates="plant")
    health_checks = relationship("HealthCheck", back_populates="plant")

class CareTask(Base):
    __tablename__ = "care_tasks"
    id = Column(String, primary_key=True)
    plant_id = Column(String, ForeignKey("plants.id"))
    user_id = Column(String, ForeignKey("profiles.id"))
    task_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    priority = Column(String, default="medium")
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    points = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    plant = relationship("Plant", back_populates="care_tasks")
    user = relationship("Profile", back_populates="tasks")

class HealthCheck(Base):
    __tablename__ = "health_checks"
    id = Column(String, primary_key=True)
    plant_id = Column(String, ForeignKey("plants.id"))
    check_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text)
    image_url = Column(String)
    symptoms = Column(ARRAY(String))
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    plant = relationship("Plant", back_populates="health_checks")
