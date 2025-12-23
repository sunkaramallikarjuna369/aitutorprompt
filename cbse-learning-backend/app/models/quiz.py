from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class BloomLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class QuestionType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    NUMERICAL = "numerical"

class QuestionOption(BaseModel):
    id: str
    text: str
    is_correct: bool = False

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: str
    topic_id: Optional[str] = None
    bloom_level: BloomLevel
    difficulty: int = Field(ge=1, le=5, default=3)
    type: QuestionType
    question_text: str
    options: List[QuestionOption] = []
    correct_answer: str
    explanation: str
    hint: Optional[str] = None
    points: int = 10
    time_limit_seconds: int = 60
    metadata: Dict[str, Any] = {}

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_session_id: str
    question_id: str
    user_id: str
    answer_payload: str
    is_correct: bool
    response_time_ms: int
    confidence_level: Optional[int] = None
    points_earned: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: str
    user_id: str
    quiz_type: str = "adaptive"
    questions: List[str] = []
    current_question_index: int = 0
    current_difficulty: int = 3
    total_score: int = 0
    max_score: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "in_progress"
    bloom_performance: Dict[str, Dict[str, int]] = {}

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: str
    user_id: str
    session_id: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken_seconds: int
    bloom_breakdown: Dict[str, float] = {}
    strengths: List[str] = []
    weaknesses: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
