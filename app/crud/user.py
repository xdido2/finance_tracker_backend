from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from app.core.aws_s3 import delete_file_from_s3_async
from app.core.security import get_password_hash
from app.models.bill import Bill
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserCRUD:
    """CRUD operations for users."""

    # Create
    @classmethod
    async def create_user(cls, user: UserCreate, db: AsyncSession) -> User:
        user_data = user.model_dump()
        if "password_hash" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password_hash"))
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    # Read one
    @classmethod
    async def get_user(cls, user_id: UUID, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
        return user

    # Read many
    @classmethod
    async def get_users(cls, db: AsyncSession, skip: int = 0, limit: int = 10):
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    # Update
    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdate, db: AsyncSession):
        """Update user and re-hash password if provided"""
        db_user = await cls.get_user(user_id=user_id, db=db)
        if not db_user:
            return None

        update_data = user.model_dump(exclude_unset=True)
        if "password_hash" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password_hash"))

        for key, value in update_data.items():
            setattr(db_user, key, value)

        await db.commit()
        await db.refresh(db_user)
        return db_user

        # Delete (soft delete optional)

    @classmethod
    async def delete_user(cls, user_id: UUID, db: AsyncSession) -> bool:
        """Delete user and all related S3 files"""
        user = await cls.get_user(user_id=user_id, db=db)
        if not user:
            return False

        result = await db.execute(select(Bill.bill_image_url).where(Bill.user_id == user_id))
        bill_urls = []
        for url in result.scalars().all():
            if url:
                bill_urls.append(url)

        for url in bill_urls:
            try:
                await delete_file_from_s3_async(url)
            except Exception as e:
                print(f"⚠️ Error deleting S3 file {url}: {e}")

        await db.delete(user)
        await db.commit()
        return True
