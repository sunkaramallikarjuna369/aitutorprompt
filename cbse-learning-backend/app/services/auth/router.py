from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta
from ...utils.auth import create_access_token, get_password_hash, verify_password, get_current_user
from ...utils.database import db
from ...config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    class_id: str = "class-10"
    school: Optional[str] = None
    student_mode: str = "average"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    school: Optional[str] = None
    learning_style: Optional[str] = None
    student_mode: Optional[str] = None
    pace: Optional[str] = None

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    existing_user = db.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    password_hash = get_password_hash(request.password)
    user = db.create_user(
        email=request.email,
        password_hash=password_hash,
        name=request.name,
        class_id=request.class_id,
        school=request.school,
        student_mode=request.student_mode
    )
    
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    stored_hash = db.get_password_hash(request.email)
    if not stored_hash or not verify_password(request.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user
    )

@router.post("/bootstrap")
async def bootstrap_profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Profile bootstrapped successfully",
        "user": current_user
    }

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/me")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    if not updates:
        return current_user
    
    updated_user = db.update_user(current_user["id"], updates)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user
