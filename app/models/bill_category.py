from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, event
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlmodel import SQLModel, Field


class BillCategory(SQLModel, table=True):
    """
    BillCategory model.
    Stores categories for bills (default or user-defined).
    """
    __tablename__ = 'bill_categories'

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
    name: str = Field(
        max_length=100,
        nullable=False,
        index=True,
        description="Category name (e.g. Food, Subscriptions, Utilities)",
    )
    icon_url: str | None = Field(
        default=None,
        description="Optional icon for category (e.g. S3 link)",
    )
    user_id: UUID | None = Field(
        default=None,
        foreign_key="users.id",
        ondelete="CASCADE",
        index=True,
        description="FK → User.id (if custom user-defined category)",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now(), nullable=False),
        description="Creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now(), nullable=False),
        description="Last update timestamp (UTC)",
    )


@event.listens_for(BillCategory, "before_update", propagate=True)
def set_updated_at(mapper, connection, target) -> None:
    target.updated_at = datetime.now()
