from fastapi import FastAPI 
from app.routes import players, teams, advanced_stats
from app.utils.error_handler import register_exception_handlers
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nba_api")

app = FastAPI(
    title = "NBA Data Analyst API",
    description = "API for NBA Data Analyst project with comprehensive NBA player and team statistics",
    version = "0.2.0",
)

# Register all API routes
app.include_router(players.router, prefix="/api/v1", tags=["players"])
# app.include_router(teams.router, prefix="/api/v1", tags=["teams"])
# app.include_router(advanced_stats.router, prefix="/api/v1", tags=["advanced"])

# Register exception handlers
register_exception_handlers(app)

@app.get("/") 
def read_root():
    return {
        "message": "Welcome to the NBA Data Analyst API!",
        "documentation": "/docs",
        "version": "0.2.0"
    }

@app.on_event("startup")
async def startup_event():
    """Log when the application starts up."""
    logger.info("NBA Data Analyst API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Log when the application shuts down."""
    logger.info("NBA Data Analyst API shut down")