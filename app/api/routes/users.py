from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:
    return UserService(db)


UserServiceDependency = Annotated[
    UserService,
    Depends(get_user_service),
]


@router.get("/", response_model=list[UserResponse])
def index(
    service: UserServiceDependency,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[UserResponse]:
    return service.get_all(skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def show(
    user_id: int,
    service: UserServiceDependency,
) -> UserResponse:
    user = service.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def store(
    data: UserCreate,
    service: UserServiceDependency,
) -> UserResponse:
    return service.create(data)


@router.put("/{user_id}", response_model=UserResponse)
def update(
    user_id: int,
    data: UserUpdate,
    service: UserServiceDependency,
) -> UserResponse:
    user = service.update(user_id, data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def destroy(
    user_id: int,
    service: UserServiceDependency,
) -> None:
    deleted = service.delete(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
