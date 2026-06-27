import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Card, Transaction
from app.services import claude_service

router = APIRouter(prefix="/api/cards", tags=["cards"])

VALID_PLATFORMS = {"rozetka", "prom", "wildberries", "etsy", "universal"}


class GenerateRequest(BaseModel):
    telegram_id: int
    platform: str
    product_name: str
    category: str
    key_features: str
    language: str = "ru"
    image_base64: str | None = None


@router.post("/generate")
async def generate_card(data: GenerateRequest, db: AsyncSession = Depends(get_db)):
    if data.platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail="Invalid platform")

    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tokens_cost = 2 if data.image_base64 else 1
    if user.tokens < tokens_cost:
        raise HTTPException(status_code=402, detail="Insufficient tokens")

    card_data = await claude_service.generate_card(
        platform=data.platform,
        product_name=data.product_name,
        category=data.category,
        key_features=data.key_features,
        language=data.language,
        image_base64=data.image_base64,
    )

    card = Card(
        user_id=user.id,
        platform=data.platform,
        input_text=f"{data.product_name} | {data.category} | {data.key_features}",
        result_title=card_data.get("title"),
        result_description=card_data.get("description"),
        result_characteristics=json.dumps(card_data.get("characteristics", []), ensure_ascii=False),
        result_tags=json.dumps(card_data.get("seo_tags", []), ensure_ascii=False),
        tokens_spent=tokens_cost,
    )
    db.add(card)

    user.tokens -= tokens_cost

    tx = Transaction(
        user_id=user.id,
        type="spend",
        amount=-tokens_cost,
        description=f"Генерация карточки для {data.platform}: {data.product_name}",
    )
    db.add(tx)

    await db.commit()
    await db.refresh(card)

    return {
        "card_id": card.id,
        "title": card_data.get("title"),
        "description": card_data.get("description"),
        "characteristics": card_data.get("characteristics", []),
        "seo_tags": card_data.get("seo_tags", []),
        "tokens_left": user.tokens,
    }


@router.get("/history/{telegram_id}")
async def get_history(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cards_result = await db.execute(
        select(Card)
        .where(Card.user_id == user.id)
        .order_by(desc(Card.created_at))
        .limit(20)
    )
    cards = cards_result.scalars().all()

    return [
        {
            "id": c.id,
            "platform": c.platform,
            "title": c.result_title,
            "description": c.result_description,
            "characteristics": json.loads(c.result_characteristics or "[]"),
            "seo_tags": json.loads(c.result_tags or "[]"),
            "tokens_spent": c.tokens_spent,
            "created_at": c.created_at.isoformat(),
        }
        for c in cards
    ]
