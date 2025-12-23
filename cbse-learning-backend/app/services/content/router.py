from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from ...utils.database import db
from ...utils.auth import get_current_user

router = APIRouter(prefix="/content", tags=["Content"])

@router.get("/topics/{topic_id}")
async def get_topic_content(topic_id: str):
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic {topic_id} not found"
        )
    
    visual_configs = db.get_visual_configs_by_topic(topic_id)
    rwal_scenarios = db.get_rwal_scenarios_by_topic(topic_id)
    
    return {
        "topic": topic,
        "content_blocks": topic.get("content_blocks", []),
        "learning_objectives": topic.get("learning_objectives", []),
        "visual_configs": visual_configs,
        "rwal_scenarios": rwal_scenarios,
        "estimated_time_minutes": topic.get("estimated_time_minutes", 15)
    }

@router.get("/topics/{topic_id}/visual-config")
async def get_topic_visual_configs(topic_id: str):
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic {topic_id} not found"
        )
    
    visual_configs = db.get_visual_configs_by_topic(topic_id)
    return {"topic_id": topic_id, "visual_configs": visual_configs}

@router.get("/visual-configs/{config_id}")
async def get_visual_config(config_id: str):
    config = db.get_visual_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visual config {config_id} not found"
        )
    return config

@router.get("/chapters/{chapter_id}/content")
async def get_chapter_content(chapter_id: str):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    topics = db.get_topics_by_chapter(chapter_id)
    
    all_content_blocks = []
    all_visual_configs = []
    all_rwal_scenarios = []
    
    for topic in topics:
        all_content_blocks.extend(topic.get("content_blocks", []))
        all_visual_configs.extend(db.get_visual_configs_by_topic(topic["id"]))
        all_rwal_scenarios.extend(db.get_rwal_scenarios_by_topic(topic["id"]))
    
    return {
        "chapter": chapter,
        "topics": topics,
        "total_content_blocks": len(all_content_blocks),
        "total_visual_configs": len(all_visual_configs),
        "total_rwal_scenarios": len(all_rwal_scenarios),
        "estimated_time_hours": chapter.get("estimated_time_hours", 2.0)
    }

@router.get("/chapters/{chapter_id}/sgt-flow")
async def get_sgt_learning_flow(chapter_id: str):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    topics = db.get_topics_by_chapter(chapter_id)
    
    entry_scenario = None
    for topic in topics:
        for block in topic.get("content_blocks", []):
            if block.get("metadata", {}).get("sgt_entry"):
                entry_scenario = {
                    "topic_id": topic["id"],
                    "topic_name": topic["name"],
                    "content_block": block
                }
                break
        if entry_scenario:
            break
    
    learning_stages = [
        {
            "stage": 1,
            "name": "Concept Overview",
            "description": "Introduction to the main concepts with text and simple graphics",
            "topics": [t for t in topics if t["order"] <= 2]
        },
        {
            "stage": 2,
            "name": "Interactive Exploration",
            "description": "Hands-on exploration with interactive visualizations",
            "visual_configs": [db.get_visual_config("vis-coefficient-explorer")]
        },
        {
            "stage": 3,
            "name": "Real-World Applications",
            "description": "See how concepts apply in real-world scenarios",
            "rwal_scenarios": db.get_all_rwal_scenarios()[:3]
        },
        {
            "stage": 4,
            "name": "Worked Examples",
            "description": "Step-by-step worked examples",
            "topics": [t for t in topics if "worked_example" in str(t.get("content_blocks", []))]
        },
        {
            "stage": 5,
            "name": "Formative Quiz",
            "description": "Short quiz to check understanding (3-5 questions)",
            "quiz_type": "formative",
            "question_count": 5
        },
        {
            "stage": 6,
            "name": "Summative Assessment",
            "description": "Comprehensive adaptive quiz for the chapter",
            "quiz_type": "summative",
            "adaptive": True
        }
    ]
    
    return {
        "chapter_id": chapter_id,
        "chapter_name": chapter["name"],
        "entry_scenario": entry_scenario,
        "learning_stages": learning_stages,
        "total_topics": len(topics),
        "estimated_time_hours": chapter.get("estimated_time_hours", 2.0)
    }
