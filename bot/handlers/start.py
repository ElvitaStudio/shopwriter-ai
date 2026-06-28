import httpx
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, LabeledPrice

from config import settings
from keyboards.main_menu import get_main_menu, get_open_app_button

router = Router()

WELCOME = {
    "ru": (
        "👋 Привет, {name}!\n\n"
        "🤖 <b>ShopWriter AI</b> — создаёт продающие карточки товаров для Rozetka, Prom, Wildberries, Etsy и других маркетплейсов.\n\n"
        "💎 На старте тебе начислено <b>5 токенов</b> — это 5 карточек бесплатно!\n\n"
        "Выбери действие в меню ниже 👇"
    ),
    "ua": (
        "👋 Привіт, {name}!\n\n"
        "🤖 <b>ShopWriter AI</b> — створює продаючі картки товарів для Rozetka, Prom, Wildberries, Etsy та інших маркетплейсів.\n\n"
        "💎 На старті тобі нараховано <b>5 токенів</b> — це 5 карток безкоштовно!\n\n"
        "Обери дію в меню нижче 👇"
    ),
    "en": (
        "👋 Hello, {name}!\n\n"
        "🤖 <b>ShopWriter AI</b> — generates high-converting product listings for Rozetka, Prom, Wildberries, Etsy and more.\n\n"
        "💎 You've got <b>5 free tokens</b> to start — that's 5 free cards!\n\n"
        "Choose an action from the menu below 👇"
    ),
}


BUY_PACKAGES = {
    "buy_20":   {"tokens": 20,   "stars": 50},
    "buy_100":  {"tokens": 100,  "stars": 200},
    "buy_500":  {"tokens": 500,  "stars": 800},
    "buy_1000": {"tokens": 1000, "stars": 1400},
}


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    args = message.text.split(maxsplit=1)
    param = args[1].strip() if len(args) > 1 else None

    # Deep link from tokens page: ?start=buy_20
    if param and param.startswith("buy_"):
        pkg = BUY_PACKAGES.get(param)
        if pkg:
            await bot.send_invoice(
                chat_id=message.chat.id,
                title=f"ShopWriter AI — {pkg['tokens']} токенов",
                description=f"{pkg['tokens']} генераций карточек товаров",
                payload=f"tokens_{pkg['tokens']}",
                currency="XTR",
                prices=[LabeledPrice(label=f"{pkg['tokens']} токенов", amount=pkg["stars"])],
            )
            return

    ref_code = param if param and not param.startswith("buy_") else None

    tg_user = message.from_user
    language = "ru"
    if tg_user.language_code:
        if tg_user.language_code.startswith("uk"):
            language = "ua"
        elif not tg_user.language_code.startswith("ru"):
            language = "en"

    async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
        reg_resp = await client.post("/api/users/register", json={
            "telegram_id": tg_user.id,
            "username": tg_user.username,
            "full_name": tg_user.full_name,
            "language": language,
        })
        user_data = reg_resp.json()
        language = user_data.get("language", language)

        if ref_code and not user_data.get("referred_by"):
            await client.post("/api/referral/activate", json={
                "telegram_id": tg_user.id,
                "referral_code": ref_code,
            })

    welcome_text = WELCOME.get(language, WELCOME["ru"]).format(name=tg_user.first_name or "друг")

    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_open_app_button(settings.MINI_APP_URL, language),
    )
    await message.answer("Главное меню:", reply_markup=get_main_menu(language))
