import os
from dotenv import load_dotenv

from telethon import TelegramClient
from iahr.reg import init, Register
from iahr.config import IahrConfig
from iahr.utils import CommandDelimiter

import commands 

# constants
API_ID = 'TG_API_ID'
API_HASH = 'TG_API_HASH'
TG_SESSION_PATH = 'TG_SESSION_PATH'



def make_client():
    api_id = os.getenv(API_ID)
    api_hash = os.getenv(API_HASH)
    tg_session_path = os.path.abspath(os.getenv(TG_SESSION_PATH))
    client = TelegramClient(tg_session_path, api_id, api_hash)
    return client

async def main(client):
    await init(client)
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__': 
    load_dotenv()
    client = make_client()
    client.loop.run_until_complete(main(client))
    client.loop.close()

