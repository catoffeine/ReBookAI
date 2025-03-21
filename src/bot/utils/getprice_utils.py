import httpx
from bs4 import BeautifulSoup

async def get_book_price(url):
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    #     "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    # }

    try:
        async with httpx.AsyncClient() as client:
            url = url.replace("https://", "https://www.")
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    price_meta = soup.find('meta', {'itemprop': 'price'})

    if price_meta:
        price_text = price_meta.get('content')
        return price_text
    return None