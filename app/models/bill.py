from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, event
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlmodel import Field, SQLModel


class Bill(SQLModel, table=True):
    """
    Bill model.
    Stores information about user bills / recurring payments.
    """
    __tablename__ = "bills"

    id: UUID = Field(default_factory=uuid4,
                     sa_column=Column(
                         pgUUID(as_uuid=True),
                         primary_key=True,
                         index=True,
                         unique=True
                     ))
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        ondelete="CASCADE",
        nullable=False,
        description="FK → User.id",
    )
    category_id: UUID | None = Field(
        default=None,
        foreign_key="bill_categories.id",
        index=True,
        description="FK → BillCategory.id",
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        description="Bill name (e.g. Amazon Prime, Uzum Market)",
    )
    amount: Decimal = Field(
        default=0,
        nullable=False,
        description="Bill amount",
    )
    currency: str = Field(
        max_length=3,
        nullable=False,
        description="Currency (ISO 4217: UZS, USD, EUR...)",
    )
    bill_image_url: str | None = Field(
        default=None,
        description="Link to bill image (e.g. S3 storage)",
    )
    is_deleted: bool = Field(
        default=False,
        nullable=False,
        description="Soft delete flag",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now(), nullable=False),
        description="Creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now(), nullable=False),
        description="Last update timestamp (UTC)",
    )


@event.listens_for(Bill, "before_update", propagate=True)
def set_updated_at(mapper, connection, target) -> None:
    target.updated_at = datetime.now()


@event.listens_for(Bill, "before_delete")
async def delete_bill_image(mapper, connection, target):
    """Delete bill image from S3 after DB delete"""
    if target.bill_image_url:
        from app.core.aws_s3 import delete_file_from_s3
        delete_file_from_s3(target.bill_image_url)
