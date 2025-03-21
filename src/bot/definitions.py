import os

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN'] if 'TELEGRAM_TOKEN' in os.environ else None
DEVELOPER_ID = int(os.environ['DEVELOPER_ID']) if 'DEVELOPER_ID' in os.environ else None
DEVELOPER_CHAT_ID = int(os.environ['DEVELOPER_CHAT_ID']) if 'DEVELOPER_CHAT_ID' in os.environ else None
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(f'{ROOT_DIR}/', 'logfiles/')
USERS = "users"
DB_FILE = os.path.join(ROOT_DIR, 'database.db')
APIS_PATH = os.path.join(ROOT_DIR, 'apis.txt')
DATASET_PATH = os.path.join(ROOT_DIR, 'dataset.csv')

class ApiErrors:
    RATELIMIT = 0
    RESTRICTED = 1

BASE_USER_CONFIG = {
    "existing_books_data": {},
    "some_setting": 0
}
