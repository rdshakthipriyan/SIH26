"""
Physician/User model.
"""
from sqlalchemy import Column, String, Boolean
from app.core.database import Base
from app.models.base import TimestampMixin


class Physician(Base, TimestampMixin):
    """
    Physician/doctor user model.
    """
    __tablename__ = "physicians"

    # Primary identifier
    physician_id = Column(String(50), primary_key=True, index=True)

    # Credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(200), nullable=False)
    specialization = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    # Role and status
    role = Column(String(20), default="physician", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
