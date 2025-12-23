from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import uuid

class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TopicProgress(BaseModel):
    topic_id: str
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    progress_pct: float = 0.0
    time_spent_minutes: int = 0
    last_accessed: Optional[datetime] = None
    content_blocks_viewed: List[str] = []

class Progress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    chapter_id: str
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    progress_pct: float = 0.0
    topics_progress: Dict[str, TopicProgress] = {}
    quiz_scores: List[float] = []
    average_quiz_score: float = 0.0
    bloom_performance: Dict[str, float] = {}
    strengths: List[str] = []
    weaknesses: List[str] = []
    time_spent_minutes: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ProgressEvent(BaseModel):
    event_type: str
    user_id: str
    chapter_id: Optional[str] = None
    topic_id: Optional[str] = None
    quiz_session_id: Optional[str] = None
    data: Dict = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
