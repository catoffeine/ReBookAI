from bot.books_core.RAG import extract_books_data
from bot.sql.users import set_user_setting
from bot.utils.getprice_utils import get_book_price


async def get_books(text: str, user_id: int, clarify: bool = False):
    books_data = await extract_books_data(text, user_id, clarify)

    for book in books_data:
        price = await get_book_price(book["litres_url"])
        if price is not None:
            book["price"] = price

    await set_user_setting(user_id, "books_data", books_data)
    await set_user_setting(user_id, "user_request", text)

    return books_data
