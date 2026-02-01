"""
MSME Agent Server - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database.connection import database

# Import routers
from api.routes.chat import router as chat_router
from api.routes.orders import router as orders_router
from api.routes.inventory import router as inventory_router
from api.routes.suppliers import router as suppliers_router
from api.routes.staff import router as staff_router
from api.routes.analytics import router as analytics_router
from api.routes.leads import router as leads_router
from whatsapp import router as whatsapp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    print("Starting MSME Agent Server...")
    await database.connect()
    print("Database connected successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await database.disconnect()


# Create FastAPI app
app = FastAPI(
    title="MSME Decision-Centric AI Agent System",
    description="LLM-powered agent orchestration for MSME operations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(orders_router)
app.include_router(inventory_router)
app.include_router(suppliers_router)
app.include_router(staff_router)
app.include_router(analytics_router)
app.include_router(leads_router)
app.include_router(whatsapp_router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "MSME Decision-Centric AI Agent System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "orders": "/api/orders",
            "inventory": "/api/inventory",
            "suppliers": "/api/suppliers",
            "staff": "/api/staff",
            "analytics": "/api/analytics",
            "leads": "/api/leads",
            "whatsapp": "/whatsapp/webhook"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        await database.db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
