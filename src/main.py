import os

from telethon import TelegramClient

from engine import reg

# constants
API_ID = 'API_ID'
API_HASH = 'API_HASH'
SESSIONPATH = 'SESSION_PATH'
VOICE_API_URL = 'VOICEAPI_URL'


def make_client():
    API_ID = os.getenv(API_ID)
    API_HASH = os.getenv(API_HASH)
    SESSION_PATH = os.path.abspath(os.getenv(SESSION_PATH))
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    return client


async def main():
    await reg(client)
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__': 
    client = make_client()
    client.loop.run_until_complete(main())
    client.loop.close()
