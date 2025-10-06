from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.auth.routers import router as auth_router
from app.users.routers import router as users_router
from app.admin.routers import router as admin_router
import time
import logging
import os

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Configure logging based on environment
log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Only include test router in development
if ENVIRONMENT == "development":
    from app.test.routers import router as test_router

app = FastAPI(title="SeatDuty Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Startup event with database connection retry and initialization."""
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})")
            Base.metadata.create_all(bind=engine)
            logger.info("Database connection successful and tables created")
            
            # Initialize database with default admin user
            from app.core.init_db import init_db
            init_db()
            
            break
        except Exception as e:
            logger.warning(f"Database connection failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after all retries")
                raise


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "Hello, world from backend"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)

# Only include test router in development
if ENVIRONMENT == "development":
    app.include_router(test_router)
    logger.info("🧪 Test endpoints enabled (development mode)")
else:
    logger.info("🔒 Test endpoints disabled (production mode)")

