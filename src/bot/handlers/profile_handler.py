from typing import Dict, Any, Callable, Awaitable

from aiogram import Router, BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from bot.sql.users import check_if_user_exists, add_user

router = Router()

class UnregisteredMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ):

        user_id = event.from_user.id
        if not await check_if_user_exists(user_id) and event.text != "/start":
            await event.answer("Вы должны зарегистрироваться прежде, чем использовать бота командой /start.")
            return

        return await handler(event, data)

router.message.outer_middleware(UnregisteredMiddleware())


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id

    if not await check_if_user_exists(user_id):
        chat_id = message.chat.id
        username = message.from_user.username
        await add_user(user_id, chat_id, username)

    text = '''
📚 Привет, этот бот порекомендует тебе книги с учетом твоих предпочтений!

Для того, чтобы получить рекомендацию, просто введи сюда запрос на то, какие книги тебе интересны, либо просто отправь голосовое сообщение.

<b>Пример:</b>
<i>Хочу что-нибудь в жанре фантастики, короткое, после 2000 года.</i>
'''

    await message.answer(text, parse_mode=ParseMode.HTML)
