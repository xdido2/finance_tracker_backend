from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserCRUD:
    """CRUD operations for users."""

    # Create
    @classmethod
    async def create_user(cls, user: UserCreate, db: AsyncSession) -> User:
        db_user = User(**user.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    # Read one
    @classmethod
    async def get_user(cls, user_id: UUID, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    # Read many
    @classmethod
    async def get_users(cls, db: AsyncSession, skip: int = 0, limit: int = 10):
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    # Update
    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdate, db: AsyncSession):
        db_user = await cls.get_user(user_id=user_id, db=db)
        if not db_user:
            return None
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    # Delete (soft delete optional)
    @classmethod
    async def delete_user(cls, user_id: UUID, db: AsyncSession) -> bool:
        result = await cls.get_user(user_id=user_id, db=db)
        db_user = result.scalars().first()
        if not db_user:
            return False
        await db.delete(db_user)
        await db.commit()
        return True
