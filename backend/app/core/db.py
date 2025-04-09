from sqlmodel import SQLModel, create_engine
from core.models import User, UserCreate
from config.config import settings
import logging

from app.core.session import engine # Import engine directly
from app.core.models import User
from app.core import crud
from sqlmodel import Session, select

def init_db():
    """
    Initializes the database: creates the first superuser if it doesn't exist.
    Assumes database tables are already created by Alembic.
    """
    
    with Session(engine) as session:
        # Check if the superuser already exists
        superuser = session.exec(select(User).where(User.email == settings.DB_SUPERUSER_EMAIL)).first()   
        if not superuser:
            logging.log("Intial user not found, creating...")
            intial_user =  UserCreate(settings.DB_SUPERUSER_USERNAME, settings.DB_SUPERUSER_PASSWORD, settings.DB_SUPERUSER_EMAIL)
            superuser = crud.create_user(session=session, user_create=intial_user)
            logging.log("Intial user created")
        else:
            logging.log("Intial user already exists") 