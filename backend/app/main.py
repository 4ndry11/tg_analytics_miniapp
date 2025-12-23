from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import reports, metrics, auth, plans, alerts

# Create FastAPI app
app = FastAPI(
    title="Analytics Mini App API",
    description="Backend API for Telegram Mini App Analytics Dashboard",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router)
app.include_router(metrics.router)
app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(alerts.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Analytics Mini App API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "bitrix24_configured": bool(settings.BITRIX24_DOMAIN),
        "finmap_configured": bool(settings.FINMAP_API_KEY),
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development"
    )
