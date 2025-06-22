# infra/db/models/user_model.py

from sqlalchemy import Column, DateTime, Integer, String, Enum, func
from neomediapi.infra.db.base_class import Base
from neomediapi.enums.user_roles import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(Enum(UserRole), nullable=False)
    firebase_uid = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
