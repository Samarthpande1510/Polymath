from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
from pm.db.models import Base
import os

def _get_engine():
    load_dotenv(Path.home() / ".polymath" / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Polymath not initialized. Run 'pm init' first.")
    return create_engine(url)

def get_session():
    return sessionmaker(autoflush=False, autocommit=False, bind=_get_engine())()

class LocalSession:
    def __new__(cls):
        return get_session()

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()