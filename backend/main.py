from fastapi import FastAPI
from backend.api import router as api_router
from backend.database.db import Base, engine
from backend.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nutrition Tracker API",
    description="API for tracking and analyzing food consumption and nutritional data",
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Nutrition Tracker API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_version": "1.0.0",
    }
