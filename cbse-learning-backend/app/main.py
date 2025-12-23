import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .config import settings
from .services import (
    auth_router,
    curriculum_router,
    content_router,
    visualization_router,
    visualization_orchestrator_router,
    rwal_router,
    quiz_router,
    progress_router,
    recommendation_router,
    pdf_ingestion_router,
    rag_agent_router,
    firebase_users_router
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CBSE Learning Platform API - An interactive learning platform for CBSE students with adaptive quizzes and real-world applications based on Situated Cognition Theory (SGT)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth_router)
app.include_router(curriculum_router)
app.include_router(content_router)
app.include_router(visualization_router)
app.include_router(visualization_orchestrator_router)
app.include_router(rwal_router)
app.include_router(quiz_router)
app.include_router(progress_router)
app.include_router(recommendation_router)
app.include_router(pdf_ingestion_router)
app.include_router(rag_agent_router)
app.include_router(firebase_users_router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api")
async def api_root():
    return {
        "message": "Welcome to CBSE Learning Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "services": [
            {"name": "Authentication", "prefix": "/auth"},
            {"name": "Curriculum", "prefix": "/curriculum"},
            {"name": "Content", "prefix": "/content"},
            {"name": "Visualization", "prefix": "/visualization"},
            {"name": "Visualization Orchestrator (AI-Driven)", "prefix": "/visualization-orchestrator"},
            {"name": "Real-World Applications (SGT)", "prefix": "/rwal"},
            {"name": "Quiz & Assessment", "prefix": "/quiz"},
            {"name": "Progress Tracking", "prefix": "/progress"},
            {"name": "Recommendations", "prefix": "/recommendations"},
            {"name": "PDF Ingestion (CBSE Content)", "prefix": "/pdf-ingestion"},
            {"name": "RAG Agent (PDF Q&A + Visualization)", "prefix": "/rag-agent"},
            {"name": "Firebase User Management", "prefix": "/firebase-users"}
        ]
    }

# Serve frontend static files if they exist
FRONTEND_DIR = Path(__file__).parent.parent.parent / "cbse-learning-frontend" / "dist"

if FRONTEND_DIR.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # Serve index.html for all non-API routes (SPA routing)
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to CBSE Learning Platform API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "note": "Frontend not found. Visit /docs for API documentation."
        }
