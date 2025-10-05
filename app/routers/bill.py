from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.bill import BillCRUD as crud
from app.deps import get_db
from app.schemas import bill as schemas

router = APIRouter(prefix="/bills", tags=["Bills"])


@router.post("/", response_model=schemas.BillRead, status_code=status.HTTP_201_CREATED)
async def create_bill(bill: schemas.BillCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_bill(db, bill)


@router.get("/{bill_id}", response_model=schemas.BillRead, status_code=status.HTTP_200_OK)
async def read_bill(bill_id: UUID, db: AsyncSession = Depends(get_db)):
    db_bill = await crud.get_bill(bill_id, db)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill


@router.get("/", response_model=list[schemas.BillRead], status_code=status.HTTP_200_OK)
async def read_bills(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.get_bills(db, skip, limit)


@router.put("/{bill_id}", response_model=schemas.BillRead, status_code=status.HTTP_201_CREATED)
async def update_bill(bill_id: UUID, bill: schemas.BillUpdate, db: AsyncSession = Depends(get_db)):
    db_bill = await crud.update_bill(bill_id, bill, db)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill


@router.delete("/{bill_id}", response_model=schemas.BillRead, status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(bill_id: UUID, db: AsyncSession = Depends(get_db)):
    db_bill = await crud.delete_bill(bill_id, db)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill
