import re
import time
from collections import defaultdict

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginResponse, MeResponse, MessageResponse, SignupResponse
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"

# In-memory brute-force guard, keyed by "ip:email". Process-local only — fine
# for a single-instance deployment, but won't share state across workers or
# restarts. A distributed deployment would want Redis or similar instead.
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 60
_login_attempts = defaultdict(list)


def _rate_limit_key(request: Request, email: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{email.lower()}"


def _check_login_rate_limit(request: Request, email: str) -> None:
    key = _rate_limit_key(request, email)
    now = time.time()
    recent = [t for t in _login_attempts[key] if now - t < LOGIN_LOCKOUT_SECONDS]
    _login_attempts[key] = recent
    if len(recent) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many failed login attempts. Try again in a minute.",
        )


def _record_login_failure(request: Request, email: str) -> None:
    _login_attempts[_rate_limit_key(request, email)].append(time.time())


def _clear_login_failures(request: Request, email: str) -> None:
    _login_attempts.pop(_rate_limit_key(request, email), None)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new staff account",
)
def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email address")

    if not re.match(PASSWORD_REGEX, password):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Password must be at least 8 characters and include an uppercase "
            "letter, a lowercase letter, a number, and a special character",
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is already registered")

    user = User(name=name, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return SignupResponse(message="Signup successful", user_id=user.id)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in and receive a bearer access token",
)
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _check_login_rate_limit(request, email)

    user = db.query(User).filter(User.email == email).first()

    # Deliberately generic: don't reveal whether the email is registered.
    if not user or not verify_password(password, user.hashed_password):
        _record_login_failure(request, email)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email or password")

    _clear_login_failures(request, email)
    token = create_access_token({"sub": user.email})

    return LoginResponse(message="Login successful", access_token=token)


@router.get("/me", response_model=MeResponse, summary="Get the logged-in staff account")
def me(current_user: User = Depends(get_current_user)):
    return MeResponse(id=current_user.id, name=current_user.name, email=current_user.email)


@router.put("/password", response_model=MessageResponse, summary="Change the logged-in staff password")
def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")

    if not re.match(PASSWORD_REGEX, new_password):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Password must be at least 8 characters and include an uppercase "
            "letter, a lowercase letter, a number, and a special character",
        )

    current_user.hashed_password = hash_password(new_password)
    db.commit()

    return MessageResponse(message="Password updated successfully")
