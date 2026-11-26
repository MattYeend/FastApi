from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

EMAIL_MAX_LENGTH = 255


def normalise_email(value: str | None) -> str | None:
    if value is None:
        return None

    if len(value) > EMAIL_MAX_LENGTH:
        raise ValueError(f"Email must not exceed {EMAIL_MAX_LENGTH} characters")

    return value.lower()


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str | None:
        return normalise_email(value)


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=100)

    email: EmailStr | None = None
    is_active: bool | None = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str | None) -> str | None:
        return normalise_email(value)

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> Self:
        for field in ("name", "email", "is_active"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)