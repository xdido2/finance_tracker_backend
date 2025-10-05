from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str | None = None


class UserCreate(UserBase):
    password_hash: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password_hash: str | None = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
