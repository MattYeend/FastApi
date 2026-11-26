from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(
    db: Annotated[Session, Depends(get_db)],
) -> ProductService:
    return ProductService(db)


ProductServiceDependency = Annotated[
    ProductService,
    Depends(get_product_service),
]


@router.get("/", response_model=list[ProductResponse])
def index(
    service: ProductServiceDependency,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ProductResponse]:
    return service.get_all(skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
def show(
    product_id: int,
    service: ProductServiceDependency,
) -> ProductResponse:
    product = service.get_by_id(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def store(
    data: ProductCreate,
    service: ProductServiceDependency,
) -> ProductResponse:
    return service.create(data)


@router.put("/{product_id}", response_model=ProductResponse)
@router.patch("/{product_id}", response_model=ProductResponse)
def update(
    product_id: int,
    data: ProductUpdate,
    service: ProductServiceDependency,
) -> ProductResponse:
    product = service.update(product_id, data)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def destroy(
    product_id: int,
    service: ProductServiceDependency,
) -> None:
    deleted = service.delete(product_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )