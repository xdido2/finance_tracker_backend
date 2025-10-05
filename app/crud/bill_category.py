from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.bill_category import BillCategory
from app.models.user import User
from app.schemas.bill_category import BillCategoryCreate, BillCategoryUpdate


class BillCategoryCRUD:
    """CRUD operations for BillCategory"""

    # Create
    @classmethod
    async def create_bill_category(cls, bill_category: BillCategoryCreate, user_id: UUID | None, db: AsyncSession):
        data = bill_category.model_dump()
        data["user_id"] = user_id or data.get("user_id")

        if data["user_id"]:
            user_check = await db.execute(select(User).where(User.id == data["user_id"]))
            if not user_check.scalars().first():
                raise HTTPException(status_code=404, detail="User not found")

        db_bill_category = BillCategory(**data)
        db.add(db_bill_category)
        await db.commit()
        await db.refresh(db_bill_category)
        return db_bill_category

    # Read one
    @classmethod
    async def get_bill_category(cls, bill_category_id: UUID, db: AsyncSession):
        result = await db.execute(
            select(BillCategory).where(BillCategory.id == bill_category_id)
        )
        return result.scalars().first()

    # Read Many
    @classmethod
    async def get_bill_categories(cls, user_id: UUID, db: AsyncSession, skip: int = 0,
                                  limit: int = 10):
        result = await db.execute(
            select(BillCategory).offset(skip).limit(limit).where(BillCategory.user_id == user_id)
        )

        return result.scalars().all()

    # Update
    @classmethod
    async def update_bill_category(
            cls,
            bill_category_id: UUID,
            bill_category_data: BillCategoryUpdate,
            db: AsyncSession,
            user_id: UUID
    ):
        result = await db.execute(
            select(BillCategory)
            .where(BillCategory.id == bill_category_id, BillCategory.user_id == user_id)
        )
        db_bill_category = result.scalars().first()

        if not db_bill_category:
            return None

        update_data = bill_category_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_bill_category, key, value)

        await db.commit()
        await db.refresh(db_bill_category)

        return db_bill_category

    # Delete (soft delete optional)
    @classmethod
    async def delete_user(cls, bill_category_id: UUID, db: AsyncSession) -> bool:
        db_bill_category = await cls.get_bill_category(bill_category_id, db)
        if not db_bill_category:
            return False
        await db.delete(db_bill_category)
        await db.commit()
        return True
