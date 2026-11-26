from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip, limit)

    def get_by_id(self, product_id: int):
        return self.repository.get_by_id(product_id)

    def create(self, data: ProductCreate):
        return self.repository.create(data)

    def update(self, product_id: int, data: ProductUpdate):
        product = self.get_by_id(product_id)

        if product is None:
            return None

        return self.repository.update(product, data)

    def delete(self, product_id: int):
        product = self.get_by_id(product_id)

        if product is None:
            return False

        self.repository.delete(product)

        return True
