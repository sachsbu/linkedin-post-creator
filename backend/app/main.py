import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api.stories import router as stories_router
from app.api.posts import router as posts_router
from app.api.health import router as health_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SQLite database...")
    await init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Automated LinkedIn Tech Post Generator backend service.",
    lifespan=lifespan
)

# Enable CORS for local desktop React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated output images & files
app.mount("/output", StaticFiles(directory=str(settings.OUTPUT_FOLDER)), name="output")

# Include Routers
app.include_router(health_router)
app.include_router(stories_router)
app.include_router(posts_router)

