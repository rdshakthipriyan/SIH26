"""
MediKiosk FastAPI Application.

AI-assisted multilingual patient intake system for Indian public hospitals.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import sessions, clinical_history, endpoints
from app.api.v1 import byod


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Initializing MediKiosk backend...")
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down MediKiosk backend...")


app = FastAPI(
    title="MediKiosk API",
    description="AI-assisted multilingual patient intake system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """API root."""
    return {
        "name": "MediKiosk API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "speech_provider": settings.SPEECH_PROVIDER,
        "tts_provider": settings.TTS_PROVIDER,
        "ocr_provider": settings.OCR_PROVIDER
    }


# Include routers
app.include_router(
    sessions.router,
    prefix=f"{settings.API_V1_PREFIX}/sessions",
    tags=["sessions"]
)

app.include_router(
    clinical_history.router,
    prefix=settings.API_V1_PREFIX,
    tags=["clinical_history"]
)

app.include_router(
    endpoints.ayush_router,
    prefix=settings.API_V1_PREFIX,
    tags=["ayush"]
)

app.include_router(
    endpoints.ocr_router,
    prefix=settings.API_V1_PREFIX,
    tags=["ocr"]
)

app.include_router(
    endpoints.queue_router,
    prefix=settings.API_V1_PREFIX,
    tags=["queue"]
)

app.include_router(
    endpoints.doctor_router,
    prefix=settings.API_V1_PREFIX,
    tags=["doctor"]
)

app.include_router(
    endpoints.fhir_router,
    prefix=settings.API_V1_PREFIX,
    tags=["fhir"]
)

# BYOD router
app.include_router(
    byod.router,
    prefix=f"{settings.API_V1_PREFIX}/byod",
    tags=["byod"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
