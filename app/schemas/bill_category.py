from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BillCategoryBase(BaseModel):
    name: str
    icon_url: str | None


class BillCategoryCreate(BillCategoryBase):
    user_id: UUID | None

class BillCategoryUpdate(BillCategoryBase):
    pass

class BillCategoryRead(BillCategoryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime