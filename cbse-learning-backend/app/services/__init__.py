from .auth.router import router as auth_router
from .curriculum.router import router as curriculum_router
from .content.router import router as content_router
from .visualization.router import router as visualization_router
from .rwal.router import router as rwal_router
from .quiz.router import router as quiz_router
from .progress.router import router as progress_router
from .recommendation.router import router as recommendation_router

__all__ = [
    "auth_router",
    "curriculum_router", 
    "content_router",
    "visualization_router",
    "rwal_router",
    "quiz_router",
    "progress_router",
    "recommendation_router"
]
