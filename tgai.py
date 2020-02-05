from typing import Callable
from telethon import events, TelegramClient
from telethon.tl.custom import Message

class TgAI:
    def __init__(self):
        self._callbacks = {}
        self._deferred = []
    
    def on_command(
        self,
        command: str,
        callback: Callable[[Message, TelegramClient], None]
    ):
        self._callbacks[command] = callback
    
    def get_callback(self):
        def cb(event: events.NewMessage):
            pass
        return cb
