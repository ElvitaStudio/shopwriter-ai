import httpx
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import settings
from keyboards.main_menu import MENU_LABELS

router = Router()

EXAMPLES = {
    "rozetka": (
        "<b>Пример — Rozetka</b>\n"
        "🏷 <b>Назва:</b> Кросівки Nike Air Max 90 чоловічі білі шкіряні\n"
        "📝 <b>Опис:</b> Легендарні кросівки Nike Air Max 90 в класичному білому кольорі. "
        "Амортизація Air Max забезпечує неперевершений комфорт протягом усього дня. "
        "Верх виготовлений з натуральної шкіри преміум-класу...\n"
        "🏷 <b>Теги:</b> кросівки nike, найк ейр макс, чоловічі кросівки, білі кросівки"
    ),
    "prom": (
        "<b>Пример — Prom.ua</b>\n"
        "🏷 <b>Назва:</b> Сукня жіноча літня квіткова A-силует міді\n"
        "📝 <b>Опис:</b> Елегантна літня сукня з квітковим принтом. Легка тканина...\n"
        "📋 <b>Характеристики:</b>\n• Матеріал: 100% вискоза\n• Довжина: міді\n• Принт: квітковий"
    ),
    "wildberries": (
        "<b>Пример — Wildberries</b>\n"
        "🏷 <b>Назва:</b> Сумка женская кожаная через плечо черная городская деловая\n"
        "📝 <b>Опис:</b> Стильная кожаная сумка идеально подходит для деловых встреч и повседневных прогулок. "
        "Вместительное основное отделение, удобные карманы для телефона и документов...\n"
        "🏷 <b>30 тегов:</b> сумка женская, сумка кожаная, сумка через плечо..."
    ),
}


def _get_webapp_button(url: str, label: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, web_app=WebAppInfo(url=url))]]
    )


async def _get_user_language(telegram_id: int) -> str:
    try:
        async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
            resp = await client.get(f"/api/users/{telegram_id}")
            if resp.status_code == 200:
                return resp.json().get("language", "ru")
    except Exception:
        pass
    return "ru"


def _is_button(text: str, key: str) -> bool:
    return any(text == labels[key] for labels in MENU_LABELS.values())


@router.message(lambda m: _is_button(m.text or "", "create"))
async def handle_create(message: Message):
    lang = await _get_user_language(message.from_user.id)
    labels = {"ru": "✍️ Создать карточку", "ua": "✍️ Створити картку", "en": "✍️ Create Card"}
    await message.answer(
        labels.get(lang, labels["ru"]),
        reply_markup=_get_webapp_button(f"{settings.MINI_APP_URL}/generate", "🚀 Открыть генератор"),
    )


@router.message(lambda m: _is_button(m.text or "", "photo"))
async def handle_photo(message: Message):
    texts = {
        "ru": "📸 Отправьте фото товара, затем откройте генератор:",
        "ua": "📸 Надішліть фото товару, потім відкрийте генератор:",
        "en": "📸 Send a product photo, then open the generator:",
    }
    lang = await _get_user_language(message.from_user.id)
    await message.answer(
        texts.get(lang, texts["ru"]),
        reply_markup=_get_webapp_button(f"{settings.MINI_APP_URL}/generate", "🖼 Генератор с фото"),
    )


@router.message(lambda m: _is_button(m.text or "", "examples"))
async def handle_examples(message: Message):
    for example in EXAMPLES.values():
        await message.answer(example, parse_mode="HTML")


@router.message(lambda m: _is_button(m.text or "", "my_cards"))
async def handle_my_cards(message: Message):
    lang = await _get_user_language(message.from_user.id)
    labels = {"ru": "📦 Мои карточки", "ua": "📦 Мої картки", "en": "📦 My Cards"}
    await message.answer(
        labels.get(lang, labels["ru"]),
        reply_markup=_get_webapp_button(f"{settings.MINI_APP_URL}/history", "📦 Открыть историю"),
    )


@router.message(lambda m: _is_button(m.text or "", "profile"))
async def handle_profile(message: Message):
    telegram_id = message.from_user.id
    try:
        async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
            resp = await client.get(f"/api/users/{telegram_id}")
            user = resp.json()
        lang = user.get("language", "ru")
        texts = {
            "ru": f"👤 <b>Профиль</b>\n\nИмя: {user.get('full_name', '—')}\n💎 Токены: {user.get('tokens', 0)}\n📦 Карточек создано: {user.get('total_cards', 0)}",
            "ua": f"👤 <b>Профіль</b>\n\nІм'я: {user.get('full_name', '—')}\n💎 Токени: {user.get('tokens', 0)}\n📦 Карток створено: {user.get('total_cards', 0)}",
            "en": f"👤 <b>Profile</b>\n\nName: {user.get('full_name', '—')}\n💎 Tokens: {user.get('tokens', 0)}\n📦 Cards created: {user.get('total_cards', 0)}",
        }
        await message.answer(texts.get(lang, texts["ru"]), parse_mode="HTML",
                             reply_markup=_get_webapp_button(f"{settings.MINI_APP_URL}/profile", "👤 Открыть профиль"))
    except Exception:
        await message.answer("Ошибка загрузки профиля")


@router.message(lambda m: _is_button(m.text or "", "buy_tokens"))
async def handle_buy_tokens(message: Message):
    lang = await _get_user_language(message.from_user.id)
    labels = {"ru": "⚡️ Купить токены", "ua": "⚡️ Купити токени", "en": "⚡️ Buy Tokens"}
    await message.answer(
        labels.get(lang, labels["ru"]),
        reply_markup=_get_webapp_button(f"{settings.MINI_APP_URL}/tokens", "⚡️ Открыть магазин токенов"),
    )


@router.message(lambda m: _is_button(m.text or "", "referral"))
async def handle_referral(message: Message):
    telegram_id = message.from_user.id
    try:
        async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
            resp = await client.get(f"/api/referral/{telegram_id}")
            data = resp.json()
        text = (
            f"🤝 <b>Партнёрка</b>\n\n"
            f"Твоя ссылка:\n<code>{data['referral_link']}</code>\n\n"
            f"👥 Приглашено: {data['total_referred']}\n"
            f"💎 Заработано токенов: {data['earned_tokens']}\n\n"
            f"За каждого приглашённого — +{data['bonus_per_referral']} токена!"
        )
        await message.answer(text, parse_mode="HTML",
                             reply_markup=_get_webapp_button(f"{settings.MINI_APP_URL}/referral", "🤝 Открыть партнёрку"))
    except Exception:
        await message.answer("Ошибка загрузки реферальной информации")


@router.message(lambda m: _is_button(m.text or "", "support"))
async def handle_support(message: Message):
    text = f"🆘 Поддержка: {settings.SUPPORT_USERNAME}"
    await message.answer(text)
