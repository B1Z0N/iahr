from telethon import events

from iahr import run
from iahr.utils import Delayed, EventService, argstr
from iahr.config import IahrConfig
from iahr.exception import IahrBaseError

from functools import wraps
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Callable

import inspect


@dataclass
class MultiArgs:
    """
        To show that the command returned multiple arguments, 
        not just a list of arguments
    """
    args: list

    def get(self):
        if len(self.args) == 1:
            return self.args[0]
        else:
            return self.args

    def __str__(self):
        return str(self.get())


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
        self.pass_event, self.multiret = pass_event, multiret
        self.event, self.res = None, None

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

    async def invoke(self, *args, **kwargs):
        """
            Invoke the actual funciton and store it's result in self.res
        """
        if self.pass_event:
            self.res = await self.fun(self.event, *args, **kwargs)
        else:
            self.res = await self.fun(*args, **kwargs)

    async def __call__(self, event, *args, **kwargs):
        """
            Provide sender with:

            1. Command result - to use it in command composition
            2. Event object - to use it in sending an output(final step)

            Create new sender from current for this event.
        """
        new = type(self)(self.fun, self.pass_event, self.multiret)

        new.event = event
        await new.invoke(*args, **kwargs)

        if new.multiret is True:
            new.res = MultiArgs(new.res)
        elif type(new.res) != MultiArgs:
            new.res = MultiArgs([new.res] if new.res is not None else [])

        return new

    def __repr__(self):
        clsname = self.__class__.__name__
        return f'{clsname}(pass_event:{self.pass_event}, multiret:{self.multiret}, res:{self.res})'


def create_sender(sender: Union[Callable, ABCSender], name: str = None):
    """
        ABCSender concrete subtypes factory
    """
    if inspect.isclass(sender) and issubclass(sender, ABCSender):
        Sender, name = sender, sender.__name__
    else:
        Sender = type(name, (ABCSender, ), {'send': sender})

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
            nonlocal name, about, tags, on_event

            name = handler.__name__ if name is None else name
            on_event = events.NewMessage if on_event is None else on_event
            tags = set() if tags is None else set(tags)

            wrapped = wraps(handler)(Sender(handler, take_event, multiret))

            about = '' if about is None else about
            about = '`{}`\n{}'.format(
                '\n  args: ' + argstr(handler, take_event), about)

            IahrConfig.REG.do(name, wrapped, about, on_event, tags)
            return handler

        return decorator

    return create_decorator


async def any_send(event, *args, **kwargs):
    """
        Shortcut for sending response to the same chat
        the event occured on
    """
    if IahrConfig.EDIT_TO_RESPOND is True:
        me = await EventService.userid_from(event)
        if me == 'me':
            await event.message.edit(*args, **kwargs)
            return
    await event.message.reply(*args, **kwargs)


async def __text_send(self):
    res = run.Query.unescape(str(self.res))
    IahrConfig.LOGGER.info(f'sending text:{res}')
    await any_send(self.event, res)


TextSender = create_sender(__text_send, 'TextSender')


async def __media_send(self):
    await any_send(self.event, file=self.res.args[0])


MediaSender = create_sender(__media_send, 'MediaSender')


async def __void_send(self):
    pass


VoidSender = create_sender(__void_send, 'VoidSender')
