from sqlalchemy import create_all_engines
from sqlalchemy.orm import sessionmaker
from .db_models import Base
from ..core.config import settings

# Database setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

def get_db():
    from sqlalchemy import create_engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from sqlalchemy import create_engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
