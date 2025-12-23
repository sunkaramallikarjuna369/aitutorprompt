from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from ...ai import get_ai_provider, VisualConfig, StudentMode, AIPromptTemplate
from ...utils.database import topics_db, users_db
from ...utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visualization-orchestrator", tags=["Visualization Orchestrator"])


class VisualConfigRequest(BaseModel):
    student_mode: Optional[StudentMode] = None
    mastery_level: Optional[float] = Field(default=None, ge=0, le=100)
    pace: Optional[str] = None


class WorkedExampleRequest(BaseModel):
    problem: str
    student_mode: Optional[StudentMode] = None


class VisualConfigResponse(BaseModel):
    config: VisualConfig
    prompt_template_used: str
    ai_provider: str


@router.post("/topics/{topic_id}/config", response_model=VisualConfigResponse)
async def generate_visual_config(
    topic_id: str,
    request: VisualConfigRequest,
    current_user: dict = Depends(get_current_user)
):
    topic = topics_db.get(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    student_mode = request.student_mode
    if student_mode is None:
        user_mode = users_db.get(current_user["id"], {}).get("student_mode", "average")
        student_mode = StudentMode(user_mode)
    
    mastery_level = request.mastery_level
    if mastery_level is None:
        mastery_level = 50.0
    
    ai_provider = get_ai_provider()
    provider_name = type(ai_provider).__name__
    
    logger.info(f"Generating visual config for topic {topic_id} with mode {student_mode} using {provider_name}")
    
    config = await ai_provider.generate_visual_config(
        topic_id=topic_id,
        topic_name=topic.get("name", "Quadratic Equations"),
        learning_objectives=topic.get("learning_objectives", []),
        student_mode=student_mode,
        mastery_level=mastery_level
    )
    
    template = AIPromptTemplate.get_template_for_mode(student_mode)
    
    return VisualConfigResponse(
        config=config,
        prompt_template_used=template.user_prompt_template[:200] + "...",
        ai_provider=provider_name
    )


@router.get("/topics/{topic_id}/config/preview")
async def preview_visual_configs(
    topic_id: str,
    current_user: dict = Depends(get_current_user)
):
    topic = topics_db.get(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    ai_provider = get_ai_provider()
    provider_name = type(ai_provider).__name__
    
    configs = {}
    for mode in StudentMode:
        config = await ai_provider.generate_visual_config(
            topic_id=topic_id,
            topic_name=topic.get("name", "Quadratic Equations"),
            learning_objectives=topic.get("learning_objectives", []),
            student_mode=mode,
            mastery_level=50.0
        )
        configs[mode.value] = config.model_dump()
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.get("name"),
        "ai_provider": provider_name,
        "configs_by_mode": configs
    }


@router.post("/topics/{topic_id}/worked-example")
async def generate_worked_example(
    topic_id: str,
    request: WorkedExampleRequest,
    current_user: dict = Depends(get_current_user)
):
    topic = topics_db.get(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    student_mode = request.student_mode
    if student_mode is None:
        user_mode = users_db.get(current_user["id"], {}).get("student_mode", "average")
        student_mode = StudentMode(user_mode)
    
    ai_provider = get_ai_provider()
    
    example = await ai_provider.generate_worked_example(
        topic_id=topic_id,
        problem=request.problem,
        student_mode=student_mode
    )
    
    return {
        "topic_id": topic_id,
        "student_mode": student_mode.value,
        "worked_example": example,
        "ai_provider": type(ai_provider).__name__
    }


@router.get("/prompt-templates")
async def get_prompt_templates(
    current_user: dict = Depends(get_current_user)
):
    templates = {}
    for mode in StudentMode:
        template = AIPromptTemplate.get_template_for_mode(mode)
        templates[mode.value] = {
            "system_prompt": template.system_prompt,
            "user_prompt_template": template.user_prompt_template
        }
    
    return {
        "description": "AI prompt templates used for each student learning mode",
        "templates": templates,
        "usage": {
            "dull": "For students who need extra support with simplified, metaphor-based explanations",
            "average": "For students who benefit from balanced, procedural learning",
            "clever": "For advanced students who want complex, abstract challenges"
        }
    }


@router.get("/modes")
async def get_available_modes():
    return {
        "modes": [
            {
                "id": StudentMode.DULL.value,
                "name": "Supportive Learning",
                "description": "Simplified visualizations with real-world metaphors, slower animations, and high scaffolding",
                "features": [
                    "High-contrast colors for better visibility",
                    "Real-world metaphors (ball trajectory, bridge arches)",
                    "Step-by-step guidance with hints",
                    "Slower animation speeds",
                    "Simplified controls"
                ],
                "recommended_for": "Students who need extra support or are new to the topic"
            },
            {
                "id": StudentMode.AVERAGE.value,
                "name": "Balanced Learning",
                "description": "Procedural visualizations focusing on mathematical relationships",
                "features": [
                    "Standard mathematical color coding",
                    "Discriminant visualization",
                    "Medium scaffolding with hints available",
                    "Normal animation speeds",
                    "Drag and zoom enabled"
                ],
                "recommended_for": "Students with foundational understanding seeking to deepen knowledge"
            },
            {
                "id": StudentMode.CLEVER.value,
                "name": "Advanced Exploration",
                "description": "Complex visualizations with abstract concepts and sandbox mode",
                "features": [
                    "Complex roots and 3D transformations",
                    "Sandbox/exploration mode",
                    "Minimal scaffolding",
                    "Fast animations",
                    "Stress-test mode for edge cases",
                    "Derivative and integral visualizations"
                ],
                "recommended_for": "Advanced students seeking challenges and deeper mathematical insights"
            }
        ]
    }
