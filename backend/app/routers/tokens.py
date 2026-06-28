import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config import settings
from app.database import get_db
from app.models import User, Transaction
from app.services.payment_service import get_packages, get_package

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


class PurchaseByPackageRequest(BaseModel):
    telegram_id: int
    package_id: str
    payment_method: str = "stars"


class PurchaseByAmountRequest(BaseModel):
    telegram_id: int
    amount: int
    payment_method: str = "stars"


async def _credit_tokens(
    db: AsyncSession,
    telegram_id: int,
    tokens: int,
    description: str,
    payment_method: str,
) -> dict:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tokens += tokens
    db.add(Transaction(
        user_id=user.id,
        type="purchase",
        amount=tokens,
        description=description,
        payment_method=payment_method,
    ))
    await db.commit()
    return {"success": True, "tokens_added": tokens, "tokens_total": user.tokens}


@router.get("/packages")
async def list_packages():
    return get_packages()


@router.post("/purchase")
async def purchase_tokens(data: PurchaseByAmountRequest, db: AsyncSession = Depends(get_db)):
    """Used by bot after successful Telegram Stars payment."""
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    return await _credit_tokens(
        db,
        data.telegram_id,
        data.amount,
        f"Покупка {data.amount} токенов (Telegram Stars)",
        data.payment_method,
    )


@router.post("/purchase_package")
async def purchase_package(data: PurchaseByPackageRequest, db: AsyncSession = Depends(get_db)):
    """Used by frontend for package-based purchases."""
    pkg = get_package(data.package_id)
    if not pkg:
        raise HTTPException(status_code=400, detail="Invalid package")
    return await _credit_tokens(
        db,
        data.telegram_id,
        pkg["tokens"],
        f"Покупка пакета {pkg['label']}: {pkg['tokens']} токенов",
        data.payment_method,
    )


class CreateInvoiceRequest(BaseModel):
    telegram_id: int
    package_id: str


@router.post("/create_invoice")
async def create_invoice(data: CreateInvoiceRequest):
    pkg = get_package(data.package_id)
    if not pkg:
        raise HTTPException(status_code=400, detail="Invalid package")

    tg_api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/createInvoiceLink"
    payload = {
        "title": f"ShopWriter AI — {pkg['label']}",
        "description": f"{pkg['tokens']} генераций карточек товаров для маркетплейсов",
        "payload": f"tokens_{pkg['tokens']}",
        "currency": "XTR",
        "prices": [{"label": pkg["label"], "amount": pkg["stars"]}],
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(tg_api_url, json=payload)

    if resp.status_code != 200 or not resp.json().get("ok"):
        raise HTTPException(status_code=502, detail="Telegram API error")

    invoice_url = resp.json()["result"]
    return {"invoice_url": invoice_url}


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
