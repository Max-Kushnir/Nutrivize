from typing import Generator
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

load_dotenv()

user_name = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PW")
db = os.environ.get("POSTGRES_DB")
host = os.environ.get("POSTGRES_HOST", "localhost")
port = os.environ.get("POSTGRES_PORT", 5432)
url = f"postgresql://{user_name}:{password}@{host}:{port}/{db}"

engine = create_engine(url)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(engine)

def get_db() -> Generator:
    db = Session()
    try:
        yield db
    finally:
        db.close()

    