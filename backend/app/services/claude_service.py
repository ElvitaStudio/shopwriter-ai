import json
import anthropic

from app.config import settings

SYSTEM_PROMPTS = {
    "ru": (
        "Ты эксперт по написанию продающих карточек товаров для маркетплейсов. "
        "Отвечай ТОЛЬКО в формате JSON без markdown и лишних символов. "
        "Пиши убедительно, с выгодами для покупателя, SEO-оптимизированно."
    ),
    "ua": (
        "Ти експерт з написання продаючих карток товарів для маркетплейсів. "
        "Відповідай ТІЛЬКИ у форматі JSON без markdown та зайвих символів. "
        "Пиши переконливо, з вигодами для покупця, SEO-оптимізовано."
    ),
    "en": (
        "You are an expert in writing high-converting product listings for marketplaces. "
        "Reply ONLY in JSON format without markdown or extra characters. "
        "Write persuasively, focusing on buyer benefits, SEO-optimized."
    ),
}

PLATFORM_PROMPTS = {
    "rozetka": "Формат для Rozetka: название до 100 символов, описание 500-1000 символов, 5-10 характеристик, 10-15 SEO-тегов на русском/украинском",
    "prom": "Формат для Prom.ua: название до 120 символов, описание 300-800 символов, характеристики таблицей, теги через запятую",
    "wildberries": "Формат для Wildberries: название с ключевыми словами до 100 символов, описание 1000-2000 символов, 30 тегов",
    "etsy": "Format for Etsy: title up to 140 chars with keywords, description 500-1500 chars with story, 13 tags in English",
    "universal": "Универсальный формат: краткое название, развернутое описание, характеристики, теги",
}

USER_PROMPT_TEMPLATE = """
Платформа: {platform}
{platform_rules}
Товар: {product_name}
Категория: {category}
Особенности: {key_features}
{image_description}

Верни JSON:
{{
    "title": "название товара",
    "description": "описание товара",
    "characteristics": [
        {{"name": "Материал", "value": "Кожа"}},
        {{"name": "Цвет", "value": "Белый"}}
    ],
    "seo_tags": ["тег1", "тег2", "тег3"]
}}
"""


async def generate_card(
    platform: str,
    product_name: str,
    category: str,
    key_features: str,
    language: str = "ru",
    image_base64: str | None = None,
) -> dict:
    client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)

    image_description = ""
    if image_base64:
        image_description = "Фото товара предоставлено, учитывай его при описании."

    user_prompt = USER_PROMPT_TEMPLATE.format(
        platform=platform,
        platform_rules=PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS["universal"]),
        product_name=product_name,
        category=category,
        key_features=key_features,
        image_description=image_description,
    )

    messages: list = []

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64,
                    },
                },
                {"type": "text", "text": user_prompt},
            ],
        })
    else:
        messages.append({"role": "user", "content": user_prompt})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["ru"]),
        messages=messages,
    )

    raw = response.content[0].text.strip()
    return json.loads(raw)
