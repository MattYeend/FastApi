from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repository.get_all(skip, limit)

    def get_by_id(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def create(self, data: UserCreate) -> User:
        if self.repository.get_by_email(str(data.email)):
            raise EmailAlreadyRegisteredError

        try:
            return self.repository.create(data)
        except IntegrityError as exc:
            self.db.rollback()
            raise EmailAlreadyRegisteredError from exc

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        user = self.get_by_id(user_id)

        if user is None:
            return None

        email = data.email

        if email is not None:
            existing = self.repository.get_by_email(str(email))

            if existing and existing.id != user_id:
                raise EmailAlreadyRegisteredError

        try:
            return self.repository.update(user, data)
        except IntegrityError as exc:
            self.db.rollback()
            raise EmailAlreadyRegisteredError from exc

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)

        if user is None:
            return False

        self.repository.delete(user)

        return True