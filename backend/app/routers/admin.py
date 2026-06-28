from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Card, Transaction
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin(x_admin_token: str = Header(...)):
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/stats", dependencies=[Depends(verify_admin)])
async def get_stats(db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    new_users_24h = (
        await db.execute(select(func.count()).where(User.created_at >= day_ago))
    ).scalar() or 0
    total_cards = (await db.execute(select(func.count()).select_from(Card))).scalar() or 0
    cards_today = (
        await db.execute(select(func.count()).where(Card.created_at >= today_start))
    ).scalar() or 0
    tokens_purchased = (
        await db.execute(
            select(func.sum(Transaction.amount)).where(Transaction.type == "purchase")
        )
    ).scalar() or 0

    return {
        "total_users": total_users,
        "new_users_24h": new_users_24h,
        "total_cards": total_cards,
        "cards_today": cards_today,
        "tokens_purchased": tokens_purchased,
    }


@router.get("/users", dependencies=[Depends(verify_admin)])
async def get_users(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "full_name": u.full_name,
            "language": u.language,
            "tokens": u.tokens,
            "referral_code": u.referral_code,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.get("/all_telegram_ids", dependencies=[Depends(verify_admin)])
async def get_all_telegram_ids(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]
