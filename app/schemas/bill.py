# schemas/bill.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BillBase(BaseModel):
    title: str
    amount: Decimal
    currency: str
    bill_image_url: str | None = None


class BillCreate(BillBase):
    user_id: UUID
    category_id: UUID | None = None


class BillUpdate(BillBase):
    category_id: UUID | None


class BillRead(BillBase):
    id: UUID
    user_id: UUID
    category_id: UUID | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
