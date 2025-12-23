from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class StudentMode(str, Enum):
    DULL = "dull"
    AVERAGE = "average"
    CLEVER = "clever"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    class_id: str = "class-10"
    school: Optional[str] = None
    student_mode: StudentMode = StudentMode.AVERAGE


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    class_id: str
    school: Optional[str] = None
    learning_style: LearningStyle = LearningStyle.VISUAL
    student_mode: StudentMode = StudentMode.AVERAGE
    pace: str = "normal"
    role: str = "student"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(BaseModel):
    id: str
    email: EmailStr
    name: str
    class_id: str
    school: Optional[str]
    learning_style: LearningStyle
    student_mode: StudentMode
    pace: str
    role: str
