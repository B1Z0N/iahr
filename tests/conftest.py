import decorator
import os

import pytest
from dotenv import load_dotenv
from telethon import TelegramClient

# constants

API_ID1 = 'TG_API_ID1'
API_HASH1 = 'TG_API_HASH1'
TG_SESSION_PATH1 = 'TG_SESSION_PATH1'
IAHR_SESSION_PATH1 = 'IAHR_SESSION_PATH1'

API_ID2 = 'TG_API_ID2'
API_HASH2 = 'TG_API_HASH2'
TG_SESSION_PATH2 = 'TG_SESSION_PATH2'
IAHR_SESSION_PATH2 = 'IAHR_SESSION_PATH2'


def make_client(API_ID, API_HASH, TG_SESSION_PATH):
    api_id = os.getenv(API_ID)
    api_hash = os.getenv(API_HASH)
    tg_session_path = os.path.abspath(os.getenv(TG_SESSION_PATH))
    client = TelegramClient(tg_session_path, api_id, api_hash)
    client.parse_mode = 'markdown'

    return client

@pytest.fixture(scope='session')
async def client1():
    load_dotenv()
    return await make_client(API_ID1, API_HASH1, TG_SESSION_PATH1).start()

@pytest.fixture(scope='session')
async def client2():
    load_dotenv()
    return await make_client(API_ID2, API_HASH2, TG_SESSION_PATH2).start()

@pytest.fixture(scope='session')
    async def message(self, client1, client2):
        @client2.on(events.NewMessage)
        async def get_event(event):
            return event

        


