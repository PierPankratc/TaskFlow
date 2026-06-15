# db/create_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Движок для SQLite
engine = create_engine(url='sqlite:///todo.db', echo=True)

# Фабрика сессий
SessionLocal = sessionmaker(bind=engine)

# Зависимость для получения сессии в эндпоинтах
def get_db_connect():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db():
    Base.metadata.create_all(bind=engine)

create_db()