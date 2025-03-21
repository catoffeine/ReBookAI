from ast import literal_eval

from aiogram import Router, Bot
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import errors
from bot.books_core.RAG import write_book_blurbs
from bot.books_core.get_books import get_books
from bot.errors import NoAvailableApis
from bot.sql.users import get_user_setting
from bot.utils.audio_to_text import audio_to_text
from bot.utils.log_utils import get_user_logger

router = Router()

class BooksHandlerStates(StatesGroup):
    clarify = State()


async def write_answer(message: Message, text: str, user_id: int, state: FSMContext, clarify: bool = False):
    logger = get_user_logger(user_id)
    logger.info("write_answer start...")

    start_message = await message.answer("⏳ Думаем, какие книги вам лучше всего подойдут...")

    try:
        logger.info("awaiting books...")
        books = await get_books(text, user_id, clarify)
        logger.info(f"books got: {books}")
    except errors.NeedToClarifyError:
        logger.warning("need to clarify...")
        await start_message.edit_text("🔍 Кажется, нам недостаточно данных для хорошей рекомендации, пожалуйста, уточните запрос")
        # await state.set_state(BooksHandlerStates.clarify)
    except errors.NoAvailableApis:
        logger.warning("server is overloaded, need to wait...")
        await start_message.edit_text("⚠️ Сервер перегружен, подождите несколько секунд и попробуйте снова...")
    except Exception as exception:
        logger.error(f"Unhandled error: {repr(exception)}")
        await start_message.edit_text("🛠️ Неизвестная ошибка на сервере, проблема на нашей стороне, попробуйте позже...")
    else:
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text="🔍 Получить описания", callback_data="add_descriptions")

        ans_text = "Хорошо, ниже представлю книги, которые тебе могут понравиться!\n"
        for i, book in enumerate(books):
            ans_text += f'''
📖 Книга: <b>{book["title"]}</b>
🎭 Жанр(-ы): <b>{book["genre"]}</b>
👤 Автор(-ы): <b>{book["author"]}</b>
⭐ Рейтинг: <b>{str(book["rating"]).replace(".0", "")} из 5</b>
📄 Кол-во страниц: <b>{int(book["volume"])}</b>

🛒 Приобрести данную книгу можно по <a href="{book["litres_url"]}">ссылке</a>
'''
            if "price" in book:
                ans_text += f'''
💵 Текущая цена книги на Litres: {book["price"]}₽.
'''
            ans_text += "\n➖➖➖➖➖\n" if i < len(books) - 1 else ""

        ans_text += '''

<i>Если вы хотите поподробнее узнать про книги, вы можете получить их описания кнопкой ниже.</i>
'''
        await state.clear()
        await start_message.edit_text(ans_text,
                             reply_markup=keyboard_builder.as_markup(),
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True)
    logger.info("write_answer end...")

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
    text = ""
    try:
        text = await audio_to_text(bot, message.voice.file_id)
    except errors.EmptyVoiceError:
        await message.answer("⚠️ Мы не смогли обнаружить текст в голосовом сообщений, пожалуйста, уточните ваш запрос.")
    except Exception:
        await message.answer("⚠️ Ошибка во время обработки голосового сообщения, попробуйте позже...")
        return

    await write_answer(message, text, message.from_user.id, state)
#_______________________


#_______________________
# Если нужно уточнить запрос
#_______________________
# @router.message(F.text, StateFilter(BooksHandlerStates.clarify))
# async def text_message_clarify(message: Message, state: FSMContext):
#     text = message.text
#     await write_answer(message, text, message.from_user.id, state, True)
#
# @router.message(F.voice, StateFilter(BooksHandlerStates.clarify))
# async def voice_message_clarify(message: Message, bot: Bot, state: FSMContext):
#     text = await audio_to_text(bot, message.voice.file_id)
#     await write_answer(message, text, message.from_user.id, state, True)
#_______________________

#_______________________
# Если нужно получить описание
#_______________________

@router.callback_query(F.data == "add_descriptions")
async def add_descriptions(callback: CallbackQuery):
    user_id = callback.from_user.id
    logger = get_user_logger(user_id)
    logger.info("add_descriptions start...")
    if callback.message is None:
        logger.warning("callback.message is None")
        logger.info("add_descriptions end...")
        return

    try:
        current_books = literal_eval(str(await get_user_setting(user_id, "books_data")))
        current_user_request = await get_user_setting(user_id, "user_request")
    except errors.CheckUserError:
        logger.error("CheckUserError...")
        logger.info("add_descriptions end...")
        return

    if current_books is None or current_user_request is None:
        await callback.anwser("Ошибка получения описаний...")
        logger.error("error getting descriptions...")
        return

    try:
        full_books_data = await write_book_blurbs(current_books, current_user_request, user_id)
    except NoAvailableApis:
        await callback.answer()
        await callback.message.edit_text("⚠️ Сервер перегружен, подождите несколько секунд и попробуйте снова... ",
                                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    ans_text = "Хорошо, вот книги с их описаниями:\n"
    for i, book in enumerate(full_books_data):
        ans_text += f'''
📖 Книга: <b>{book["title"]}</b>
🎭 Жанр(-ы): <b>{book["genre"]}</b>
👤 Автор(-ы): <b>{book["author"]}</b>
⭐ Рейтинг: <b>{str(book["rating"]).replace(".0", "")} из 5</b>
📄 Кол-во страниц: <b>{int(book["volume"])}</b>
💭 Описание: <b>{book["blurb"]}</b>

🛒 Приобрести данную книгу можно по <a href="{book["litres_url"]}">ссылке</a>
'''

        if "price" in book:
            ans_text += f'''
💵 Текущая цена книги на Litres: {book["price"]}₽.
'''

        ans_text += "\n➖➖➖➖➖\n" if i < len(full_books_data) - 1 else ""

    await callback.answer()
    await callback.message.edit_text(ans_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    logger.info("add_descriptions end...")
#_______________________