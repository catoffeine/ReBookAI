import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.books_core.RAG import setup_rag
from bot.definitions import TELEGRAM_TOKEN
from bot.sql.sql import db_init

# импорт роутеров
import bot.handlers.profile_handler as base_handlers
import bot.handlers.books_handler as books_handlers


bot = Bot(token=TELEGRAM_TOKEN)

# Запуск бота
async def launch_bot():

    print("rag setup...")
    await setup_rag()

    dp = Dispatcher(storage=MemoryStorage())

    commands = [
        BotCommand(command="start", description="регистрация и приветствие")
    ]
    await bot.set_my_commands(commands)

    db_init()

    dp.include_routers(
        base_handlers.router,
        books_handlers.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def main():
    if TELEGRAM_TOKEN is None:
        print("Enivornment variable TELEGRAM_TOKEN is None, so quiting...")
        sys.exit(-1)

    asyncio.run(launch_bot())
