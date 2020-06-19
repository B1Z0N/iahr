from .. import run
from ..utils import Delayed, argstr
from ..config import IahrConfig

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

    def __str__(self):
        if len(self.args) == 1:
            return str(self.args[0])
        else:
            return str(self.args)


class ABCSender(ABC):
    """
        Abstract decorator class to encapsulate sending of output
        whether it's sending to chat or serves as input to other
        command.
    """
    def __init__(self, fun, pass_event=True, multiret=False):
        """
            1. fun - actual handler
            2. pass_event - pass or not to pass event to fun when calling 
            3. multiret - surround func return with MultiArgs
        """
        self.fun = fun
        self.pass_event = pass_event
        self.multiret = multiret
        self.event = None
        self.res = None

    def __str__(self):
        return '{{ fun: {}, passevent: {}, multiret: {}, res: {} }}'.format(
            self.fun, self.pass_event, self.multiret, self.res)

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

        if self.pass_event:
            self.res = await self.fun(event, *args, **kwargs)
        else:
            self.res = await self.fun(*args, **kwargs)

        if self.multiret is True:
            self.res = MultiArgs(self.res)
        elif type(self.res) != MultiArgs:
            self.res = MultiArgs([self.res] if self.res is not None else [])

        return self

    def __repr__(self):
        clsname = self.__class__.__name__
        return f'{clsname}(pass_event:{self.pass_event}, multiret:{self.multiret}, res:{self.res})'


def create_sender(name, sendf):
    """
        ABCSender concrete subtypes factory
    """
    Sender = type(name, (ABCSender, ), {'send': sendf})

    def create_decorator(name=None,
                         about=None,
                         take_event=True,
                         multiret=False,
                         on_event=None, 
                         tags=None):
        """
            Parameterized decorator based on command name and it's description
            event - true if function takes event as the first argument,
            false if it don't need it
        """
        def decorator(handler):
            """
                Register handler wrapped in ABCSender in Manager as a command
                with current name and description. If it is not supplied
                then name will be taken from handler itslef and description
                will be just it's name. 
                
                Doesn't change handler itself, just registers appropriate wrapper
            """
            nonlocal name, about, tags
            
            name = handler.__name__ if name is None else name
            about = '' if about is None else about
            about = '`{}`\n{}'.format(
                '\n  args: ' + argstr(handler, take_event), about)
            wrapped = wraps(handler)(Sender(handler, take_event, multiret))
            tags = set() if tags is None else set(tags)

            IahrConfig.REG.do(name, wrapped, about, on_event, tags)
            return handler

        return decorator

    return create_decorator


async def any_send(event, *args, **kwargs):
    """
        Shortcut for sending response to the same chat
        the event occured on
    """
    await event.message.reply(*args, **kwargs)


async def __text_send(self):
    res = run.Query.unescape(str(self.res))
    IahrConfig.LOGGER.info(f'sending text:{res}')
    await any_send(self.event, res)


TextSender = create_sender('TextSender', __text_send)


async def __media_send(self):
    await any_send(self.event, file=self.res.args[0])


MediaSender = create_sender('MediaSender', __media_send)


async def __void_send(self):
    pass


VoidSender = create_sender('VoidSender', __void_send)
