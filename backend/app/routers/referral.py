import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Transaction
from app.config import settings

router = APIRouter(prefix="/api/referral", tags=["referral"])

REFERRAL_BONUS = 3


class ActivateRequest(BaseModel):
    telegram_id: int
    referral_code: str


@router.get("/{telegram_id}")
async def get_referral_info(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    referred_count = await db.execute(
        select(func.count()).where(User.referred_by == user.id)
    )
    total_referred = referred_count.scalar() or 0

    earned_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user.id,
            Transaction.type == "referral",
        )
    )
    earned_tokens = earned_result.scalar() or 0

    return {
        "referral_code": user.referral_code,
        "referral_link": f"https://t.me/ShopWriterBot?start={user.referral_code}",
        "mini_app_referral_link": f"{settings.MINI_APP_URL}?ref={user.referral_code}",
        "total_referred": total_referred,
        "earned_tokens": earned_tokens,
        "bonus_per_referral": REFERRAL_BONUS,
    }


@router.post("/activate")
async def activate_referral(data: ActivateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    new_user = result.scalar_one_or_none()
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")

    if new_user.referred_by:
        return {"success": False, "message": "Already activated"}

    ref_result = await db.execute(
        select(User).where(User.referral_code == data.referral_code)
    )
    referrer = ref_result.scalar_one_or_none()
    if not referrer or referrer.telegram_id == data.telegram_id:
        raise HTTPException(status_code=400, detail="Invalid referral code")

    new_user.referred_by = referrer.id
    new_user.tokens += REFERRAL_BONUS
    referrer.tokens += REFERRAL_BONUS

    db.add(Transaction(
        user_id=new_user.id,
        type="referral",
        amount=REFERRAL_BONUS,
        description=f"Бонус за приглашение от {referrer.username or referrer.telegram_id}",
    ))
    db.add(Transaction(
        user_id=referrer.id,
        type="referral",
        amount=REFERRAL_BONUS,
        description=f"Бонус за приглашённого {new_user.username or new_user.telegram_id}",
    ))

    await db.commit()
    return {"success": True, "tokens_added": REFERRAL_BONUS}
