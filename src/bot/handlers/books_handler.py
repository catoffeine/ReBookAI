from aiogram import Router, Bot
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot import errors
from bot.books_core.get_books import get_books
from bot.utils.audio_to_text import audio_to_text

router = Router()

class BooksHandlerStates(StatesGroup):
    clarify = State()

async def write_answer(message: Message, text: str, user_id: int, state: FSMContext, clarify: bool = False):
    try:
        books = await get_books(text, user_id, clarify)
    except errors.NeedToClarifyError:

        # как пример
        await message.answer("Уточните запрос")
        await state.set_state(BooksHandlerStates.clarify)
    except errors.NoAvailableApis:
        await message.answer("Сервер перегружен, подождите несколько секунд и попробуйте снова...")
    else:
        # здесь надо написать как будем отвечать, books возвращает нужные данные в каком-то из форматов

        ans_text = ""
        for book in books:
            ans_text += f"Book1: {book['name']}\n"

        await state.clear()
        await message.answer(ans_text)

#_______________________
# Первичный запрос
#_______________________
# Обрабатываем текстовое сообщение
#_______________________
@router.message(F.text, StateFilter(None))
async def text_message_start(message: Message, state: FSMContext):
    text = message.text
    await write_answer(message, text, message.from_user.id, state)

# Обрабатываем аудио сообщение
@router.message(F.voice, StateFilter(None))
async def voice_message_start(message: Message, bot: Bot, state: FSMContext):
    text = await audio_to_text(bot, message.voice.file_id)
    await write_answer(message, text, message.from_user.id, state)
#_______________________


#_______________________
# Если нужно уточнить запрос
#_______________________
@router.message(F.text, StateFilter(BooksHandlerStates.clarify))
async def text_message_clarify(message: Message, state: FSMContext):
    text = message.text
    await write_answer(message, text, message.from_user.id, state, True)

@router.message(F.voice, StateFilter(BooksHandlerStates.clarify))
async def voice_message_clarify(message: Message, bot: Bot, state: FSMContext):
    text = await audio_to_text(bot, message.voice.file_id)
    await write_answer(message, text, message.from_user.id, state, True)
#_______________________