from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.core.security import get_current_user_data
from app.db.session import get_db

router = APIRouter()


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: schemas.UserRegistration,
        db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(models.User).where(models.User.firebase_uid == user_data.firebase_uid)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Firebase ID already exists"
        )

    stmt = select(models.User).where(models.User.username == user_data.username)
    result = await db.execute(stmt)
    username_exists = result.scalars().first()

    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    stmt = select(models.User).where(models.User.email == user_data.email)
    result = await db.execute(stmt)
    email_exists = result.scalars().first()

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    db_user = models.User(
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
        username=user_data.username,
        display_name=user_data.display_name or user_data.username,
        avatar_url=user_data.avatar_url
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:

    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
        user_update: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Any:

    if user_update.username and user_update.username != current_user.username:
        stmt = select(models.User).where(models.User.username == user_update.username)
        result = await db.execute(stmt)
        username_exists = result.scalars().first()

        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user