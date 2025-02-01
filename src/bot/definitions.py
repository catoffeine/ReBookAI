import os

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN'] if 'TELEGRAM_TOKEN' in os.environ else None
DEVELOPER_ID = int(os.environ['DEVELOPER_ID']) if 'DEVELOPER_ID' in os.environ else None
DEVELOPER_CHAT_ID = int(os.environ['DEVELOPER_CHAT_ID']) if 'DEVELOPER_CHAT_ID' in os.environ else None
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(f'{ROOT_DIR}/', 'logfiles/')
USERS = "users"
DB_FILE = os.path.join(ROOT_DIR, 'database.db')

BASE_USER_CONFIG = {
    "some_setting": 0
}
