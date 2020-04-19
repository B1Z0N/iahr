from manager import app

from functools import wraps
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MultiArgs:
    """
        To show that the command returned multiple arguments, 
        not just a list of arguments
    """
    args: list

    
class ABCSender(ABC):
    """
        Abstract decorator class to encapsulate sending of output
        whether it's sending to chat or serves as input to other
        command.
    """
    def __init__(self, fun):
        self.fun = fun
    

    @abstractmethod
    async def send(self):
        """
            Send final result to telegram
            (to chat or some other type of communication)
            based on input event and command result
        """
        pass

    async def __call__(self, event, *args, **kwargs):
        """
            Provide sender with:
            1. Command result - to use it in command composition
            2. Event object - to use it in sending an output(final step)
        """
        self.event = event
        self.res = await self.fun(event, *args, **kwargs)
        if type(self.res) != MultiArgs:
            self.res = MultiArgs(
                [self.res] if self.res is not None else []
            )
        return self


def create_sender(name, sendf):
    """
        ABCSender concrete subtypes factory
    """
    Sender = type(name, (ABCSender,), { 'send' : sendf })

    def create_decorator(name=None, about=None):
        """
            Parameterized decorator based on command name and it's description
        """
        def decorator(handler):
            """
                Register handler wrapped in ABCSender in Manager as a command
                with current name and description. If it is not supplied
                then name will be taken from handler itslef and description
                will be just it's name. 
                
                Doesn't change handler itself, just registers appropriate wrapper
            """
            nonlocal name
            nonlocal about
            name = handler.__name__ if name is None else name
            about = name if about is None else about
            wrapped = wraps(handler)(Sender(handler))

            app.add(name, wrapped, about)
            return handler

        return decorator

    return create_decorator 


async def any_send(event, *args, **kwargs):
    """
        Shortcut for sending response to the same chat
        the event occured on
    """
    print('anysend')
    chat = await event.get_input_chat()
    client = event.client
    return await client.send_message(chat, *args, **kwargs)


async def __text_send(self):
    return await any_send(self.event, self.res.args[0])
TextSender = create_sender('TextSender', __text_send)

async def __media_send(self):
    return await any_send(self.event, file=self.res.args[0])
Text2MediaSender = create_sender('MediaSender', __media_send)

async def __void_send(self):
    pass
VoidSender = create_sender('VoidSender', __void_send)

