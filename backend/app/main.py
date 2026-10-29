from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import api_router
from app.database import engine, Base

# Create tables if not exist (seed scripts will populate)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Explainable Compensation Disparity Analysis & Pay Equity Review System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.APP_NAME,
        "documentation": "/docs",
        "health": "/health",
        "api_v1": "/api/v1"
    }

app.include_router(api_router)
