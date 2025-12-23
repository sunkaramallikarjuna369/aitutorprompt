from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from ...utils.database import db
from ...utils.auth import get_current_user

router = APIRouter(prefix="/rwal", tags=["Real-World Applications (SGT)"])

class StudentProfile(BaseModel):
    learning_style: Optional[str] = "visual"
    difficulty_preference: Optional[str] = "medium"
    regional_context: Optional[str] = "india"
    interests: Optional[List[str]] = []

class PersonalizedExampleRequest(BaseModel):
    student_profile: StudentProfile

@router.get("/topics/{topic_id}")
async def get_rwal_for_topic(topic_id: str):
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic {topic_id} not found"
        )
    
    scenarios = db.get_rwal_scenarios_by_topic(topic_id)
    
    all_daily_life = []
    all_industry = []
    all_careers = []
    all_projects = []
    
    for scenario in scenarios:
        all_daily_life.extend(scenario.get("daily_life_examples", []))
        all_industry.extend(scenario.get("industry_use_cases", []))
        all_careers.extend(scenario.get("career_links", []))
        all_projects.extend(scenario.get("mini_project_ideas", []))
    
    return {
        "topic_id": topic_id,
        "topic_name": topic["name"],
        "scenarios": scenarios,
        "summary": {
            "daily_life_examples": list(set(all_daily_life)),
            "industry_use_cases": list(set(all_industry)),
            "career_links": list(set(all_careers)),
            "mini_project_ideas": list(set(all_projects))
        }
    }

@router.post("/topics/{topic_id}/personalized-examples")
async def get_personalized_examples(
    topic_id: str,
    request: PersonalizedExampleRequest,
    current_user: dict = Depends(get_current_user)
):
    topic = db.get_topic(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic {topic_id} not found"
        )
    
    scenarios = db.get_rwal_scenarios_by_topic(topic_id)
    profile = request.student_profile
    
    personalized = []
    for scenario in scenarios:
        adapted_scenario = {
            "original_scenario": scenario,
            "personalized_description": _adapt_description(
                scenario["description"],
                profile.learning_style,
                profile.difficulty_preference
            ),
            "regional_examples": _get_regional_examples(
                scenario,
                profile.regional_context
            ),
            "learning_style_tips": _get_learning_style_tips(
                scenario,
                profile.learning_style
            )
        }
        personalized.append(adapted_scenario)
    
    return {
        "topic_id": topic_id,
        "student_id": current_user["id"],
        "personalized_scenarios": personalized,
        "profile_used": profile.model_dump()
    }

def _adapt_description(description: str, learning_style: str, difficulty: str) -> str:
    adaptations = {
        "visual": f"Visualize this: {description} Try drawing a diagram to understand better.",
        "auditory": f"Listen to this explanation: {description} Try explaining it out loud to yourself.",
        "kinesthetic": f"Get hands-on: {description} Try building a model or doing an experiment.",
        "reading_writing": f"Read and note: {description} Write down the key points in your own words."
    }
    
    base = adaptations.get(learning_style, description)
    
    if difficulty == "easy":
        base = f"Let's start simple: {base}"
    elif difficulty == "hard":
        base = f"Challenge yourself: {base} Can you think of more complex applications?"
    
    return base

def _get_regional_examples(scenario: dict, region: str) -> List[str]:
    regional_context = scenario.get("regional_context", "")
    
    if region == "india" and regional_context:
        return [regional_context]
    
    default_examples = {
        "india": [
            "Think about the arches in Mughal architecture like the Taj Mahal",
            "Consider how cricket ball trajectories follow parabolic paths",
            "Look at the parabolic reflectors used in ISRO's satellite dishes"
        ],
        "global": scenario.get("daily_life_examples", [])[:2]
    }
    
    return default_examples.get(region, default_examples["global"])

def _get_learning_style_tips(scenario: dict, learning_style: str) -> List[str]:
    tips = {
        "visual": [
            "Draw the parabola and mark key points",
            "Use different colors for different parts of the equation",
            "Watch videos showing real-world parabolas"
        ],
        "auditory": [
            "Explain the concept to a friend or family member",
            "Create a song or rhyme to remember the quadratic formula",
            "Listen to educational podcasts about mathematics"
        ],
        "kinesthetic": [
            "Build a model bridge with parabolic arch",
            "Throw a ball and trace its path",
            "Use physical manipulatives to understand factoring"
        ],
        "reading_writing": [
            "Write detailed notes with examples",
            "Create flashcards for formulas and methods",
            "Solve many practice problems and write solutions"
        ]
    }
    
    return tips.get(learning_style, tips["visual"])

@router.get("/scenarios")
async def get_all_scenarios():
    scenarios = db.get_all_rwal_scenarios()
    return {"scenarios": scenarios, "total": len(scenarios)}

@router.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    scenario = db.get_rwal_scenario(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )
    return scenario

@router.get("/categories")
async def get_scenario_categories():
    scenarios = db.get_all_rwal_scenarios()
    categories = {}
    
    for scenario in scenarios:
        cat = scenario.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "id": scenario["id"],
            "title": scenario["title"],
            "topic_id": scenario["topic_id"]
        })
    
    return {"categories": categories}

@router.get("/chapters/{chapter_id}/sgt-entry")
async def get_chapter_sgt_entry(chapter_id: str):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    topics = db.get_topics_by_chapter(chapter_id)
    
    for topic in topics:
        for block in topic.get("content_blocks", []):
            if block.get("metadata", {}).get("sgt_entry"):
                scenarios = db.get_rwal_scenarios_by_topic(topic["id"])
                return {
                    "chapter_id": chapter_id,
                    "entry_topic": topic["name"],
                    "entry_content": block,
                    "related_scenarios": scenarios[:2] if scenarios else [],
                    "hook_message": "Before we dive into the math, let's see where this shows up in the real world!"
                }
    
    return {
        "chapter_id": chapter_id,
        "entry_topic": None,
        "entry_content": None,
        "related_scenarios": [],
        "hook_message": "Let's explore this chapter together!"
    }
