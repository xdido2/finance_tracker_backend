from fastapi import APIRouter, status

router = APIRouter(prefix="/bills", tags=["Bills"])

from uuid import UUID
from decimal import Decimal
from fastapi import Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.aws_s3 import upload_file_to_s3, generate_presigned_url
from app.schemas import bill as schemas
from app.crud.bill import BillCRUD as crud
from app.deps import get_db


@router.post("/", response_model=schemas.BillRead)
async def create_bill(
        title: str = Form(...),
        amount: Decimal = Form(...),
        currency: str = Form(...),
        user_id: UUID = Form(...),
        category_id: UUID | None = Form(None),
        file: UploadFile | None = File(None),
        db: AsyncSession = Depends(get_db),
):
    bill_data = schemas.BillCreate(
        title=title,
        amount=amount,
        currency=currency,
        user_id=user_id,
        category_id=category_id,
    )
    db_bill = await crud.create_bill(db, bill_data)

    if file and file.filename:
        key = upload_file_to_s3(file, str(db_bill.id))
        db_bill.bill_image_url = key
        await db.commit()
        await db.refresh(db_bill)

    return db_bill


@router.get("/{bill_id}", response_model=schemas.BillRead, status_code=status.HTTP_200_OK)
async def read_bill(bill_id: UUID, db: AsyncSession = Depends(get_db)):
    bill = await crud.get_bill(bill_id, db)
    if bill.bill_image_url:
        bill.bill_image_url = generate_presigned_url(bill.bill_image_url)
    return bill


@router.get("/", response_model=list[schemas.BillRead], status_code=status.HTTP_200_OK)
async def read_bills(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    bills = await crud.get_bills(db, skip=skip, limit=limit)

    for bill in bills:
        if bill.bill_image_url:
            bill.bill_image_url = generate_presigned_url(bill.bill_image_url)

    return bills


@router.put("/{bill_id}", response_model=schemas.BillRead)
async def update_bill(
        bill_id: UUID,
        db: AsyncSession = Depends(get_db),
        title: str | None = Form(None),
        amount: Decimal | None = Form(None),
        currency: str | None = Form(None),
        category_id: UUID | None = Form(None),
        file: UploadFile | None = File(None),
):
    update_data = schemas.BillUpdate(
        title=title,
        amount=amount,
        currency=currency,
        category_id=category_id,
    )
    db_bill = await crud.update_bill(bill_id, update_data, db)

    if file and file.filename:
        key = upload_file_to_s3(file, str(bill_id))
        db_bill.bill_image_url = key
        await db.commit()
        await db.refresh(db_bill)

    return db_bill


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(bill_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud.delete_bill(bill_id, db)
