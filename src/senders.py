from abc import ABC, abstractmethod
from functools import wraps

from app import app


@dataclass
class MultiArgs:
    # to show that the command returned multiple arguments, not just a list of arguments
    args: list

    
class ABCSender(ABC):
    def __init__(self, fun):
        self.fun = fun
    
    @abstractmethod
    async def send(self):
       pass

    async def __call__(self, event, *args, **kwargs):
        self.event = event
        self.res = await self.fun(event, *args, **kwargs)
        if type(self.res) != MultiArgs:
            self.res = MultiArgs([self.res])
        return self


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
    return await self.event.message.reply(self.res)
TextSender = create_sender('TextSender', __text_send)

async def __media_send(self):
    return await self.event.message.reply(file=self.res)
MediaSender = create_sender('MediaSender', __media_send)

async def __void_send(self):
    pass
VoidSender = create_sender('VoidSender', __void_send)

class IncompatibleSendersError(RuntimeError):
    pass
    
