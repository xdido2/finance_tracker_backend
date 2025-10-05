from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate


class BillCRUD:
    """CRUD operations for bills."""

    # Create
    @classmethod
    async def create_bill(cls, db: AsyncSession, bill: BillCreate):
        db_bill = Bill(**bill.model_dump())
        db.add(db_bill)
        await db.commit()
        await db.refresh(db_bill)
        return db_bill

    # Get one
    @classmethod
    async def get_bill(cls, bill_id: UUID, db: AsyncSession):
        result = await db.execute(
            select(Bill).where(Bill.id == bill_id, Bill.is_deleted == False)
        )
        return result.first()

    # Get many
    @classmethod
    async def get_bills(cls, db: AsyncSession, skip: int = 0, limit: int = 10):
        result = await db.execute(
            select(Bill).where(Bill.is_deleted == False).offset(skip).limit(limit)
        )
        return result.all()

    # Update
    @classmethod
    async def update_bill(cls, bill_id: UUID, bill: BillUpdate, db: AsyncSession):
        db_bill = await cls.get_bill(bill_id, db)
        if not db_bill:
            return None
        for key, value in bill.model_dump(exclude_unset=True).items():
            setattr(db_bill, key, value)
        await db.commit()
        await db.refresh(db_bill)
        return db_bill

    # Soft delete
    @classmethod
    async def delete_bill(cls, bill_id: UUID, db: AsyncSession):
        db_bill = await cls.get_bill(bill_id, db)
        if not db_bill:
            return None
        db_bill.is_deleted = True
        await db.commit()
        return db_bill
