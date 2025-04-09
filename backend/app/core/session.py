from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker

from app.config.config import settings # Assuming your config is here

# Use the database URL from your settings
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function to get a DB session
def get_session() -> Generator[Session, None, None]:
    """
    Dependency function that yields a SQLModel session.
    Ensures the session is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
