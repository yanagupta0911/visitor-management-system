import os
import re
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, Visitor
from app.schemas import MessageResponse, VisitorCreateResponse, VisitorOut
from app.security import get_current_user
from app.utils import generate_visitor_id, save_photo

router = APIRouter(prefix="/visitors", tags=["Visitors"])

EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
PHONE_REGEX = r"^[6-9]\d{9}$"


def _get_visitor_or_404(db: Session, visitor_id: str) -> Visitor:
    visitor = db.query(Visitor).filter(Visitor.visitor_id == visitor_id).first()
    if not visitor:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Visitor not found")
    return visitor


@router.post(
    "",
    response_model=VisitorCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new visitor (staff only)",
)
def create_visitor(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    authority: str = Form(...),
    id_name: str = Form(...),
    id_no: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email address")

    if not re.match(PHONE_REGEX, phone):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid phone number")

    now = datetime.now()

    visitor = Visitor(
        visitor_id=generate_visitor_id(),
        user_id=current_user.id,
        name=name,
        email=email,
        phone=phone,
        address=address,
        authority=authority,
        id_name=id_name,
        id_no=id_no,
        status="Registered",
        registered_date=now.strftime("%d-%m-%Y"),
        registered_time=now.strftime("%H:%M:%S"),
        registered_by=current_user.name,
    )

    db.add(visitor)
    db.commit()
    db.refresh(visitor)

    return VisitorCreateResponse(
        message="Visitor registered successfully", visitor_id=visitor.visitor_id
    )


@router.get("", response_model=List[VisitorOut], summary="List all visitors (staff only)")
def list_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Visitor).all()


@router.get(
    "/lookup",
    response_model=VisitorOut,
    summary="Look up a single visit by visitor ID + email (public)",
)
def lookup_visitor(
    visitor_id: str,
    email: str,
    db: Session = Depends(get_db),
):
    visitor = db.query(Visitor).filter(
        Visitor.visitor_id == visitor_id,
        Visitor.email == email,
    ).first()

    if not visitor:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Visitor not found or email mismatch"
        )

    return visitor


@router.get(
    "/{visitor_id}",
    response_model=VisitorOut,
    summary="Get a single visitor's full record (staff only)",
)
def get_visitor(
    visitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_visitor_or_404(db, visitor_id)


@router.put(
    "/{visitor_id}",
    response_model=VisitorOut,
    summary="Update a visitor's core details (staff only)",
)
def update_visitor(
    visitor_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    authority: str = Form(...),
    id_name: str = Form(...),
    id_no: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = _get_visitor_or_404(db, visitor_id)

    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email address")

    if not re.match(PHONE_REGEX, phone):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid phone number")

    visitor.name = name
    visitor.email = email
    visitor.phone = phone
    visitor.address = address
    visitor.authority = authority
    visitor.id_name = id_name
    visitor.id_no = id_no

    db.commit()
    db.refresh(visitor)

    return visitor


@router.post(
    "/{visitor_id}/checkin",
    response_model=VisitorOut,
    summary="Check a visitor in with a photo (staff only)",
)
async def checkin(
    visitor_id: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = _get_visitor_or_404(db, visitor_id)

    file_path = await save_photo(photo, settings.CHECKIN_PHOTO_DIR, visitor_id)

    now = datetime.now()
    visitor.status = "Checked In"
    visitor.checkin_date = now.strftime("%d-%m-%Y")
    visitor.checkin_time = now.strftime("%H:%M:%S")
    visitor.checkin_photo = file_path
    visitor.checkin_by = current_user.name

    db.commit()
    db.refresh(visitor)

    return visitor


@router.put(
    "/{visitor_id}/checkout",
    response_model=VisitorOut,
    summary="Check a visitor out with a photo (staff only)",
)
async def checkout(
    visitor_id: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = _get_visitor_or_404(db, visitor_id)

    file_path = await save_photo(photo, settings.CHECKOUT_PHOTO_DIR, visitor_id)

    now = datetime.now()
    visitor.status = "Checked Out"
    visitor.checkout_date = now.strftime("%d-%m-%Y")
    visitor.checkout_time = now.strftime("%H:%M:%S")
    visitor.checkout_photo = file_path
    visitor.checkout_by = current_user.name

    db.commit()
    db.refresh(visitor)

    return visitor


@router.get(
    "/{visitor_id}/photo/{stage}",
    summary="Fetch a visitor's check-in/out photo (staff only)",
)
def get_visitor_photo(
    visitor_id: str,
    stage: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = _get_visitor_or_404(db, visitor_id)

    if stage == "checkin":
        path = visitor.checkin_photo
    elif stage == "checkout":
        path = visitor.checkout_photo
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "stage must be 'checkin' or 'checkout'")

    if not path or not os.path.isfile(path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Photo not found")

    return FileResponse(path)


@router.delete(
    "/{visitor_id}",
    response_model=MessageResponse,
    summary="Delete a visitor record (staff only)",
)
def delete_visitor(
    visitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = _get_visitor_or_404(db, visitor_id)

    db.delete(visitor)
    db.commit()

    return MessageResponse(message="Visitor deleted successfully")
