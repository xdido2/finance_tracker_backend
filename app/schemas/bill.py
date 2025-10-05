from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BillBase(BaseModel):
    title: str
    amount: Decimal
    currency: str
    category_id: UUID | None = None
    bill_image_url: str | None = None


class BillCreate(BillBase):
    user_id: UUID


class BillUpdate(BillBase):
    pass


class BillRead(BillBase):
    id: UUID
    user_id: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
