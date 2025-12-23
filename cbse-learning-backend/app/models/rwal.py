from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid

class RealWorldScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    title: str
    description: str
    category: str
    difficulty_level: str = "medium"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    daily_life_examples: List[str] = []
    industry_use_cases: List[str] = []
    career_links: List[str] = []
    mini_project_ideas: List[str] = []
    regional_context: Optional[str] = None
    tags: List[str] = []

class PersonalizedExample(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    user_id: str
    personalized_description: str
    difficulty_adjusted: str
    regional_relevance: Optional[str] = None
    learning_style_adaptation: str
    generated_at: str

class SGTContent(BaseModel):
    topic_id: str
    entry_scenario: RealWorldScenario
    learning_stages: List[Dict] = []
    real_world_applications: List[RealWorldScenario] = []
    reflection_prompts: List[str] = []
