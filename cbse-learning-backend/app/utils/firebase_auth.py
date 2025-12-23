"""
Firebase Authentication Module for CBSE Learning Platform

This module provides Firebase Authentication integration for user management.
It supports both Firebase ID token verification and user management operations.

Firebase Free Tier (Spark Plan):
- 50,000 monthly active users
- Email/Password authentication
- Google Sign-In
- Phone authentication (limited)

Setup:
1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication and choose sign-in methods
3. Download service account key JSON
4. Set FIREBASE_CREDENTIALS_PATH environment variable

Usage:
- For new projects: Use Firebase as primary auth
- For existing projects: Use alongside JWT auth for gradual migration
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Firebase Admin SDK - optional import
firebase_admin = None
auth = None
firestore = None

def _init_firebase():
    """Initialize Firebase Admin SDK if credentials are available."""
    global firebase_admin, auth, firestore
    
    if firebase_admin is not None:
        return True
    
    try:
        import firebase_admin as fb_admin
        from firebase_admin import auth as fb_auth
        from firebase_admin import credentials, firestore as fb_firestore
        
        firebase_admin = fb_admin
        auth = fb_auth
        firestore = fb_firestore
        
        # Check if already initialized
        try:
            fb_admin.get_app()
            logger.info("Firebase already initialized")
            return True
        except ValueError:
            pass
        
        # Try to initialize with credentials
        creds_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        
        if creds_path and os.path.exists(creds_path):
            cred = credentials.Certificate(creds_path)
            fb_admin.initialize_app(cred)
            logger.info(f"Firebase initialized with credentials from {creds_path}")
            return True
        
        # Try Application Default Credentials (works on GCP)
        try:
            cred = credentials.ApplicationDefault()
            fb_admin.initialize_app(cred)
            logger.info("Firebase initialized with Application Default Credentials")
            return True
        except Exception as e:
            logger.warning(f"Could not initialize Firebase with ADC: {e}")
        
        # Initialize without credentials (limited functionality)
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
        if project_id:
            fb_admin.initialize_app(options={"projectId": project_id})
            logger.info(f"Firebase initialized with project ID: {project_id}")
            return True
        
        logger.warning("Firebase not initialized - no credentials found")
        return False
        
    except ImportError:
        logger.warning("firebase-admin not installed")
        return False
    except Exception as e:
        logger.error(f"Firebase initialization error: {e}")
        return False


def is_firebase_enabled() -> bool:
    """Check if Firebase is properly initialized."""
    return _init_firebase()


security = HTTPBearer(auto_error=False)


class FirebaseUser:
    """Represents a Firebase authenticated user."""
    
    def __init__(
        self,
        uid: str,
        email: Optional[str] = None,
        display_name: Optional[str] = None,
        photo_url: Optional[str] = None,
        email_verified: bool = False,
        phone_number: Optional[str] = None,
        provider_id: str = "firebase",
        custom_claims: Optional[Dict[str, Any]] = None
    ):
        self.uid = uid
        self.id = uid  # Alias for compatibility
        self.email = email
        self.display_name = display_name
        self.photo_url = photo_url
        self.email_verified = email_verified
        self.phone_number = phone_number
        self.provider_id = provider_id
        self.custom_claims = custom_claims or {}
        
        # Default user properties for compatibility with existing code
        self.class_id = self.custom_claims.get("class_id", "class_10")
        self.student_mode = self.custom_claims.get("student_mode", "average")
        self.role = self.custom_claims.get("role", "student")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "id": self.uid,
            "email": self.email,
            "display_name": self.display_name,
            "photo_url": self.photo_url,
            "email_verified": self.email_verified,
            "phone_number": self.phone_number,
            "provider_id": self.provider_id,
            "class_id": self.class_id,
            "student_mode": self.student_mode,
            "role": self.role,
            "custom_claims": self.custom_claims
        }


def verify_firebase_token(id_token: str) -> FirebaseUser:
    """
    Verify a Firebase ID token and return user information.
    
    Args:
        id_token: The Firebase ID token from the client
        
    Returns:
        FirebaseUser object with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase authentication not configured"
        )
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        
        return FirebaseUser(
            uid=decoded_token["uid"],
            email=decoded_token.get("email"),
            display_name=decoded_token.get("name"),
            photo_url=decoded_token.get("picture"),
            email_verified=decoded_token.get("email_verified", False),
            phone_number=decoded_token.get("phone_number"),
            provider_id=decoded_token.get("firebase", {}).get("sign_in_provider", "firebase"),
            custom_claims={
                k: v for k, v in decoded_token.items()
                if k not in ["uid", "email", "name", "picture", "email_verified", 
                            "phone_number", "firebase", "iat", "exp", "aud", "iss", "sub"]
            }
        )
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has expired"
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has been revoked"
        )
    except auth.InvalidIdTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Firebase token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase authentication failed"
        )


async def get_firebase_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> FirebaseUser:
    """
    FastAPI dependency to get the current Firebase authenticated user.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: FirebaseUser = Depends(get_firebase_user)):
            return {"message": f"Hello {user.email}"}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    return verify_firebase_token(credentials.credentials)


async def get_firebase_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[FirebaseUser]:
    """
    FastAPI dependency to optionally get the current Firebase user.
    Returns None if no valid token is provided.
    """
    if credentials is None:
        return None
    
    try:
        return verify_firebase_token(credentials.credentials)
    except HTTPException:
        return None


# User Management Functions

def create_firebase_user(
    email: str,
    password: str,
    display_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    email_verified: bool = False
) -> Dict[str, Any]:
    """
    Create a new Firebase user.
    
    Args:
        email: User's email address
        password: User's password (min 6 characters)
        display_name: Optional display name
        phone_number: Optional phone number (E.164 format)
        email_verified: Whether to mark email as verified
        
    Returns:
        Dict with user information including uid
    """
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            phone_number=phone_number,
            email_verified=email_verified
        )
        
        logger.info(f"Created Firebase user: {user_record.uid}")
        
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "display_name": user_record.display_name,
            "email_verified": user_record.email_verified,
            "phone_number": user_record.phone_number,
            "created_at": user_record.user_metadata.creation_timestamp
        }
        
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    except auth.InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    except Exception as e:
        logger.error(f"Error creating Firebase user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


def get_firebase_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a Firebase user by email address."""
    if not is_firebase_enabled():
        return None
    
    try:
        user_record = auth.get_user_by_email(email)
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "display_name": user_record.display_name,
            "email_verified": user_record.email_verified,
            "disabled": user_record.disabled
        }
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        logger.error(f"Error getting Firebase user: {e}")
        return None


def get_firebase_user_by_uid(uid: str) -> Optional[Dict[str, Any]]:
    """Get a Firebase user by UID."""
    if not is_firebase_enabled():
        return None
    
    try:
        user_record = auth.get_user(uid)
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "display_name": user_record.display_name,
            "email_verified": user_record.email_verified,
            "disabled": user_record.disabled,
            "custom_claims": user_record.custom_claims
        }
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        logger.error(f"Error getting Firebase user: {e}")
        return None


def update_firebase_user(
    uid: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    display_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    email_verified: Optional[bool] = None,
    disabled: Optional[bool] = None
) -> Dict[str, Any]:
    """Update a Firebase user's properties."""
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        kwargs = {}
        if email is not None:
            kwargs["email"] = email
        if password is not None:
            kwargs["password"] = password
        if display_name is not None:
            kwargs["display_name"] = display_name
        if phone_number is not None:
            kwargs["phone_number"] = phone_number
        if email_verified is not None:
            kwargs["email_verified"] = email_verified
        if disabled is not None:
            kwargs["disabled"] = disabled
        
        user_record = auth.update_user(uid, **kwargs)
        
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "display_name": user_record.display_name,
            "email_verified": user_record.email_verified,
            "disabled": user_record.disabled
        }
        
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error updating Firebase user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


def delete_firebase_user(uid: str) -> bool:
    """Delete a Firebase user."""
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        auth.delete_user(uid)
        logger.info(f"Deleted Firebase user: {uid}")
        return True
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error deleting Firebase user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


def set_custom_claims(uid: str, claims: Dict[str, Any]) -> bool:
    """
    Set custom claims for a Firebase user.
    
    Custom claims can be used to store:
    - User role (student, teacher, admin)
    - Class ID
    - Student mode preference
    - Subscription status
    
    Note: Custom claims are limited to 1000 bytes.
    """
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        auth.set_custom_user_claims(uid, claims)
        logger.info(f"Set custom claims for user {uid}: {claims}")
        return True
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error setting custom claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set custom claims: {str(e)}"
        )


def list_firebase_users(max_results: int = 100, page_token: Optional[str] = None) -> Dict[str, Any]:
    """
    List Firebase users with pagination.
    
    Args:
        max_results: Maximum number of users to return (max 1000)
        page_token: Token for pagination
        
    Returns:
        Dict with users list and next_page_token
    """
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        page = auth.list_users(max_results=max_results, page_token=page_token)
        
        users = []
        for user in page.users:
            users.append({
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "email_verified": user.email_verified,
                "disabled": user.disabled,
                "created_at": user.user_metadata.creation_timestamp if user.user_metadata else None
            })
        
        return {
            "users": users,
            "next_page_token": page.next_page_token
        }
        
    except Exception as e:
        logger.error(f"Error listing Firebase users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


def generate_password_reset_link(email: str) -> str:
    """Generate a password reset link for a user."""
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        link = auth.generate_password_reset_link(email)
        return link
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error generating password reset link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reset link: {str(e)}"
        )


def generate_email_verification_link(email: str) -> str:
    """Generate an email verification link for a user."""
    if not is_firebase_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not configured"
        )
    
    try:
        link = auth.generate_email_verification_link(email)
        return link
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error generating email verification link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate verification link: {str(e)}"
        )
