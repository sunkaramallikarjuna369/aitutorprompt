"""
Firebase User Management Router

This router provides API endpoints for Firebase user management operations.
It can be used alongside or instead of the existing JWT-based auth service.

Endpoints:
- POST /firebase-users/create - Create a new Firebase user
- GET /firebase-users/me - Get current user info (from Firebase token)
- GET /firebase-users/{uid} - Get user by UID (admin only)
- PUT /firebase-users/{uid} - Update user (admin only)
- DELETE /firebase-users/{uid} - Delete user (admin only)
- GET /firebase-users/list - List all users (admin only)
- POST /firebase-users/{uid}/claims - Set custom claims (admin only)
- POST /firebase-users/password-reset - Generate password reset link
- POST /firebase-users/verify-email - Generate email verification link
- GET /firebase-users/status - Check Firebase status
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from ...utils.firebase_auth import (
    is_firebase_enabled,
    get_firebase_user,
    FirebaseUser,
    create_firebase_user,
    get_firebase_user_by_email,
    get_firebase_user_by_uid,
    update_firebase_user,
    delete_firebase_user,
    set_custom_claims,
    list_firebase_users,
    generate_password_reset_link,
    generate_email_verification_link
)

router = APIRouter(prefix="/firebase-users", tags=["Firebase Users"])


# Request/Response Models

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    display_name: Optional[str] = None
    phone_number: Optional[str] = Field(None, description="Phone number in E.164 format (e.g., +919876543210)")
    class_id: Optional[str] = Field("class_10", description="CBSE class ID")
    student_mode: Optional[str] = Field("average", description="Student mode: dull, average, or clever")


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: Optional[bool] = None
    disabled: Optional[bool] = None


class SetClaimsRequest(BaseModel):
    claims: Dict[str, Any] = Field(..., description="Custom claims to set (max 1000 bytes)")


class PasswordResetRequest(BaseModel):
    email: EmailStr


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    email_verified: bool = False
    phone_number: Optional[str] = None
    disabled: bool = False
    custom_claims: Optional[Dict[str, Any]] = None
    created_at: Optional[int] = None


class FirebaseStatusResponse(BaseModel):
    enabled: bool
    message: str
    features: List[str]


# Endpoints

@router.get("/status", response_model=FirebaseStatusResponse)
async def get_firebase_status():
    """
    Check if Firebase is properly configured and available.
    
    This endpoint does not require authentication.
    """
    enabled = is_firebase_enabled()
    
    if enabled:
        return FirebaseStatusResponse(
            enabled=True,
            message="Firebase is configured and ready",
            features=[
                "Email/Password authentication",
                "Token verification",
                "User management",
                "Custom claims",
                "Password reset",
                "Email verification"
            ]
        )
    else:
        return FirebaseStatusResponse(
            enabled=False,
            message="Firebase is not configured. Set FIREBASE_CREDENTIALS_PATH or deploy to GCP.",
            features=[]
        )


@router.post("/create", response_model=UserResponse)
async def create_user(request: CreateUserRequest):
    """
    Create a new Firebase user.
    
    This endpoint can be used for server-side user registration.
    For client-side registration, use Firebase SDK directly.
    
    Note: This creates the user in Firebase Auth. You may also want to
    store additional user data in Firestore.
    """
    result = create_firebase_user(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
        phone_number=request.phone_number
    )
    
    # Set custom claims for class and student mode
    if request.class_id or request.student_mode:
        claims = {}
        if request.class_id:
            claims["class_id"] = request.class_id
        if request.student_mode:
            claims["student_mode"] = request.student_mode
        claims["role"] = "student"
        
        set_custom_claims(result["uid"], claims)
    
    return UserResponse(
        uid=result["uid"],
        email=result["email"],
        display_name=result["display_name"],
        email_verified=result.get("email_verified", False),
        phone_number=result.get("phone_number"),
        created_at=result.get("created_at")
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: FirebaseUser = Depends(get_firebase_user)):
    """
    Get the current authenticated user's information.
    
    Requires a valid Firebase ID token in the Authorization header.
    """
    return UserResponse(
        uid=user.uid,
        email=user.email,
        display_name=user.display_name,
        email_verified=user.email_verified,
        phone_number=user.phone_number,
        custom_claims=user.custom_claims
    )


@router.get("/by-email/{email}")
async def get_user_by_email(
    email: str,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Get a user by email address.
    
    Requires authentication. Users can only look up their own email
    unless they have admin role.
    """
    # Check if user is looking up themselves or is admin
    if current_user.email != email and current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other users"
        )
    
    result = get_firebase_user_by_email(email)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return result


@router.get("/{uid}", response_model=UserResponse)
async def get_user(
    uid: str,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Get a user by UID.
    
    Users can view their own profile. Admin role required to view others.
    """
    # Check if user is looking up themselves or is admin
    if current_user.uid != uid and current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other users"
        )
    
    result = get_firebase_user_by_uid(uid)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**result)


@router.put("/{uid}", response_model=UserResponse)
async def update_user(
    uid: str,
    request: UpdateUserRequest,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Update a user's profile.
    
    Users can update their own profile. Admin role required to update others.
    Only admins can set disabled status.
    """
    # Check authorization
    if current_user.uid != uid and current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update other users"
        )
    
    # Only admins can disable users
    if request.disabled is not None and current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can disable users"
        )
    
    result = update_firebase_user(
        uid=uid,
        email=request.email,
        password=request.password,
        display_name=request.display_name,
        phone_number=request.phone_number,
        email_verified=request.email_verified,
        disabled=request.disabled
    )
    
    return UserResponse(**result)


@router.delete("/{uid}")
async def delete_user(
    uid: str,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Delete a user.
    
    Users can delete their own account. Admin role required to delete others.
    """
    # Check authorization
    if current_user.uid != uid and current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete other users"
        )
    
    delete_firebase_user(uid)
    
    return {"message": "User deleted successfully", "uid": uid}


@router.post("/{uid}/claims")
async def set_user_claims(
    uid: str,
    request: SetClaimsRequest,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Set custom claims for a user.
    
    Admin role required. Custom claims can include:
    - role: student, teacher, admin
    - class_id: CBSE class ID
    - student_mode: dull, average, clever
    - subscription: free, premium
    
    Note: Custom claims are limited to 1000 bytes total.
    """
    if current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to set custom claims"
        )
    
    set_custom_claims(uid, request.claims)
    
    return {
        "message": "Custom claims set successfully",
        "uid": uid,
        "claims": request.claims
    }


@router.get("/list/all")
async def list_users(
    max_results: int = 100,
    page_token: Optional[str] = None,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    List all Firebase users with pagination.
    
    Admin role required.
    
    Args:
        max_results: Maximum number of users to return (max 1000)
        page_token: Token for pagination (from previous response)
    """
    if current_user.custom_claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to list users"
        )
    
    return list_firebase_users(max_results=max_results, page_token=page_token)


@router.post("/password-reset")
async def request_password_reset(request: PasswordResetRequest):
    """
    Generate a password reset link for a user.
    
    This endpoint does not require authentication.
    The link should be sent to the user via email.
    
    Note: In production, you should send this via email rather than
    returning the link directly.
    """
    link = generate_password_reset_link(request.email)
    
    return {
        "message": "Password reset link generated",
        "email": request.email,
        "link": link,
        "note": "In production, send this link via email instead of returning it"
    }


@router.post("/verify-email")
async def request_email_verification(request: EmailVerificationRequest):
    """
    Generate an email verification link for a user.
    
    This endpoint does not require authentication.
    The link should be sent to the user via email.
    
    Note: In production, you should send this via email rather than
    returning the link directly.
    """
    link = generate_email_verification_link(request.email)
    
    return {
        "message": "Email verification link generated",
        "email": request.email,
        "link": link,
        "note": "In production, send this link via email instead of returning it"
    }


@router.post("/set-student-mode")
async def set_student_mode(
    student_mode: str,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Set the student mode for the current user.
    
    Valid modes: dull, average, clever
    """
    if student_mode not in ["dull", "average", "clever"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid student mode. Must be: dull, average, or clever"
        )
    
    # Get current claims and update
    current_claims = current_user.custom_claims.copy()
    current_claims["student_mode"] = student_mode
    
    set_custom_claims(current_user.uid, current_claims)
    
    return {
        "message": "Student mode updated",
        "uid": current_user.uid,
        "student_mode": student_mode
    }


@router.post("/set-class")
async def set_class(
    class_id: str,
    current_user: FirebaseUser = Depends(get_firebase_user)
):
    """
    Set the class for the current user.
    
    Example class IDs: class_9, class_10, class_11, class_12
    """
    # Get current claims and update
    current_claims = current_user.custom_claims.copy()
    current_claims["class_id"] = class_id
    
    set_custom_claims(current_user.uid, current_claims)
    
    return {
        "message": "Class updated",
        "uid": current_user.uid,
        "class_id": class_id
    }
