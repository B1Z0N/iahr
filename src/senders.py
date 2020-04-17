from abc import ABC, abstractmethod
from functools import wraps

from app import app

class ABCSender(ABC):
    def __init__(self, fun):
        self.fun = fun
    
    @abstractmethod
    async def send(self):
        pass

    async def __call__(self, event, *args, **kwargs):
        self.event = event
        self.res = await self.fun(event, *args, **kwargs)
        return self

    def __getattr__(self):
        pass


def create_sender(name, sendf):
    Sender = type(name, (ABCSender,), { 'send' : sendf })

    def create_decorator(name=None, about=None):
        def decorator(handler):
            name = handler.__name__ if name is None else name
            about = name if about is None else about
            wrapped = wraps(handler)(Sender(handler))

            app.add(name, wrapped, about)
            return handler

        return decorator

    return create_decorator 


async def __text_send(self):
    return await self.msg.reply(self.res)
TextSender = create_sender('TextSender', __text_send)

async def __media_send(self):
    return await self.msg.reply(file=self.res)
MediaSender = create_sender('MediaSender', __media_send)

 
