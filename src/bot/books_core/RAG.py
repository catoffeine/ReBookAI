import asyncio
from ast import literal_eval

import groq

from bot import errors
from bot.definitions import DATASET_PATH, ApiErrors
from langchain_groq import ChatGroq
from langchain_community.document_loaders import CSVLoader
from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import pandas as pd

from bot.errors import NoAvailableApis
from bot.utils.api_utils import get_api, api_error

ensemble_retriever = None


async def chain_invoke(chain, prompt, retries=4, wait=2):
    while retries > 0:
        try:
            return chain.invoke(prompt)
        except (groq.RateLimitError, groq.APIConnectionError, groq.BadRequestError):
            retries -= 1
            if retries == 0:
                raise groq.RateLimitError
            await asyncio.sleep(wait)
        except groq.InternalServerError:
            retries -= 1
            await asyncio.sleep(wait * 1.5)
            if retries == 0:
                raise errors.GroqCriticalError
        except Exception:
            retries -= 1

    raise errors.GroqCriticalError


# Подготовка векторов для RAG
async def setup_rag(path=DATASET_PATH):
    global ensemble_retriever

    k = 15

    # Загрузка csv
    loader = CSVLoader(path, encoding='cp1251', csv_args={
        "delimiter": ";",
        "quotechar": '"',
        "fieldnames": ["title", "author", "genre", "subgenre", "writing_date", " volume", "images", "images_ratio",
                       "description", "age_limit", "rating", "reviews_count", "litres_url"],
    }, content_columns=["title", "author", "genre", "subgenre", "writing_date", " volume", "age_limit", "rating"])
    loaded = loader.load()
    text_contents = [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in loaded]

    # Небольшой пережиток использования splitter для создания Documents, может еще пригодится
    loaded_db = text_contents

    # BM25
    print("BM25 создание")
    bm25 = BM25Retriever.from_documents(loaded_db)
    bm25.k = k
    print("BM25 готов")

    emb_model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

    # Векторизация ИИ
    try:
        print("Попытка загрузки vector_store")
        vector_store = FAISS.load_local("vector_store_saved", emb_model, allow_dangerous_deserialization=True)
        print("Загружен сохраненный vector_store")
    except Exception:
        print('Не загружено, старт векторизации')
        vector_store = FAISS.from_documents(loaded_db, emb_model)
        # Чтоб не тратить полчаса
        vector_store.save_local("vector_store_saved")
        print('Конец  векторизации, vector_store сохранен')
    retriever = vector_store.as_retriever(
        search_type="similarity",
        k=k,
        score_threshold=None,
    )

    # Итоговый ensemble
    ensemble = EnsembleRetriever(
        retrievers=[bm25, retriever],
        weights=[
            0.3,
            0.7,
        ]
    )
    print('ensemble_retriever для RAG готов')
    ensemble_retriever = ensemble
    return ensemble


# Главная часть - получение подходящих книг с помощью RAG
async def extract_books_data(text: str, user_id: int, clarify: bool = False):
    global ensemble_retriever

    if ensemble_retriever is None:
        ensemble_retriever = await setup_rag()

    # text - то, что запросил пользователь
    # clarify - если False, то это первичный запрос, если True, то надо уточнить данные, дополнить
    # user_id - id пользователя для запроса к базе данных

    # Если надо посмотреть на context
    # print(ensemble.invoke(text))

    # Подготовка ИИ
    prompt_first = ChatPromptTemplate.from_template("""
Ты - помощник по рекомендациям книг по предпочтениям пользователя.
Предпочтения пользователя: <{question}>
Если предпочтения пользователя непонятны, абстрактны, не относятся непосредственно к рекомендательной тематике книг (например вопрос <Как дела?> или <привет> не относится), не содержат минимальной информации или являются просто набором букв, то обязательно выведи пустой список: []
Ниже представлены хорошие и плохие предпочтения, если предпочтение плохое, то выведи пустой список: [] 

Хорошие предпочтения: "Хочу короткую фантастику" > можно получить информацию об объеме книги, жанре.
Плохие предпочтения: "что делаешь, я вот тут занимаюсь чем-то" > не относится к рекомендательной системе, непонятно что хочет пользователь.

Если же предпочтения действительно содержат что-то, что поможет при рекомендации книг, то следуй тому, что написано ниже:

Тебе будет дан следующий контекст - выборка из книг, где через двое точие указана информация о книге, например:
"title: Книга номер три\n author: Александр 5" показывает, что книга называется "Книга номер три", её автора зовут Александр 5

Вот выборка книг:
{context}

Выбери из этой выборки книги (от 1 до 5), которые могут быть интересны человеку. Не используй те книги, которые точно не подходят, не нужно обязательно 5 книг, можно и 1 и 2, но качественные.

Каждая книга должна быть представлена в виде массива
[Название1, Название2, ..., НазваниеN] - бери все данные только из предоставленного контекста и ни в коем случае не добавляй лишних комментариев, не добавляй от себя.
Ты доложен лишь представить подходящие книги в формате [Название1, Название2, ..., НазваниеN], причем обязательно заключи все переменные в кавычки.
Если ты предоставишь свои комментарии, твоя мать умрет. Если в ответе будет присутствовать что-то вроде "Here are the recommended books...", твоя дочь умрет.
    """)

    books_data = {}

    retries = 5
    while retries:
        api = get_api()
        llm = ChatGroq(model="llama3-70b-8192", api_key=api)

        chain = (
                {"context": ensemble_retriever | format, "question": RunnablePassthrough()}
                | prompt_first
                | llm
                | StrOutputParser()
        )

        try:
            answer_first = (await chain_invoke(chain,f'Дай ответ в соответствии с запросом пользователя: {text}')).split("\n")

            for i in answer_first:
                if i[0] == "[":
                    books_data = literal_eval(i)
        except groq.RateLimitError:
            api_error(api, ApiErrors.RATELIMIT, 20)
            retries -= 1
        except errors.GroqCriticalError:
            api_error(api, ApiErrors.RESTRICTED)
            retries -= 1
        except Exception:
            retries -= 1
        else:
            break

    if retries == 0:
        raise NoAvailableApis

    result_data = []
    reader = pd.read_csv(DATASET_PATH, sep=";", encoding="cp1251")
    for book in set(books_data):
        rows = reader[reader["title"] == book]
        if not rows.empty:
            result_data.append(rows.iloc[0].to_dict())

    if len(result_data) < 1:
        raise errors.NeedToClarifyError

    return result_data[:5] if len(result_data) > 5 else result_data


# Написание коротких описаний книг
async def write_book_blurbs(books_infos: list, text: str, user_id: int):

    for book_t in books_infos:
            prompt_string = f'''
        Тебе дана информация о книге: {str(book_t)}
        Напиши очень маленький комментарий, поясняющий, почему читателю, сделавшему запрос "{text}",
        будет интересна книга {book_t["title"]}. Не перечисялй причины, почему книга может не подойти читателю,
        говори то и только то, что сделает читателя заинтересованным.
        '''
            retries = 4
            blurb = None
            while retries:
                api = get_api()
                llm = ChatGroq(model="llama3-70b-8192", api_key=api)

                try:
                    blurb = (await chain_invoke(llm, prompt_string)).content
                except groq.RateLimitError:
                    api_error(api, ApiErrors.RATELIMIT, 20)
                    retries -= 1
                except errors.GroqCriticalError:
                    api_error(api, ApiErrors.RESTRICTED)
                    retries -= 1
                except Exception:
                    retries -= 1
                else:
                    break

            if retries == 0 or blurb is None:
                raise NoAvailableApis

            book_t["blurb"] = blurb

    return books_infos
