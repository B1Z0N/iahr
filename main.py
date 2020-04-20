import os

from telethon import TelegramClient

import default_commands
from register import init

# constants
API_ID = 'API_ID'
API_HASH = 'API_HASH'
SESSION_PATH = 'SESSION_PATH'


def make_client():
    api_id = os.getenv(API_ID)
    api_hash = os.getenv(API_HASH)
    session_path = os.path.abspath(os.getenv(SESSION_PATH))
    client = TelegramClient(session_path, api_id, api_hash)
    return client


async def main(client):
    init(client)
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__': 
    client = make_client()
    client.loop.run_until_complete(main(client))
    client.loop.close()

