from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.core.aws_s3 import delete_file_from_s3_async
from app.models.bill import Bill
from app.models.bill_category import BillCategory
from app.models.user import User
from app.schemas.bill import BillCreate, BillUpdate


class BillCRUD:
    """Optimized CRUD for bills."""

    # --- Helpers ---
    @staticmethod
    async def _validate_fk(db: AsyncSession, category_id: UUID | None = None):
        if category_id:
            exists = await db.scalar(select(BillCategory.id).where(BillCategory.id == category_id))
            if not exists:
                raise HTTPException(HTTP_400_BAD_REQUEST, f"Category {category_id} not found")

    # --- Create ---
    @classmethod
    async def create_bill(cls, db: AsyncSession, bill: BillCreate):
        user_exists = await db.scalar(select(User.id).where(User.id == bill.user_id))
        if not user_exists:
            raise HTTPException(HTTP_400_BAD_REQUEST, f"User {bill.user_id} not found")

        await cls._validate_fk(db, bill.category_id)

        db_bill = Bill(**bill.model_dump())
        db.add(db_bill)
        await db.commit()
        await db.refresh(db_bill)
        return db_bill

    # --- Read ---
    @classmethod
    async def get_bill(cls, bill_id: UUID, db: AsyncSession):
        bill = await db.scalar(select(Bill).where(Bill.id == bill_id, Bill.is_deleted == False))
        if not bill:
            raise HTTPException(HTTP_404_NOT_FOUND, f"Bill {bill_id} not found")
        return bill

    @classmethod
    async def get_bills(cls, db: AsyncSession, skip: int = 0, limit: int = 10):
        result = await db.scalars(select(Bill).where(Bill.is_deleted == False).offset(skip).limit(limit))
        return result.all()

    # --- Update ---
    @classmethod
    async def update_bill(cls, bill_id: UUID, bill: BillUpdate, db: AsyncSession):
        db_bill = await cls.get_bill(bill_id, db)
        await cls._validate_fk(db, bill.category_id)

        for key, value in bill.model_dump(exclude_unset=True).items():
            setattr(db_bill, key, value)

        await db.commit()
        await db.refresh(db_bill)
        return db_bill

    # --- Soft delete ---
    @classmethod
    async def delete_bill(cls, bill_id: UUID, db: AsyncSession):
        db_bill = await cls.get_bill(bill_id, db)
        db_bill.is_deleted = True
        if db_bill.bill_image_url:
            await delete_file_from_s3_async(db_bill.bill_image_url)
        await db.delete(db_bill)
        await db.commit()
        return db_bill
