import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Card

router = APIRouter(prefix="/api/users", tags=["users"])


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    language: str = "ru"


class LanguageUpdate(BaseModel):
    language: str


@router.post("/register")
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = result.scalar_one_or_none()

    if user:
        user.username = data.username
        user.full_name = data.full_name
        await db.commit()
        await db.refresh(user)
    else:
        user = User(
            telegram_id=data.telegram_id,
            username=data.username,
            full_name=data.full_name,
            language=data.language,
            referral_code=secrets.token_urlsafe(8),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    cards_count = await db.execute(select(func.count()).where(Card.user_id == user.id))
    total_cards = cards_count.scalar() or 0

    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "language": user.language,
        "tokens": user.tokens,
        "referral_code": user.referral_code,
        "total_cards": total_cards,
        "created_at": user.created_at.isoformat(),
    }


@router.get("/{telegram_id}")
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cards_count = await db.execute(select(func.count()).where(Card.user_id == user.id))
    total_cards = cards_count.scalar() or 0

    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "language": user.language,
        "tokens": user.tokens,
        "referral_code": user.referral_code,
        "total_cards": total_cards,
        "created_at": user.created_at.isoformat(),
    }


@router.patch("/{telegram_id}/language")
async def update_language(telegram_id: int, data: LanguageUpdate, db: AsyncSession = Depends(get_db)):
    if data.language not in ("ru", "ua", "en"):
        raise HTTPException(status_code=400, detail="Invalid language")

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.language = data.language
    await db.commit()
    return {"language": user.language}
