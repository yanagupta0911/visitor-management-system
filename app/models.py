from sqlalchemy import Column, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Visitor(Base):
    __tablename__ = "visitors"

    visitor_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    address = Column(String)

    authority = Column(String)

    id_name = Column(String)
    id_no = Column(String)

    status = Column(String, default="Registered")

    registered_date = Column(String)
    registered_time = Column(String)
    registered_by = Column(String)

    checkin_date = Column(String)
    checkin_time = Column(String)
    checkin_photo = Column(String)
    checkin_by = Column(String)

    checkout_date = Column(String)
    checkout_time = Column(String)
    checkout_photo = Column(String)
    checkout_by = Column(String)
