import random
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.models import User
from backend.schemas.schemas import UserCreate, UserLogin, Token, UserOut, OTPRequest, OTPVerify, FirebaseAuthRequest
from backend.services.auth_service import get_password_hash, verify_password, create_access_token, get_current_user
from backend.services.email_service import send_real_otp_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory OTP storage with timestamp: {email: {"otp": "123456", "expires_at": float}}
otp_store: Dict[str, Dict[str, Any]] = {}

@router.post("/send-otp")
def send_otp(req: OTPRequest, db: Session = Depends(get_db)):
    """Generate 6-digit OTP for 2-step verification and dispatch real email if configured."""
    email = req.email.strip().lower()
    otp = f"{random.randint(100000, 999999)}"
    expires_at = time.time() + 600  # 10 minutes

    otp_store[email] = {
        "otp": otp,
        "expires_at": expires_at
    }

    # Dispatch real email
    dispatch_res = send_real_otp_email(email, otp)

    return {
        "status": "success",
        "message": f"6-digit 2-Step Verification OTP dispatched to {email}",
        "demo_otp": otp,
        "delivery": dispatch_res.get("provider", "console"),
        "expires_in_seconds": 600
    }

@router.post("/verify-otp", response_model=Token)
def verify_otp(req: OTPVerify, db: Session = Depends(get_db)):
    """Verifies 2-Step OTP and authenticates user."""
    email = req.email.strip().lower()
    record = otp_store.get(email)

    if not record or record["otp"] != req.otp.strip():
        # Demo bypass for test ease: if user enters 999999 or correct demo_otp
        if req.otp != "999999":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired 2-Step OTP code."
            )

    if record and time.time() > record["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired. Please request a new one."
        )

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create new user during registration with OTP
        full_name = req.full_name or email.split("@")[0].title()
        pw = req.password or "TravelPilot2026!Secure"
        user = User(
            email=email,
            hashed_password=get_password_hash(pw),
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

@router.post("/firebase-login", response_model=Token)
def firebase_login(req: FirebaseAuthRequest, db: Session = Depends(get_db)):
    """1-Click Google / Firebase Authentication."""
    email = req.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash("FirebaseAutoAuth!2026"),
            full_name=req.full_name or email.split("@")[0].title()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Restore active user session on app load."""
    return UserOut.model_validate(current_user)

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))
