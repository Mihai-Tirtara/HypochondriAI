import logging
import os

from sqlmodel import Session, select

from app.config.config import settings
from app.core.dependencies import engine  # Import engine directly
from app.core.models import User, UserCreate
from app.db.crud import create_user

logger = logging.getLogger(__name__)


def init_db():
    """
    Initializes the database: creates the first superuser if it doesn't exist.
    Assumes database tables are already created by Alembic.
    """
    with Session(engine) as session:
        # Check if the superuser already exists
        superuser = session.exec(
            select(User).where(User.email == settings.DB_SUPERUSER_EMAIL)
        ).first()
        if not superuser and not os.getenv("TESTING"):
            logger.info("Intial user not found, creating...")
            intial_user = UserCreate(
                username=settings.DB_SUPERUSER_USERNAME,
                password=settings.DB_SUPERUSER_PASSWORD,
                email=settings.DB_SUPERUSER_EMAIL,
            )
            superuser = create_user(session=session, user_create=intial_user)
            logger.info("Intial user created")
        else:
            logger.info("Intial user already exists")
