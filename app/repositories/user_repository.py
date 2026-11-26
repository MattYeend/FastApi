from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100):
        statement = select(User).offset(skip).limit(limit)

        return list(self.db.scalars(statement).all())

    def get_by_id(self, user_id: int):
        return self.db.get(User, user_id)

    def get_by_email(self, email: str):
        statement = select(User).where(User.email == email)

        return self.db.scalar(statement)

    def create(self, data: UserCreate):
        user = User(**data.model_dump())

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update(self, user: User, data: UserUpdate):
        fields = data.model_dump(exclude_unset=True)

        for field, value in fields.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()
