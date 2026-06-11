from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
from pm.db.models import Base
import os

env_path = Path.home() / ".polymath" / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
LocalSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()