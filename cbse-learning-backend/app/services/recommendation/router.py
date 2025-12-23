from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ...utils.database import db
from ...utils.auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/me/next-steps")
async def get_next_steps(current_user: dict = Depends(get_current_user)):
    all_progress = db.get_user_progress(current_user["id"])
    learning_style = current_user.get("learning_style", "visual")
    
    recommendations = []
    
    in_progress_chapters = [p for p in all_progress if p["status"] == "in_progress"]
    
    for prog in in_progress_chapters:
        chapter = db.get_chapter(prog["chapter_id"])
        if not chapter:
            continue
        
        topics = db.get_topics_by_chapter(prog["chapter_id"])
        topics_progress = prog.get("topics_progress", {})
        
        for topic in topics:
            topic_prog = topics_progress.get(topic["id"], {})
            if topic_prog.get("status") != "completed":
                recommendations.append({
                    "type": "continue_topic",
                    "priority": 1,
                    "chapter_id": prog["chapter_id"],
                    "chapter_name": chapter["name"],
                    "topic_id": topic["id"],
                    "topic_name": topic["name"],
                    "current_progress": topic_prog.get("progress_pct", 0),
                    "reason": f"Continue learning {topic['name']} in {chapter['name']}",
                    "estimated_time_minutes": topic.get("estimated_time_minutes", 15)
                })
                break
    
    weaknesses = []
    for prog in all_progress:
        weaknesses.extend(prog.get("weaknesses", []))
    
    if weaknesses:
        weak_areas = list(set(weaknesses))
        for weak_area in weak_areas[:2]:
            recommendations.append({
                "type": "practice_weak_area",
                "priority": 2,
                "bloom_level": weak_area,
                "reason": f"Practice more {weak_area.title()} level questions to improve",
                "action": "Take a focused quiz on this area"
            })
    
    for prog in all_progress:
        if prog["status"] == "in_progress" and prog.get("progress_pct", 0) >= 70:
            chapter = db.get_chapter(prog["chapter_id"])
            if chapter:
                recommendations.append({
                    "type": "take_quiz",
                    "priority": 3,
                    "chapter_id": prog["chapter_id"],
                    "chapter_name": chapter["name"],
                    "reason": f"You've covered most of {chapter['name']}. Take a quiz to test your understanding!",
                    "quiz_type": "adaptive"
                })
    
    if not in_progress_chapters:
        all_chapters = []
        for cls in db.get_all_classes():
            for subject in db.get_subjects_by_class(cls["id"]):
                all_chapters.extend(db.get_chapters_by_subject(subject["id"]))
        
        started_chapter_ids = {p["chapter_id"] for p in all_progress}
        new_chapters = [c for c in all_chapters if c["id"] not in started_chapter_ids]
        
        if new_chapters:
            chapter = new_chapters[0]
            recommendations.append({
                "type": "start_new_chapter",
                "priority": 4,
                "chapter_id": chapter["id"],
                "chapter_name": chapter["name"],
                "reason": f"Start learning {chapter['name']}",
                "estimated_time_hours": chapter.get("estimated_time_hours", 2)
            })
    
    style_tips = _get_learning_style_tips(learning_style)
    recommendations.append({
        "type": "learning_tip",
        "priority": 5,
        "learning_style": learning_style,
        "tip": style_tips[0] if style_tips else "Keep up the great work!",
        "reason": f"Personalized tip for {learning_style} learners"
    })
    
    recommendations.sort(key=lambda x: x["priority"])
    
    return {
        "user_id": current_user["id"],
        "recommendations": recommendations[:5],
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/me/review-plan")
async def get_review_plan(current_user: dict = Depends(get_current_user)):
    all_progress = db.get_user_progress(current_user["id"])
    
    review_items = []
    
    for prog in all_progress:
        if prog["status"] == "completed":
            chapter = db.get_chapter(prog["chapter_id"])
            if not chapter:
                continue
            
            last_accessed = prog.get("last_accessed")
            if last_accessed:
                try:
                    last_date = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                    days_since = (datetime.utcnow() - last_date.replace(tzinfo=None)).days
                    
                    if days_since >= 7:
                        urgency = "high" if days_since >= 14 else "medium"
                        review_items.append({
                            "chapter_id": prog["chapter_id"],
                            "chapter_name": chapter["name"],
                            "days_since_review": days_since,
                            "urgency": urgency,
                            "last_quiz_score": prog.get("average_quiz_score", 0),
                            "recommended_action": "Take a quick review quiz",
                            "estimated_time_minutes": 15
                        })
                except (ValueError, TypeError):
                    pass
    
    weak_topics = []
    for prog in all_progress:
        if prog.get("weaknesses"):
            chapter = db.get_chapter(prog["chapter_id"])
            if chapter:
                for weakness in prog["weaknesses"]:
                    weak_topics.append({
                        "chapter_id": prog["chapter_id"],
                        "chapter_name": chapter["name"],
                        "bloom_level": weakness,
                        "recommended_action": f"Practice {weakness} level questions"
                    })
    
    today = datetime.utcnow().date()
    schedule = []
    
    for i, item in enumerate(review_items[:3]):
        review_date = today + timedelta(days=i)
        schedule.append({
            "date": review_date.isoformat(),
            "chapter_id": item["chapter_id"],
            "chapter_name": item["chapter_name"],
            "activity": "Review Quiz",
            "estimated_time_minutes": item["estimated_time_minutes"]
        })
    
    for i, topic in enumerate(weak_topics[:2]):
        review_date = today + timedelta(days=len(review_items) + i)
        schedule.append({
            "date": review_date.isoformat(),
            "chapter_id": topic["chapter_id"],
            "chapter_name": topic["chapter_name"],
            "activity": f"Practice {topic['bloom_level']} questions",
            "estimated_time_minutes": 20
        })
    
    return {
        "user_id": current_user["id"],
        "review_plan": {
            "items_needing_review": review_items,
            "weak_areas_to_practice": weak_topics,
            "suggested_schedule": schedule
        },
        "spaced_repetition_info": {
            "method": "Spaced repetition helps you remember better by reviewing at optimal intervals",
            "intervals": ["1 day", "3 days", "7 days", "14 days", "30 days"]
        },
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/me/learning-path")
async def get_learning_path(current_user: dict = Depends(get_current_user)):
    user_class = current_user.get("class_id", "class-10")
    
    class_data = db.get_class(user_class)
    if not class_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class {user_class} not found"
        )
    
    subjects = db.get_subjects_by_class(user_class)
    all_progress = db.get_user_progress(current_user["id"])
    progress_map = {p["chapter_id"]: p for p in all_progress}
    
    learning_path = []
    
    for subject in subjects:
        chapters = db.get_chapters_by_subject(subject["id"])
        chapters.sort(key=lambda x: x.get("number", 0))
        
        subject_path = {
            "subject_id": subject["id"],
            "subject_name": subject["name"],
            "chapters": []
        }
        
        for chapter in chapters:
            prog = progress_map.get(chapter["id"], {})
            chapter_info = {
                "chapter_id": chapter["id"],
                "chapter_name": chapter["name"],
                "chapter_number": chapter["number"],
                "status": prog.get("status", "not_started"),
                "progress_pct": prog.get("progress_pct", 0),
                "quiz_score": prog.get("average_quiz_score", 0),
                "estimated_time_hours": chapter.get("estimated_time_hours", 2),
                "prerequisites": chapter.get("prerequisites", [])
            }
            
            if chapter_info["status"] == "not_started":
                chapter_info["recommended"] = True
                chapter_info["recommendation_reason"] = "Next chapter in sequence"
            
            subject_path["chapters"].append(chapter_info)
        
        learning_path.append(subject_path)
    
    return {
        "user_id": current_user["id"],
        "class_id": user_class,
        "class_name": class_data["name"],
        "learning_path": learning_path,
        "overall_progress": {
            "total_chapters": sum(len(s["chapters"]) for s in learning_path),
            "completed": sum(1 for p in all_progress if p["status"] == "completed"),
            "in_progress": sum(1 for p in all_progress if p["status"] == "in_progress")
        }
    }

@router.get("/me/visualization-preference")
async def get_visualization_preference(current_user: dict = Depends(get_current_user)):
    learning_style = current_user.get("learning_style", "visual")
    all_progress = db.get_user_progress(current_user["id"])
    
    weaknesses = []
    for prog in all_progress:
        weaknesses.extend(prog.get("weaknesses", []))
    
    preferences = {
        "visual": {
            "preferred_content_types": ["interactive_parabola", "graphs", "animations", "diagrams"],
            "visualization_configs": ["vis-coefficient-explorer", "vis-discriminant"],
            "tips": ["Use color-coded notes", "Draw diagrams for each problem", "Watch video explanations"]
        },
        "auditory": {
            "preferred_content_types": ["explanations", "discussions", "verbal_walkthroughs"],
            "visualization_configs": ["vis-quadratic-formula"],
            "tips": ["Read problems aloud", "Explain solutions to yourself", "Use mnemonic devices"]
        },
        "kinesthetic": {
            "preferred_content_types": ["interactive_parabola", "hands_on", "experiments"],
            "visualization_configs": ["vis-coefficient-explorer", "vis-completing-square"],
            "tips": ["Use physical manipulatives", "Build models", "Take breaks and move around"]
        },
        "reading_writing": {
            "preferred_content_types": ["text", "worked_examples", "notes"],
            "visualization_configs": ["vis-factorization"],
            "tips": ["Write detailed notes", "Create summary sheets", "Practice writing solutions"]
        }
    }
    
    user_prefs = preferences.get(learning_style, preferences["visual"])
    
    if "apply" in weaknesses or "analyze" in weaknesses:
        user_prefs["recommended_focus"] = "more_practice"
        user_prefs["focus_reason"] = "You need more practice with application problems"
    elif "remember" in weaknesses or "understand" in weaknesses:
        user_prefs["recommended_focus"] = "more_conceptual"
        user_prefs["focus_reason"] = "Focus on understanding the basic concepts first"
    else:
        user_prefs["recommended_focus"] = "balanced"
        user_prefs["focus_reason"] = "You're doing well! Keep a balanced approach"
    
    return {
        "user_id": current_user["id"],
        "learning_style": learning_style,
        "preferences": user_prefs
    }

def _get_learning_style_tips(style: str) -> List[str]:
    tips = {
        "visual": [
            "Draw the parabola for each equation you solve",
            "Use different colors to highlight different parts of the quadratic formula",
            "Create mind maps connecting different solution methods",
            "Watch the interactive visualizations multiple times"
        ],
        "auditory": [
            "Read the quadratic formula out loud: 'negative b, plus or minus square root of b squared minus 4ac, all over 2a'",
            "Explain each step of your solution to yourself or a study partner",
            "Create a song or rhyme to remember the discriminant rules",
            "Discuss problems with classmates"
        ],
        "kinesthetic": [
            "Use the interactive sliders to explore how coefficients affect the parabola",
            "Build a physical model of a parabola using string and pins",
            "Walk through the solution steps physically, moving to different spots for each step",
            "Take short breaks between problems to stay focused"
        ],
        "reading_writing": [
            "Write out all the steps in your own words",
            "Create a formula sheet with all methods and when to use them",
            "Keep a problem journal with solutions and reflections",
            "Summarize each topic in your own words after learning"
        ]
    }
    return tips.get(style, tips["visual"])
