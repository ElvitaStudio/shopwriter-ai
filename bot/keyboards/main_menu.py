from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

MENU_LABELS = {
    "ru": {
        "create": "✍️ Создать карточку",
        "photo": "🖼 Загрузить фото",
        "examples": "💡 Примеры карточек",
        "my_cards": "📦 Мои карточки",
        "profile": "👤 Мой профиль",
        "buy_tokens": "⚡️ Купить токены",
        "referral": "🤝 Партнёрка",
        "support": "🆘 Поддержка",
    },
    "ua": {
        "create": "✍️ Створити картку",
        "photo": "🖼 Завантажити фото",
        "examples": "💡 Приклади карток",
        "my_cards": "📦 Мої картки",
        "profile": "👤 Мій профіль",
        "buy_tokens": "⚡️ Купити токени",
        "referral": "🤝 Партнерка",
        "support": "🆘 Підтримка",
    },
    "en": {
        "create": "✍️ Create Card",
        "photo": "🖼 Upload Photo",
        "examples": "💡 Card Examples",
        "my_cards": "📦 My Cards",
        "profile": "👤 My Profile",
        "buy_tokens": "⚡️ Buy Tokens",
        "referral": "🤝 Referral",
        "support": "🆘 Support",
    },
}


def get_main_menu(language: str = "ru") -> ReplyKeyboardMarkup:
    labels = MENU_LABELS.get(language, MENU_LABELS["ru"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=labels["create"]), KeyboardButton(text=labels["photo"])],
            [KeyboardButton(text=labels["examples"]), KeyboardButton(text=labels["my_cards"])],
            [KeyboardButton(text=labels["profile"]), KeyboardButton(text=labels["buy_tokens"])],
            [KeyboardButton(text=labels["referral"]), KeyboardButton(text=labels["support"])],
        ],
        resize_keyboard=True,
    )


def get_open_app_button(url: str, language: str = "ru") -> InlineKeyboardMarkup:
    labels = {
        "ru": "🚀 Открыть ShopWriter AI",
        "ua": "🚀 Відкрити ShopWriter AI",
        "en": "🚀 Open ShopWriter AI",
    }
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=labels.get(language, labels["ru"]), web_app={"url": url})]]
    )
