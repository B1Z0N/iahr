# configuration before any imports
# treat it as a normal config file
from iahr.config import config

IAHR_LOG_PATH = 'etc/iahr.log'
IAHR_SESSION_PATH = 'etc/iahr.session'
TG_SESSION_PATH = 'etc/tg.session'

config(log_out=IAHR_LOG_PATH, session_fname=IAHR_SESSION_PATH)

# then normal code
import os
import commands

from dotenv import load_dotenv
from telethon import TelegramClient
from iahr import init

# constants
API_ID = 'TG_API_ID'
API_HASH = 'TG_API_HASH'


def make_client():
    api_id = os.getenv(API_ID)
    api_hash = os.getenv(API_HASH)
    tg_session_path = os.path.abspath(TG_SESSION_PATH)
    client = TelegramClient(tg_session_path, api_id, api_hash)
    client.parse_mode = 'markdown'
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
