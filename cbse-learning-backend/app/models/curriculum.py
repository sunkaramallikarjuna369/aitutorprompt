from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class LearningObjective(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    bloom_level: str
    keywords: List[str] = []

class ContentBlock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    title: str
    content: str
    order: int
    metadata: Dict[str, Any] = {}
    visual_config_ref: Optional[str] = None
    media_urls: List[str] = []

class Topic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: str
    name: str
    description: str
    order: int
    learning_objectives: List[LearningObjective] = []
    content_blocks: List[ContentBlock] = []
    rwal_refs: List[str] = []
    visual_config_refs: List[str] = []
    tags: List[str] = []
    estimated_time_minutes: int = 15

class Chapter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject_id: str
    name: str
    number: int
    description: str
    difficulty: str = "medium"
    topics: List[str] = []
    learning_objectives: List[str] = []
    prerequisites: List[str] = []
    estimated_time_hours: float = 2.0

class Subject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    class_id: str
    name: str
    code: str
    description: str
    chapters: List[str] = []
    icon: str = "book"

class Class(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    board: str = "CBSE"
    grade: int
    name: str
    description: str
    subjects: List[str] = []
