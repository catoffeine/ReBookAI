import asyncio
import glob
import json
import os
import re

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

from playwright.async_api import async_playwright

genres_books_links = [
    ["детективы", "https://www.litres.ru/genre/trillery-5204/"],
    ["детективы", "https://www.litres.ru/genre/krutoy-detektiv-5265/"],
    ["детективы", "https://www.litres.ru/genre/zarubezhnye-5219/"],
    ["детективы", "https://www.litres.ru/genre/politicheskie-5264/"],
    ["детективы", "https://www.litres.ru/genre/shpionskie-5263/"],
    ["детективы", "https://www.litres.ru/genre/ironicheskie-5262/"],
    ["детективы", "https://www.litres.ru/genre/klassicheskie-5261/"],
    ["детективы", "https://www.litres.ru/genre/sovremennye-5259/"],

    ["фантастика", "https://www.litres.ru/genre/popadancy-5082/"],
    ["фантастика", "https://www.litres.ru/genre/zarubezhnaya-5080/"],
    ["фантастика", "https://www.litres.ru/genre/umoristicheskaya-5079/"],
    ["фантастика", "https://www.litres.ru/genre/socialnaya-5078/"],
    ["фантастика", "https://www.litres.ru/genre/kosmicheskaya-5077/"],
    ["фантастика", "https://www.litres.ru/genre/detektivnaya-5076/"],
    ["фантастика", "https://www.litres.ru/genre/geroicheskaya-5075/"],
    ["фантастика", "https://www.litres.ru/genre/boevaya-fantastika-5074/"],
    ["фантастика", "https://www.litres.ru/genre/nauchnaya-5073/"],
    ["фантастика", "https://www.litres.ru/genre/kiberpank-5072/"],
    ["фантастика", "https://www.litres.ru/genre/istoricheskaya-5071/"],
    ["фантастика", "https://www.litres.ru/genre/stimpank-5084/"],
    ["фантастика, любовные романы", "https://www.litres.ru/genre/lyubovno-fantasticheskiye-5090/"],

    ["любовные романы", "https://www.litres.ru/genre/zarubezhnyye-5091/"],
    ["любовные романы", "https://www.litres.ru/genre/eroticheskie_romany-5089/"],
    ["любовные романы", "https://www.litres.ru/genre/korotkiye-5088/"],
    ["любовные романы", "https://www.litres.ru/genre/istoricheskiye-5087/"],
    ["любовные романы", "https://www.litres.ru/genre/ostrosyuzhetnyye-5086/"],
    ["любовные романы", "https://www.litres.ru/genre/sovremennyye-5085/"],

    ["эротика и секс", "https://www.litres.ru/genre/seksualnyye-rukovodstva-5310/"],
    ["эротика и секс", "https://www.litres.ru/genre/eroticheskaya_literatura-5308/"],
    ["эротика и секс, любовные романы", "https://www.litres.ru/genre/eroticheskie_romany-5089/"],
    ["эротика и секс", "https://www.litres.ru/genre/eroticheskie_rasskazy-6799/"],
    ["эротика и секс, фэнтези", "https://www.litres.ru/genre/eroticheskoe_fantasy-6803/"],

    ["юмористическая литература", "https://www.litres.ru/genre/zarubezhnyy-umor-5202/"],
    ["юмористическая литература", "https://www.litres.ru/genre/anekdoty-5201/"],
    ["юмористическая литература", "https://www.litres.ru/genre/umoristicheskie-stihi-5200/"],
    ["юмористическая литература", "https://www.litres.ru/genre/umoristicheskaya-proza-5199/"],

    ["приключения", "https://www.litres.ru/genre/zarubezhnye-5096/"],
    ["приключения", "https://www.litres.ru/genre/istoricheskie-5095/"],
    ["приключения", "https://www.litres.ru/genre/puteshestviyah-5094/"],
    ["приключения", "https://www.litres.ru/genre/morskie-5092/"],
    ["приключения", "https://www.litres.ru/genre/klassika_priklyuchenij-203025/"],

    ["young adult", "https://www.litres.ru/genre/young-adult-174918/?view=showroom"],

    ["легкая проза", "https://www.litres.ru/genre/legkaya_proza-201926/"],

    ["фэнтези", "https://www.litres.ru/genre/boevoe-5232/"],
    ["фэнтези", "https://www.litres.ru/genre/lubov-5231/"],
    ["фэнтези", "https://www.litres.ru/genre/drakony-5230/"],
    ["фэнтези", "https://www.litres.ru/genre/russkoe-5229/"],
    ["фэнтези", "https://www.litres.ru/genre/umoristicheskoe-5228/"],
    ["фэнтези", "https://www.litres.ru/genre/istoricheskoe-5227/"],
    ["фэнтези", "https://www.litres.ru/genre/volshebniki-5226/"],
    ["фэнтези", "https://www.litres.ru/genre/geroicheskoe_fentezi-6791/"],
    ["фэнтези", "https://www.litres.ru/genre/detective_fentezi-6337/"],
    ["фэнтези, фантастика", "https://www.litres.ru/genre/popadancy-5082/"],
    ["фэнтези", "https://www.litres.ru/genre/zarubezhnye-5218/"],
    ["фэнтези", "https://www.litres.ru/genre/vampiry-5224/"],
    ["фэнтези", "https://www.litres.ru/genre/gorodskoe-5225/"],
    ["фэнтези", "https://www.litres.ru/genre/magicheskie-akademii-201663/"],

    ["ужасы/мистика", "https://www.litres.ru/genre/mistika-5223/"],
    ["ужасы/мистика", "https://www.litres.ru/genre/uzhasy-5222/"],

    ["фанфик", "https://www.litres.ru/genre/fanfik-5019/"],

    ["боевики", "https://www.litres.ru/genre/knigi-boeviki-ostrosugetnaya-5014/"],
    ["боевики", "https://www.litres.ru/genre/zarubezhnye-5206/"],
    ["боевики", "https://www.litres.ru/genre/boeviki-5207/"],
    ["боевики", "https://www.litres.ru/genre/vesterny-5093/"],
    ["боевики", "https://www.litres.ru/genre/kriminalnye-boeviki-5203/"],
    ["боевики, фантастика", "https://www.litres.ru/genre/boevaya-fantastika-5074/"],

    ["классика жанра", "https://www.litres.ru/genre/klassika-zhanra-201671/"],
    ["классика жанра, детективы", "https://www.litres.ru/genre/klassicheskie-5261/"],
    ["классика жанра", "https://www.litres.ru/genre/klassicheskie-lubovnye-romany-201687/"],
    ["классика жанра", "https://www.litres.ru/genre/klassika-fentezi-201679/"],
    ["классика жанра", "https://www.litres.ru/genre/klassika-fantastiki-56305/"],
    ["классика жанра, приключения", "https://www.litres.ru/genre/klassika_priklyuchenij-203025/"],

    ["серьезное чтение", "https://www.litres.ru/genre/klassicheskaya-literatura-5028/"],
    ["серьезное чтение", "https://www.litres.ru/genre/knigi-sovremennaya-proza-5015/?view=showroom"],
    ["серьезное чтение, история", "https://www.litres.ru/genre/biografii-memuary-5169/?view=showroom"],
    ["серьезное чтение", "https://www.litres.ru/genre/ob-istorii-serezno-201719/"],
    ["серьезное чтение", "https://www.litres.ru/genre/stihi-poeziya-201711/"],
    ["серьезное чтение", "https://www.litres.ru/genre/pesy-dramaturgiya-201695/"],

    ["история", "https://www.litres.ru/genre/istoricheskoe-5227/"],
    ["история", "https://www.litres.ru/genre/istoricheskie-5095/"],
    ["история", "https://www.litres.ru/genre/knigi_o_voyne-5205/"],
    ["история, любовные романы", "https://www.litres.ru/genre/istoricheskiye-5087/"],
    ["история", "https://www.litres.ru/genre/dokumentalnaya-literatura-5170/"],
    ["история", "https://www.litres.ru/genre/istoricheskaya-literatura-5209/"],
    ["история, фантастика", "https://www.litres.ru/genre/istoricheskaya-5071/"],
    ["история", "https://www.litres.ru/genre/morskie-5092/"],
    ["история", "https://www.litres.ru/genre/populyarno-ob-istorii-201727/"],

    ["комиксы и манга", "https://www.litres.ru/genre/zapadnye-komiksy-274063/"],
    ["комиксы и манга", "https://www.litres.ru/genre/aziatskie-komiksy-274066/"],
    ["комиксы и манга", "https://www.litres.ru/genre/webtoon-275083/"],
    ["комиксы и манга", "https://www.litres.ru/genre/aziatskie-novelly-276439/"],
    ["комиксы и манга", "https://www.litres.ru/genre/non-fikshn-v-komiksah-276445/"],
    ["комиксы и манга", "https://www.litres.ru/genre/rumanga-i-rukomiksy-276448/"],
    ["комиксы и манга", "https://www.litres.ru/genre/komiksy-dlya-detey-276442/"],

    ["детские книги", "https://www.litres.ru/genre/zarubezhnye-5111/"],
    ["детские книги", "https://www.litres.ru/genre/detektivy-5109/"],
    ["детские книги", "https://www.litres.ru/genre/fantastika-5108/"],
    ["детские книги", "https://www.litres.ru/genre/priklucheniya-5107/"],
    ["детские книги", "https://www.litres.ru/genre/skazki-5106/"],
    ["детские книги", "https://www.litres.ru/genre/bukvari-5313/"],
    ["детские книги", "https://www.litres.ru/genre/proza-5104/"],
    ["детские книги", "https://www.litres.ru/genre/uchebnaya-literatura-5103/"],
    ["детские книги", "https://www.litres.ru/genre/vneklassnoye-chteniye-5102/"],
    ["детские книги", "https://www.litres.ru/genre/detskaya_pazvivayushaya_literatura-6481/"],

    ["знания и навыки", "https://www.litres.ru/genre/nauchno-populyarnaya-literatura-5031/?view=showroom"],
    ["знания и навыки", "https://www.litres.ru/genre/uchebnaya-nauchnaya-literatura-5030/"],
    ["знания и навыки", "https://www.litres.ru/genre/kompyuternaya-literatura-5024/?view=showroom"],
    ["знания и навыки", "https://www.litres.ru/genre/knigi-iskusstvo-5020/"],
    ["знания и навыки", "https://www.litres.ru/genre/samorazvitiye-lichnostnyy-rost-5253/?view=showroom"],
    ["знания и навыки", "https://www.litres.ru/genre/istorii-iz-zhizni-53055/"],
    ["знания и навыки", "https://www.litres.ru/genre/izuchenie-yazykov-6356/"],

    ["спорт.здоровье.красота", "https://www.litres.ru/genre/seksualnyye-rukovodstva-5310/"],
    ["спорт.здоровье.красота", "https://www.litres.ru/genre/krasota-201767/"],
    ["спорт.здоровье.красота", "https://www.litres.ru/genre/sport-201759/"],
    ["спорт.здоровье.красота", "https://www.litres.ru/genre/medicina-i-zdorove-201743/"],
]

base_url = "https://litres.ru"

save_data_info = {}
save_data_path = "save_data.json"

params = {
    "art_types": "text_book",
    "languages": ["ru", "en"],
    "only_high_rated": "true"
}

async def find_property(page, needed_property):
    outer_span = await page.query_selector(f"span:has-text('{needed_property}')")

    if outer_span:
        inner_div = await outer_span.query_selector("xpath=..")
        if inner_div:
            container_div = await inner_div.query_selector("xpath=..")
            if container_div:
                target_spans = await container_div.query_selector_all("span")
                if target_spans and len(target_spans) > 1:
                    target_text = await target_spans[1].inner_text()
                    return target_text

    return None

async def fetch_book_info(url):
    print("Entering fetching book_info with url {url}".format(url=url))
    result = {
        "url": url.split('?')[0],
        "description": "",
        "age_limit": "",
        "writing_date": "",
        "volume": "",
        "author": "",
        "title": "",
        "rating": "",
        "reviews_count": ""
    }
    retries = 3
    while retries:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                # await asyncio.sleep(0.5)

                buttons = await page.query_selector_all("div[class*='AdultModal_buttons'] button")
                if buttons is not None and len(buttons) > 1:
                    print("adult content, clicking the button...")
                    await page.click("div[class*='AdultModal_buttons'] button")

                unwrap_button = await page.query_selector("a[role='button'][class*='Truncate_readMore']")
                if unwrap_button:
                    await page.click("a[role='button'][class*='Truncate_readMore']")

                await page.wait_for_selector(
                    "div[data-testid='book__infoAboutBook--wrapper'] div[class*='BookCard_truncate']", timeout=2500)

                description_container = await page.query_selector("div[data-testid='book__infoAboutBook--wrapper'] div[class*='BookCard_truncate']")
                description_div = await description_container.query_selector("div > div")

                description = await description_div.inner_text()
                description = description.strip().rstrip("Свернуть").replace("***", "")

                age_limit = await find_property(page, "Возрастное ограничение")
                writing_date = await find_property(page, "Дата написания")
                volume = await find_property(page, "Объем")
                volume_pages = await find_property(page, "Общее кол-во страниц")
                if volume_pages:
                    volume = volume_pages

                await page.wait_for_selector("h1[class*='BookCard_book__title']", timeout=2500)
                title_h1 = await page.query_selector("h1[class*='BookCard_book__title']")
                title = await title_h1.inner_text()

                # await page.wait_for_selector("div[class*='BookDetailsHeader_persons']", timeout=2500)
                author_div = await page.query_selector("div[class*='BookDetailsHeader_persons']")
                author = await author_div.inner_text() if author_div else ""

                await page.wait_for_selector("div[class*='BookFactoids_primary']", timeout=2500)
                rating_div = await page.query_selector("div[class*='BookFactoids_primary']")
                rating = await rating_div.inner_text()

                await page.wait_for_selector("div[class*='BookFactoids_secondary']", timeout=2500)
                reviews_count_div = await page.query_selector("div[class*='BookFactoids_secondary']")
                reviews_count = await reviews_count_div.inner_text()

                if not age_limit or not writing_date or not volume or not description \
                    or not title or not author or not rating or not reviews_count:
                    return None

                try:
                    reviews_count_temp = re.findall(r'\d+', reviews_count)
                    if len(reviews_count_temp) == 0:
                        reviews_count = "0"
                    else:
                        reviews_count = reviews_count_temp[0]
                except Exception:
                    pass

                images = "0"
                try:
                    volume_temp = re.findall(r'\d+', volume)
                    if len(volume_temp) > 1:
                        volume = volume_temp[0]
                        images = volume_temp[1]
                    else:
                        volume = volume_temp[0]

                except Exception:
                    pass

                rating = rating.replace(",", ".")

                if "Авторы" in author:
                    author = author.replace("Авторы", "")
                elif "Автор" in author:
                    author = author.replace("Автор", "")

                result["description"] = description.strip()
                result["age_limit"] = age_limit
                result["writing_date"] = writing_date
                result["volume"] = volume
                result["author"] = author.replace("\n", "").strip()
                result["title"] = title
                result["reviews_count"] = reviews_count
                result["rating"] = rating
                result["images"] = images
                result["images_ratio"] = str(min(1.0, float(images) / float(volume)))

                await browser.close()
                return result
        except Exception as e:
            print(f"Error fetching book info: {repr(e)}")
            await asyncio.sleep(15)
            retries -= 1
    print("Error fetching book, returning None")
    return None

def save_data(_save_data_info):
    with open(save_data_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(_save_data_info))

def load_data():
    global save_data_info

    if not os.path.exists(save_data_path):
        return {}

    with open(save_data_path, "r", encoding="utf-8") as f:
        save_data_info = json.loads(f.read())
        return save_data_info

def save_books(new_books, path):
    if os.path.exists(path):
        csv = pd.read_csv(path, encoding="utf-8")
    else:
        csv = pd.DataFrame({
            "title": [],
            "author": [],
            "genre": [],
            "subgenre": [],
            "writing_date": [],
            "volume": [],
            "images": [],
            "images_ratio": [],
            "description": [],
            "age_limit": [],
            "rating": [],
            "reviews_count": [],
            "litres_url": []
        })

    row_count = len(list(csv.iterrows()))
    print("number of rows is", row_count)
    print(f"len of new_books is {len(new_books)}")
    none_count = 0
    count = 0

    for i, book in enumerate(new_books):
        if book is None:
            none_count += 1
            continue
        count += 1

        if book["title"] in csv["title"]:
            none_count += 1
            count -= 1
            print("same value, skipping...")
            continue

        csv["title"] = csv["title"].astype("string")
        csv.loc[row_count + i, "title"] = book["title"]

        csv["author"] = csv["author"].astype("string")
        csv.loc[row_count + i, "author"] = book["author"]

        csv["writing_date"] = csv["writing_date"].astype("string")
        csv.loc[row_count + i, "writing_date"] = book["writing_date"]

        csv["volume"] = csv["volume"].astype("string")
        csv.loc[row_count + i, "volume"] = book["volume"]

        csv["description"] = csv["description"].astype("string")
        csv.loc[row_count + i, "description"] = book["description"]

        csv["age_limit"] = csv["age_limit"].astype("string")
        csv.loc[row_count + i, "age_limit"] = book["age_limit"]

        csv["rating"] = csv["rating"].astype("string")
        csv.loc[row_count + i, "rating"] = book["rating"]

        csv["reviews_count"] = csv["reviews_count"].astype("string")
        csv.loc[row_count + i, "reviews_count"] = book["reviews_count"]

        csv["images"] = csv["images"].astype("string")
        csv.loc[row_count + i, "images"] = book["images"]

        csv["litres_url"] = csv["litres_url"].astype("string")
        csv.loc[row_count + i, "litres_url"] = book["url"]

        csv["subgenre"] = csv["subgenre"].astype("string")
        csv.loc[row_count + i, "subgenre"] = book["subgenre"]

        csv["genre"] = csv["genre"].astype("string")
        csv.loc[row_count + i, "genre"] = book["genre"]

        csv["images_ratio"] = csv["images_ratio"].astype("string")
        csv.loc[row_count + i, "images_ratio"] = book["images_ratio"]

    csv.to_csv(path, index=False, encoding="utf-8")
    return count, none_count

async def fetch(client: httpx.AsyncClient, url, genre, max_pages=25):
    print("________________")
    print(f"Fetching url {url}...")
    save_data_info = load_data()
    if url not in save_data_info:
        save_data_info[url] = {}

    output_csv_path = None
    subgenre = None

    page = 1
    if url in save_data_info:
        print("url in save_data_info, getting...")
        page = save_data_info[url]["page"] if "page" in save_data_info[url] else 1
        subgenre = save_data_info[url]["subgenre"] if "subgenre" in save_data_info[url] else None

    print(f"current_page is {page}")

    books_container = None
    while True and page <= max_pages:
        try:
            if page != 1:
                params["page"] = page
            print(f"current page is {page}")
            retries = 6
            while retries:
                print("trying to get page...")
                try:
                    response = await client.get(url, params=params, timeout=10000)
                    response.raise_for_status()
                except Exception as e:
                    print(f"Exception while connection to server: {repr(e)}")
                    retries -= 1
                    if retries == 0:
                        return
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                if subgenre is None:
                    subgenre = soup.find("span", class_=lambda x: x and "PageHeader_title__text" in x).text.lower()
                    subgenre = subgenre.replace("/", "")
                    save_data_info[url]["subgenre"] = subgenre
                    print(f"subgenre is {subgenre}")

                books_container = soup.find("div", class_=lambda x: x and "ArtsGrid_grid" in x)

                if books_container is None:
                    print("books container is None, retrying...")
                    retries -= 1
                    if retries == 0:
                        print("out of retries, quitting...")
                        return
                    continue
                else:
                    print("books container is not None, quitting...")
                    break

            if books_container is None:
                print("books container is None, returning...")
                return

            books_url = []
            for book_container in books_container.find_all("div"):
                link = book_container.find("a", class_=lambda x: x and "Art_content__link" in x)
                if link is None or "href" not in link.attrs or "audiobook" in link["href"]:
                    continue
                books_url.append(urljoin(base_url, link["href"]))
            print(f"books_url got, it's length: {len(books_url)}")

            books_descriptions = []
            for i, book_url in enumerate(books_url):
                books_descriptions.append(await fetch_book_info(book_url))
                print(f"handled {i + 1} out of {len(books_url)} links")

            for description in books_descriptions:
                if description is not None:
                    description["subgenre"] = subgenre
                    description["genre"] = genre

            if output_csv_path is None:
                output_csv_path = os.path.join("books", subgenre + ".csv")

            saved_books, missed_books = save_books(books_descriptions, output_csv_path)
            print(f"{saved_books} books saved, {missed_books} books skipped because of None")

            page += 1
            save_data_info[url]["page"] = page

            save_data(save_data_info)
            print("save_data_info is saved")

        except Exception as e:
            print(f"Error fetching {url}: {repr(e)}")
            return

async def fetch_all():
    if not os.path.exists("books"):
        os.mkdir("books")

    for url_item in genres_books_links:
        async with httpx.AsyncClient() as client:
            await fetch(client, url_item[1], url_item[0])

def create_dataset(dataset_path, csv_files_dir):
    print("creating dataset...")
    file_paths = glob.glob(os.path.join(csv_files_dir, '*.csv'))
    dataframes = [pd.read_csv(file) for file in file_paths]
    combined = pd.concat(dataframes, ignore_index=True)
    combined = combined.drop_duplicates()

    combined.to_csv(dataset_path, index=False)
    print(f"dataset created successfully and saved to {dataset_path}")

def combine_genres(dataset_path):
    df = pd.read_csv("dataset.csv", sep=";", encoding="cp1251")

    result = (
        df.groupby(["title", "author", "age_limit", "writing_date", "volume", "images", "description", "reviews_count", "rating", "litres_url"], as_index=False).agg({
            "genre": lambda x: ", ".join(set(x)),
            "subgenre": lambda x: ", ".join(set(x))
        })
    )

    result.to_csv("combined_dataset.csv", index=False, encoding="cp1251", sep=";")

async def main():
    # await fetch_all()
    # create_dataset("dataset.csv", "books")
    combine_genres("dataset.csv")

if __name__ == '__main__':
    asyncio.run(main())