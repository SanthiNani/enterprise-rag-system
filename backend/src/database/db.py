from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from .models import Base

# Create engine
engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
