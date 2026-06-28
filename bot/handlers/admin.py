import asyncio
import logging
import httpx
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import settings

router = Router()
logger = logging.getLogger(__name__)

HEADERS = {"x-admin-token": settings.ADMIN_TOKEN}


class BroadcastState(StatesGroup):
    waiting_message = State()


def _admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Обновить", callback_data="admin_stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
        ],
    ])


def _format_stats(stats: dict) -> str:
    return (
        "📊 <b>Статистика ShopWriter AI</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
        f"🆕 Новых за 24ч: <b>{stats['new_users_24h']}</b>\n\n"
        f"📦 Всего карточек: <b>{stats['total_cards']}</b>\n"
        f"📦 Карточек сегодня: <b>{stats['cards_today']}</b>\n\n"
        f"💎 Токенов куплено (всего): <b>{stats['tokens_purchased']}</b>"
    )


@router.message(Command("admin"))
async def admin_handler(message: Message):
    if message.from_user.id != settings.ADMIN_TELEGRAM_ID:
        return
    async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
        resp = await client.get("/api/admin/stats", headers=HEADERS)
    if resp.status_code != 200:
        await message.answer("❌ Ошибка получения статистики")
        return
    await message.answer(_format_stats(resp.json()), parse_mode="HTML", reply_markup=_admin_keyboard())


@router.callback_query(F.data == "admin_stats")
async def cb_stats(call: CallbackQuery):
    if call.from_user.id != settings.ADMIN_TELEGRAM_ID:
        return await call.answer()
    async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
        resp = await client.get("/api/admin/stats", headers=HEADERS)
    if resp.status_code != 200:
        return await call.answer("Ошибка", show_alert=True)
    await call.message.edit_text(_format_stats(resp.json()), parse_mode="HTML", reply_markup=_admin_keyboard())
    await call.answer("Обновлено")


@router.callback_query(F.data == "admin_users")
async def cb_users(call: CallbackQuery):
    if call.from_user.id != settings.ADMIN_TELEGRAM_ID:
        return await call.answer()
    async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
        resp = await client.get("/api/admin/users?limit=10", headers=HEADERS)
    if resp.status_code != 200:
        return await call.answer("Ошибка", show_alert=True)

    users = resp.json()
    lines = ["👥 <b>Последние 10 пользователей:</b>\n"]
    for u in users:
        name = u.get("username") and f"@{u['username']}" or u.get("full_name") or f"id{u['telegram_id']}"
        lines.append(f"• {name} — 💎 {u['tokens']} токенов")

    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад", callback_data="admin_stats")]
    ])
    await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=back_kb)
    await call.answer()


@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != settings.ADMIN_TELEGRAM_ID:
        return await call.answer()
    await state.set_state(BroadcastState.waiting_message)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_broadcast_cancel")]
    ])
    await call.message.answer(
        "📢 <b>Рассылка</b>\n\nОтправьте текст сообщения (можно с фото или файлом).\n"
        "Сообщение будет разослано всем пользователям.",
        parse_mode="HTML",
        reply_markup=cancel_kb,
    )
    await call.answer()


@router.callback_query(F.data == "admin_broadcast_cancel")
async def cb_broadcast_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Рассылка отменена")
    await call.answer()


@router.message(BroadcastState.waiting_message)
async def broadcast_message(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != settings.ADMIN_TELEGRAM_ID:
        return
    await state.clear()

    async with httpx.AsyncClient(base_url=settings.BACKEND_URL) as client:
        resp = await client.get("/api/admin/all_telegram_ids", headers=HEADERS)
    if resp.status_code != 200:
        await message.answer("❌ Не удалось получить список пользователей")
        return

    telegram_ids: list[int] = resp.json()
    total = len(telegram_ids)
    status_msg = await message.answer(f"⏳ Рассылка начата... 0/{total}")

    sent = 0
    failed = 0

    for tid in telegram_ids:
        try:
            await _forward_message(bot, message, tid)
            sent += 1
        except Exception as e:
            logger.warning("Broadcast failed for %s: %s", tid, e)
            failed += 1
        await asyncio.sleep(0.05)  # stay under Telegram rate limits

    await status_msg.edit_text(
        f"✅ Рассылка завершена\n\n"
        f"📤 Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего: {total}"
    )


async def _forward_message(bot: Bot, source: Message, chat_id: int) -> None:
    if source.photo:
        await bot.send_photo(
            chat_id,
            source.photo[-1].file_id,
            caption=source.caption or "",
            parse_mode="HTML",
        )
    elif source.document:
        await bot.send_document(
            chat_id,
            source.document.file_id,
            caption=source.caption or "",
            parse_mode="HTML",
        )
    elif source.video:
        await bot.send_video(
            chat_id,
            source.video.file_id,
            caption=source.caption or "",
            parse_mode="HTML",
        )
    else:
        await bot.send_message(chat_id, source.text or "", parse_mode="HTML")
