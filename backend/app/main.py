from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Import routes AFTER app is defined ───────────────────────────────────────
from app.database.connection import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Deepfake Detector API...")
    await connect_to_mongo()
    yield
    print("👋 Shutting down...")
    await close_mongo_connection()

# ─── Create app FIRST ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Deepfake Detector API",
    description="AI-powered deepfake detection",
    version="1.0.0",
    lifespan=lifespan
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
allowed_origins = [
    "https://jovial-blancmange-ed4f77.netlify.app",
    "https://deepfake-detector-15h.pages.dev",   # Cloudflare Pages
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

extra_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + extra_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static files ─────────────────────────────────────────────────────────────
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# ─── Routes AFTER app is created ──────────────────────────────────────────────
from app.routes import detect, history

app.include_router(detect.router, prefix="/api", tags=["Detection"])
app.include_router(history.router, prefix="/api", tags=["History"])

# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return JSONResponse(content={
        "status": "online",
        "message": "Deepfake Detector API is running",
        "version": "1.0.0"
    })

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})