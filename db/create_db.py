from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.config import DATABASE_URL, SQL_ECHO
from db.models import Base

engine = create_engine(url=DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(bind=engine)


def get_db_connect():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db():
    Base.metadata.create_all(bind=engine)
