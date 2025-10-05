from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.bill_category import BillCategoryCRUD
from app.deps import get_db
from app.schemas.bill_category import (
    BillCategoryCreate,
    BillCategoryUpdate,
    BillCategoryRead
)

router = APIRouter(prefix="/bill-categories", tags=["Bill Categories"])


@router.post("/", response_model=BillCategoryRead, status_code=status.HTTP_201_CREATED)
async def create_bill_category(
        data: BillCategoryCreate,
        db: AsyncSession = Depends(get_db),
):
    user_id = data.user_id
    category = await BillCategoryCRUD.create_bill_category(data, user_id, db)
    return category


@router.get("/", response_model=list[BillCategoryRead], status_code=status.HTTP_200_OK)
async def read_bill_categories(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 10
):
    categories = await BillCategoryCRUD.get_bill_categories(user_id, db, skip, limit)
    return categories


@router.get("/{category_id}", response_model=BillCategoryRead, status_code=status.HTTP_200_OK)
async def read_bill_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    category = await BillCategoryCRUD.get_bill_category(category_id, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=BillCategoryRead, status_code=status.HTTP_200_OK)
async def update_bill_category(
        category_id: UUID,
        data: BillCategoryUpdate,
        db: AsyncSession = Depends(get_db),
        user_id: UUID = None,
):
    category = await BillCategoryCRUD.update_bill_category(category_id, data, db, user_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found or not yours")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await BillCategoryCRUD.delete_user(category_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return None
