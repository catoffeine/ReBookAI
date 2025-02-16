from bot.books_core.RAG import extract_books_data, determine_best_books
from bot.books_core.shop_links import add_shop_links


async def get_books(text: str, user_id: int, clarify: bool = False):
    data = await extract_books_data(text, user_id, clarify)

    # тут откуда-то надо получать сами книги...
    books = [
        {"name": "first_book", "description": "description"},
        {"name": "second_book", "description": "description"},
    ]

    best_books = await determine_best_books(books, text, 5)
    best_books = await add_shop_links(best_books)

    return best_books
