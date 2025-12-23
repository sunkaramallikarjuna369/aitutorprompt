from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from ...utils.database import db
from ...utils.auth import get_current_user

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])

@router.get("/classes")
async def get_all_classes():
    classes = db.get_all_classes()
    return {"classes": classes, "total": len(classes)}

@router.get("/classes/{class_id}")
async def get_class(class_id: str):
    class_data = db.get_class(class_id)
    if not class_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class {class_id} not found"
        )
    return class_data

@router.get("/classes/{class_id}/subjects")
async def get_subjects_by_class(class_id: str):
    class_data = db.get_class(class_id)
    if not class_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class {class_id} not found"
        )
    
    subjects = db.get_subjects_by_class(class_id)
    return {"subjects": subjects, "total": len(subjects), "class_id": class_id}

@router.get("/subjects/{subject_id}")
async def get_subject(subject_id: str):
    subject = db.get_subject(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {subject_id} not found"
        )
    return subject

@router.get("/subjects/{subject_id}/chapters")
async def get_chapters_by_subject(subject_id: str):
    subject = db.get_subject(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {subject_id} not found"
        )
    
    chapters = db.get_chapters_by_subject(subject_id)
    return {"chapters": chapters, "total": len(chapters), "subject_id": subject_id}

@router.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    topics = db.get_topics_by_chapter(chapter_id)
    chapter_with_topics = {**chapter, "topics_data": topics}
    return chapter_with_topics

@router.get("/chapters/{chapter_id}/topics")
async def get_topics_by_chapter(chapter_id: str):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    topics = db.get_topics_by_chapter(chapter_id)
    return {"topics": topics, "total": len(topics), "chapter_id": chapter_id}

@router.get("/topics/{topic_id}")
async def get_topic(topic_id: str):
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic {topic_id} not found"
        )
    return topic

@router.get("/hierarchy")
async def get_full_hierarchy():
    classes = db.get_all_classes()
    hierarchy = []
    
    for cls in classes:
        subjects = db.get_subjects_by_class(cls["id"])
        subjects_with_chapters = []
        
        for subject in subjects:
            chapters = db.get_chapters_by_subject(subject["id"])
            chapters_with_topics = []
            
            for chapter in chapters:
                topics = db.get_topics_by_chapter(chapter["id"])
                chapters_with_topics.append({
                    **chapter,
                    "topics_data": topics
                })
            
            subjects_with_chapters.append({
                **subject,
                "chapters_data": chapters_with_topics
            })
        
        hierarchy.append({
            **cls,
            "subjects_data": subjects_with_chapters
        })
    
    return {"hierarchy": hierarchy}
