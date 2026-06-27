import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings

router = Router()


@router.message(Command("admin"))
async def admin_stats(message: Message):
    if message.from_user.id != settings.ADMIN_TELEGRAM_ID:
        return

    await message.answer("🔧 Панель администратора\n\nДоступные команды:\n/admin — статистика")
