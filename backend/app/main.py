from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .db.database import init_db
from .api import calendars

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Time Ledger API ready")
    yield
    # Shutdown
    logger.info("Shutting down Time Ledger API")

app = FastAPI(
    title="Time Ledger API",
    description="Apple Calendar Analyzer — CalDAV sync + time tallying",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for local frontend and Vercel frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "https://frontend-zeta-eight-35.vercel.app",
        "https://frontend-cj98khh4q-hypekn1ghts-projects.vercel.app",
        "https://frontend-gyuvrlv7j-hypekn1ghts-projects.vercel.app",
        "https://frontend-obo5x20xs-hypekn1ghts-projects.vercel.app",
        "https://dist-liard-alpha-92.vercel.app",
        "https://dist-50lq6uftm-hypekn1ghts-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calendars.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Time Ledger API"}
