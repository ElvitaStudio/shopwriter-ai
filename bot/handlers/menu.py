import httpx
from aiogram import Router, Bot, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
    LabeledPrice, PreCheckoutQuery,
)

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


PACKAGES = [
    {"cb": "pkg_20",   "payload": "tokens_20",   "tokens": 20,   "stars": 50,
     "name_ru": "Старт",   "name_ua": "Старт",   "name_en": "Starter",  "emoji": "🌱"},
    {"cb": "pkg_100",  "payload": "tokens_100",  "tokens": 100,  "stars": 200,
     "name_ru": "Базовый", "name_ua": "Базовий", "name_en": "Basic",    "emoji": "⚡️"},
    {"cb": "pkg_500",  "payload": "tokens_500",  "tokens": 500,  "stars": 800,
     "name_ru": "Про",     "name_ua": "Про",     "name_en": "Pro",      "emoji": "🚀"},
    {"cb": "pkg_1000", "payload": "tokens_1000", "tokens": 1000, "stars": 1400,
     "name_ru": "Бизнес",  "name_ua": "Бізнес",  "name_en": "Business", "emoji": "💼"},
]

PAYLOAD_TOKENS: dict[str, int] = {p["payload"]: p["tokens"] for p in PACKAGES}
CB_TO_PACKAGE: dict[str, dict] = {p["cb"]: p for p in PACKAGES}


def _pkg_name(pkg: dict, lang: str) -> str:
    return pkg.get(f"name_{lang}") or pkg["name_ru"]


def _tokens_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = []
    for p in PACKAGES:
        name = _pkg_name(p, lang)
        rows.append([InlineKeyboardButton(
            text=f"{p['emoji']} {name} — {p['tokens']} токенов · ⭐️ {p['stars']}",
            callback_data=p["cb"],
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(lambda m: _is_button(m.text or "", "buy_tokens"))
async def handle_buy_tokens(message: Message):
    lang = await _get_user_language(message.from_user.id)
    texts = {
        "ru": "⚡️ <b>Купить токены</b>\n\nВыберите пакет. Оплата через Telegram Stars ⭐️:",
        "ua": "⚡️ <b>Купити токени</b>\n\nОберіть пакет. Оплата через Telegram Stars ⭐️:",
        "en": "⚡️ <b>Buy tokens</b>\n\nChoose a package. Payment via Telegram Stars ⭐️:",
    }
    await message.answer(
        texts.get(lang, texts["ru"]),
        parse_mode="HTML",
        reply_markup=_tokens_keyboard(lang),
    )


@router.callback_query(lambda c: c.data in CB_TO_PACKAGE)
async def handle_package_callback(call: CallbackQuery, bot: Bot):
    pkg = CB_TO_PACKAGE[call.data]
    lang = await _get_user_language(call.from_user.id)
    name = _pkg_name(pkg, lang)
    desc = {
        "ru": f"{pkg['tokens']} генераций карточек товаров для маркетплейсов",
        "ua": f"{pkg['tokens']} генерацій карток товарів для маркетплейсів",
        "en": f"{pkg['tokens']} product card generations for marketplaces",
    }
    await call.answer()
    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title=f"ShopWriter AI — {name}",
        description=desc.get(lang, desc["ru"]),
        payload=pkg["payload"],
        currency="XTR",
        prices=[LabeledPrice(label=name, amount=pkg["stars"])],
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    tokens = PAYLOAD_TOKENS.get(payload)
    if not tokens:
        return

    async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
        resp = await client.post("/api/tokens/purchase", json={
            "telegram_id": message.from_user.id,
            "amount": tokens,
            "payment_method": "stars",
        })

    if resp.status_code != 200:
        await message.answer("✅ Оплата прошла, но произошла ошибка начисления. Напишите в поддержку.")
        return

    data = resp.json()
    lang = await _get_user_language(message.from_user.id)
    texts = {
        "ru": f"✅ Оплата прошла успешно!\n\n💎 Начислено: <b>+{tokens} токенов</b>\n💰 Баланс: <b>{data['tokens_total']} токенов</b>",
        "ua": f"✅ Оплата пройшла успішно!\n\n💎 Нараховано: <b>+{tokens} токенів</b>\n💰 Баланс: <b>{data['tokens_total']} токенів</b>",
        "en": f"✅ Payment successful!\n\n💎 Added: <b>+{tokens} tokens</b>\n💰 Balance: <b>{data['tokens_total']} tokens</b>",
    }
    await message.answer(texts.get(lang, texts["ru"]), parse_mode="HTML")


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
