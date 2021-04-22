from os import path, getenv  # env vars to tell where the iahr data
from dotenv import load_dotenv  # telethon session file is being stored
load_dotenv()  # and some tg secrets to initialize client

TG_API_ID = getenv('TG_API_ID')
TG_API_HASH = getenv('TG_API_HASH')
TG_SESSION_PATH = path.abspath(getenv('TG_SESSION_PATH'))

import commands  # userspace routines
from telethon import TelegramClient  # telegram
from iahr import init  # iahr


def make_client():
    client = TelegramClient(TG_SESSION_PATH, TG_API_ID, TG_API_HASH)
    client.parse_mode = 'markdown'
    return client


async def main(client):
    await init(client)
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__':
    client = make_client()
    client.loop.run_until_complete(main(client))
    client.loop.close()
