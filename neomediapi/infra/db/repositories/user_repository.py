from sqlalchemy.orm import Session
from typing import Optional

from neomediapi.infra.db.models.user_model import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        return self.db.query(User).filter_by(firebase_uid=firebase_uid).first()

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
