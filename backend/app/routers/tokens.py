from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Transaction
from app.services.payment_service import get_packages, get_package

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


class PurchaseRequest(BaseModel):
    telegram_id: int
    package_id: str
    payment_method: str = "stars"


@router.get("/packages")
async def list_packages():
    return get_packages()


@router.post("/purchase")
async def purchase_tokens(data: PurchaseRequest, db: AsyncSession = Depends(get_db)):
    pkg = get_package(data.package_id)
    if not pkg:
        raise HTTPException(status_code=400, detail="Invalid package")

    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tokens += pkg["tokens"]
    tx = Transaction(
        user_id=user.id,
        type="purchase",
        amount=pkg["tokens"],
        description=f"Покупка пакета {pkg['label']}: {pkg['tokens']} токенов",
        payment_method=data.payment_method,
    )
    db.add(tx)
    await db.commit()

    return {
        "success": True,
        "tokens_added": pkg["tokens"],
        "tokens_total": user.tokens,
        "package": pkg,
    }


@router.get("/history/{telegram_id}")
async def token_history(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    txs = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(desc(Transaction.created_at))
        .limit(50)
    )

    return [
        {
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "description": t.description,
            "payment_method": t.payment_method,
            "created_at": t.created_at.isoformat(),
        }
        for t in txs.scalars().all()
    ]
