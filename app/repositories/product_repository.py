from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100):
        statement = select(Product).offset(skip).limit(limit)

        return list(self.db.scalars(statement).all())

    def get_by_id(self, product_id: int):
        return self.db.get(Product, product_id)

    def create(self, data: ProductCreate):
        product = Product(**data.model_dump())

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        return product

    def update(self, product: Product, data: ProductUpdate):
        fields = data.model_dump(exclude_unset=True)

        for field, value in fields.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)

        return product

    def delete(self, product: Product):
        self.db.delete(product)
        self.db.commit()
