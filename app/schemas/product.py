from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=150)

    description: str | None = None

    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=150)

    description: str | None = None

    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )

    stock: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> Self:
        for field in ("name", "price", "stock"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int

    model_config = ConfigDict(from_attributes=True)