import os
from telethon import TelegramClient


def make_client():
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    SESSION_PATH = os.path.abspath('./sessions/tgai28')
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    return client
