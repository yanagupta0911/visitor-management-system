from typing import Optional

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    message: str


class SignupResponse(BaseModel):
    message: str
    user_id: int


class MeResponse(BaseModel):
    id: int
    name: str
    email: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"


class VisitorCreateResponse(BaseModel):
    message: str
    visitor_id: str


class VisitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    visitor_id: str
    user_id: Optional[int] = None
    name: str
    email: str
    phone: str
    address: str
    authority: str
    id_name: str
    id_no: str
    status: str

    registered_date: Optional[str] = None
    registered_time: Optional[str] = None
    registered_by: Optional[str] = None

    checkin_date: Optional[str] = None
    checkin_time: Optional[str] = None
    checkin_photo: Optional[str] = None
    checkin_by: Optional[str] = None

    checkout_date: Optional[str] = None
    checkout_time: Optional[str] = None
    checkout_photo: Optional[str] = None
    checkout_by: Optional[str] = None
