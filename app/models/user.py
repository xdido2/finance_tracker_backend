from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    User model.
    Stores authentication and profile data.
    """

    __tablename__ = 'users'

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            pgUUID(as_uuid=True),
            primary_key=True,
            index=True,
            unique=True,
            nullable=False,
        ),
    )
    username: str = Field(
        nullable=False,
        max_length=50,
        index=True,
        unique=True,
        description="Unique username",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        index=True,
        unique=True,
        description="User email (optional, must be unique if provided)",
    )
    password_hash: str = Field(
        nullable=False,
        max_length=255,
        description="Hashed user password",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now(), nullable=False),
        description="User creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now(), nullable=False),
        description="Last update timestamp (UTC)",
    )


@event.listens_for(User, "before_update", propagate=True)
def set_updated_at(mapper, connection, target) -> None:
    target.updated_at = datetime.now()
