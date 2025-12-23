from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from ...utils.database import db
from ...utils.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])

class TopicViewedRequest(BaseModel):
    topic_id: str
    time_spent_minutes: int = 0
    content_blocks_viewed: List[str] = []

class UpdateProgressRequest(BaseModel):
    status: Optional[str] = None
    progress_pct: Optional[float] = None
    time_spent_minutes: Optional[int] = None

@router.get("/me/chapters")
async def get_my_progress(current_user: dict = Depends(get_current_user)):
    all_progress = db.get_user_progress(current_user["id"])
    
    progress_with_details = []
    for prog in all_progress:
        chapter = db.get_chapter(prog["chapter_id"])
        if chapter:
            progress_with_details.append({
                **prog,
                "chapter_name": chapter["name"],
                "chapter_number": chapter["number"],
                "subject_id": chapter["subject_id"]
            })
    
    total_chapters = len(db.get_all_classes())
    completed = sum(1 for p in all_progress if p["status"] == "completed")
    in_progress = sum(1 for p in all_progress if p["status"] == "in_progress")
    
    return {
        "user_id": current_user["id"],
        "progress": progress_with_details,
        "summary": {
            "total_chapters_started": len(all_progress),
            "completed": completed,
            "in_progress": in_progress,
            "overall_completion_pct": round(completed / max(1, len(all_progress)) * 100, 1)
        }
    }

@router.get("/me/chapters/{chapter_id}")
async def get_chapter_progress(
    chapter_id: str,
    current_user: dict = Depends(get_current_user)
):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    progress = db.get_or_create_progress(current_user["id"], chapter_id)
    
    topics = db.get_topics_by_chapter(chapter_id)
    topics_progress = progress.get("topics_progress", {})
    
    topics_with_progress = []
    for topic in topics:
        topic_prog = topics_progress.get(topic["id"], {
            "status": "not_started",
            "progress_pct": 0,
            "time_spent_minutes": 0
        })
        topics_with_progress.append({
            "topic_id": topic["id"],
            "topic_name": topic["name"],
            "order": topic["order"],
            **topic_prog
        })
    
    return {
        "chapter_id": chapter_id,
        "chapter_name": chapter["name"],
        "user_id": current_user["id"],
        "overall_progress": progress,
        "topics_progress": topics_with_progress,
        "quiz_history": {
            "scores": progress.get("quiz_scores", []),
            "average": progress.get("average_quiz_score", 0),
            "attempts": len(progress.get("quiz_scores", []))
        },
        "bloom_performance": progress.get("bloom_performance", {}),
        "strengths": progress.get("strengths", []),
        "weaknesses": progress.get("weaknesses", [])
    }

@router.post("/me/chapters/{chapter_id}/topic-viewed")
async def record_topic_viewed(
    chapter_id: str,
    request: TopicViewedRequest,
    current_user: dict = Depends(get_current_user)
):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    topic = db.get_topic(request.topic_id)
    if not topic or topic["chapter_id"] != chapter_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic {request.topic_id} not found in chapter {chapter_id}"
        )
    
    progress = db.get_or_create_progress(current_user["id"], chapter_id)
    
    topics_progress = progress.get("topics_progress", {})
    topic_prog = topics_progress.get(request.topic_id, {
        "status": "not_started",
        "progress_pct": 0,
        "time_spent_minutes": 0,
        "content_blocks_viewed": []
    })
    
    existing_blocks = set(topic_prog.get("content_blocks_viewed", []))
    existing_blocks.update(request.content_blocks_viewed)
    
    total_blocks = len(topic.get("content_blocks", []))
    viewed_blocks = len(existing_blocks)
    topic_progress_pct = (viewed_blocks / total_blocks * 100) if total_blocks > 0 else 100
    
    topic_prog.update({
        "status": "completed" if topic_progress_pct >= 100 else "in_progress",
        "progress_pct": min(100, topic_progress_pct),
        "time_spent_minutes": topic_prog.get("time_spent_minutes", 0) + request.time_spent_minutes,
        "content_blocks_viewed": list(existing_blocks),
        "last_accessed": datetime.utcnow().isoformat()
    })
    
    topics_progress[request.topic_id] = topic_prog
    
    all_topics = db.get_topics_by_chapter(chapter_id)
    total_topics = len(all_topics)
    completed_topics = sum(1 for t in all_topics 
                         if topics_progress.get(t["id"], {}).get("status") == "completed")
    chapter_progress_pct = (completed_topics / total_topics * 100) if total_topics > 0 else 0
    
    total_time = sum(tp.get("time_spent_minutes", 0) for tp in topics_progress.values())
    
    chapter_status = "not_started"
    if chapter_progress_pct >= 100:
        chapter_status = "completed"
    elif chapter_progress_pct > 0:
        chapter_status = "in_progress"
    
    updates = {
        "topics_progress": topics_progress,
        "progress_pct": chapter_progress_pct,
        "status": chapter_status,
        "time_spent_minutes": total_time
    }
    
    if chapter_status == "in_progress" and not progress.get("started_at"):
        updates["started_at"] = datetime.utcnow().isoformat()
    if chapter_status == "completed" and not progress.get("completed_at"):
        updates["completed_at"] = datetime.utcnow().isoformat()
    
    updated_progress = db.update_progress(current_user["id"], chapter_id, updates)
    
    return {
        "message": "Progress updated successfully",
        "topic_progress": topic_prog,
        "chapter_progress_pct": chapter_progress_pct,
        "chapter_status": chapter_status
    }

@router.put("/me/chapters/{chapter_id}")
async def update_chapter_progress(
    chapter_id: str,
    request: UpdateProgressRequest,
    current_user: dict = Depends(get_current_user)
):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    
    if not updates:
        progress = db.get_or_create_progress(current_user["id"], chapter_id)
        return progress
    
    updated_progress = db.update_progress(current_user["id"], chapter_id, updates)
    return updated_progress

@router.get("/me/summary")
async def get_progress_summary(current_user: dict = Depends(get_current_user)):
    all_progress = db.get_user_progress(current_user["id"])
    
    total_time = sum(p.get("time_spent_minutes", 0) for p in all_progress)
    total_quizzes = sum(len(p.get("quiz_scores", [])) for p in all_progress)
    avg_quiz_score = 0
    if total_quizzes > 0:
        all_scores = []
        for p in all_progress:
            all_scores.extend(p.get("quiz_scores", []))
        avg_quiz_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    all_strengths = []
    all_weaknesses = []
    for p in all_progress:
        all_strengths.extend(p.get("strengths", []))
        all_weaknesses.extend(p.get("weaknesses", []))
    
    strength_counts = {}
    for s in all_strengths:
        strength_counts[s] = strength_counts.get(s, 0) + 1
    weakness_counts = {}
    for w in all_weaknesses:
        weakness_counts[w] = weakness_counts.get(w, 0) + 1
    
    top_strengths = sorted(strength_counts.keys(), key=lambda x: strength_counts[x], reverse=True)[:3]
    top_weaknesses = sorted(weakness_counts.keys(), key=lambda x: weakness_counts[x], reverse=True)[:3]
    
    return {
        "user_id": current_user["id"],
        "summary": {
            "chapters_started": len(all_progress),
            "chapters_completed": sum(1 for p in all_progress if p["status"] == "completed"),
            "total_time_spent_minutes": total_time,
            "total_quizzes_taken": total_quizzes,
            "average_quiz_score": round(avg_quiz_score, 1)
        },
        "learning_profile": {
            "top_strengths": top_strengths,
            "areas_to_improve": top_weaknesses,
            "learning_style": current_user.get("learning_style", "visual"),
            "pace": current_user.get("pace", "normal")
        }
    }

@router.get("/me/activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    all_progress = db.get_user_progress(current_user["id"])
    
    activities = []
    for prog in all_progress:
        chapter = db.get_chapter(prog["chapter_id"])
        if chapter:
            if prog.get("last_accessed"):
                activities.append({
                    "type": "chapter_accessed",
                    "chapter_id": prog["chapter_id"],
                    "chapter_name": chapter["name"],
                    "timestamp": prog["last_accessed"],
                    "details": {
                        "progress_pct": prog["progress_pct"],
                        "status": prog["status"]
                    }
                })
    
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "user_id": current_user["id"],
        "recent_activities": activities[:limit]
    }
