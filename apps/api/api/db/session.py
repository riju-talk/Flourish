from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import settings
import os

# Database setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL or "postgresql://user:password@localhost:5432/flourish"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from ..models.db_models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
