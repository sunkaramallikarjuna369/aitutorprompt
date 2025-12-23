from .auth.router import router as auth_router
from .curriculum.router import router as curriculum_router
from .content.router import router as content_router
from .visualization.router import router as visualization_router
from .visualization_orchestrator.router import router as visualization_orchestrator_router
from .rwal.router import router as rwal_router
from .quiz.router import router as quiz_router
from .progress.router import router as progress_router
from .recommendation.router import router as recommendation_router
from .pdf_ingestion.router import router as pdf_ingestion_router
from .rag_agent.router import router as rag_agent_router
from .firebase_users.router import router as firebase_users_router

__all__ = [
    "auth_router",
    "curriculum_router", 
    "content_router",
    "visualization_router",
    "visualization_orchestrator_router",
    "rwal_router",
    "quiz_router",
    "progress_router",
    "recommendation_router",
    "pdf_ingestion_router",
    "rag_agent_router",
    "firebase_users_router"
]
