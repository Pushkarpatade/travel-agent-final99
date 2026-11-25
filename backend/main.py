import logging
from datetime import datetime
from fastapi import FastAPI, status, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.config import settings, validate_api_keys
from backend.database.session import SessionLocal
from backend.database.init_db import init_db
from backend.middleware.rate_limiter import RateLimiterMiddleware
from backend.middleware.security import SecurityHeadersMiddleware
from backend.api import auth, trips, planning, itinerary, budget, disruptions, chat, search, weather

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("travelpilot")

# Initialize DB tables on startup
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Trip Planning & Disruption Management Agent API"
)

# 1. Security Headers & Request-ID Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate Limiting Middleware
app.add_middleware(RateLimiterMiddleware)

# 3. CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Server-Timing", "Retry-After"]
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(trips.router, prefix=settings.API_V1_STR)
app.include_router(planning.router, prefix=settings.API_V1_STR)
app.include_router(itinerary.router, prefix=settings.API_V1_STR)
app.include_router(budget.router, prefix=settings.API_V1_STR)
app.include_router(disruptions.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(weather.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_liveness():
    """Liveness probe: verifies web server is alive."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }

@app.get("/ready")
def readiness_probe():
    """Readiness probe: validates database, AI provider, and LangSmith connectivity."""
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception as e:
        logger.error(f"Readiness probe DB failure: {e}")

    api_status = validate_api_keys()
    all_ready = db_ok and api_status.get("gemini") and api_status.get("tavily")

    return {
        "status": "ready" if all_ready else "degraded",
        "database_connected": db_ok,
        "services": api_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/mcp/tools")
def list_mcp_tools():
    """Model Context Protocol (MCP) tool discovery endpoint."""
    return {
        "server": "TravelPilot-AI",
        "protocol_version": "2.0",
        "tools": [
            {
                "name": "search_attractions",
                "description": "Discovers real-world attractions, dining hotspots, and ticket prices via Tavily web search.",
                "parameters": {"destination": "string", "interests": "array of strings"}
            },
            {
                "name": "check_weather_risks",
                "description": "Analyzes multi-day meteorological forecasts, evaluates precipitation probabilities, and detects rain conflicts.",
                "parameters": {"destination": "string", "days": "integer"}
            },
            {
                "name": "optimize_travel_budget",
                "description": "Calculates optimal expenditure breakdown across stay (45%), dining (25%), sightseeing (20%), and contingency (10%).",
                "parameters": {"total_budget": "number", "travel_style": "string", "currency": "string"}
            },
            {
                "name": "audit_travel_guardrails",
                "description": "Audits incoming trip request for international travel advisories, prompt injection defense, and budget feasibility.",
                "parameters": {"destination": "string", "budget": "number", "currency": "string"}
            },
            {
                "name": "ask_travelpilot",
                "description": "Asks the TravelPilot Gemini conversational travel assistant for real-time recommendations.",
                "parameters": {"destination": "string", "user_question": "string"}
            }
        ]
    }

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json", "health", "ready"]:
            raise HTTPException(status_code=404, detail="Endpoint not found")

        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
else:
    @app.get("/")
    def root():
        api_status = validate_api_keys()
        return {
            "status": "online",
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "api_keys_configured": api_status,
            "health": "/health",
            "ready": "/ready",
            "docs": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
