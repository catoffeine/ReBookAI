from bot import errors
from bot.sql.users import get_user_setting, set_user_setting


async def extract_books_data(text: str, user_id: int, clarify: bool = False):
    # здесь надо построить RAG запрос и "вытянуть" нужные данные
    # text - то, что запросил пользователь
    # clarify - если False, то это первичный запрос, если True, то надо уточнить данные, дополнить
    # user_id - id пользователя для запроса к базе данных

    # далее логика запроса в RAG....

    # как пример
    books_data = {
        # обязательные
        "genre": "жанр книги",

        # необязательные
        "name": "имя книги",
        "rating": "необходимая популярность книги",
        "length": "продолжительность книги",
    }


    if clarify:
        existing_data = await get_user_setting(user_id, "existing_books_data")

        # ... делаем запросы
        # заполняем/дополняем books_data
        # ВАЖНО! Если вдруг данных недостаточно, мы не можем определить нужные нам обязательные данные, то тогда
        # raise errors.NeedToClarifyError

        # сохраняем данные в existing_books_data
        await set_user_setting(user_id, "existing_books_data", books_data)
    else:
        # ... делаем запросы
        # ВАЖНО! Если вдруг данных недостаточно, мы не можем определить нужные нам обязательные данные, то тогда
        # raise errors.NeedToClarifyError
        # сохраняем данные в existing_books_data
        await set_user_setting(user_id, "existing_books_data", books_data)



    return books_data

async def determine_best_books(books: list, text: str, n=5):
    # здесь типа надо из списка книг books по текстовому запросу пользователя вытянуть лучшие варианты (n штук),
    # если они вообще есть и запрос не односложный, если же нет, то рандомно или по какому-нибудь принципу
    # выбираем любые n книг

    return books
