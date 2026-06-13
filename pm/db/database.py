from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from pm.db.models import Base

DATABASE_URL = f"sqlite:///{Path.home()}/.polymath/polymath.db"

def _get_engine():
    return create_engine(DATABASE_URL)

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