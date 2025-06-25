import uvicorn
from backend.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.ENV in ["test", "dev"],
        log_level="debug" if settings.ENV in ["test", "dev"] else None,
    )
