from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.user import UserCRUD
from app.deps import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# Create user
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserCRUD.create_user(db=db, user=user)


# Get all users
@router.get("/", response_model=list[UserRead])
async def get_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await UserCRUD.get_users(db=db, skip=skip, limit=limit)


# Get one user
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await UserCRUD.get_user(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# Update user
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    updated = await UserCRUD.update_user(user_id=user_id, user=user, db=db)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated


# Delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await UserCRUD.delete_user(user_id=user_id, db=db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
