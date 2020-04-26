from telethon import events

from ..utils import SingletonMeta, Delimiter
from .. import run

from dataclasses import dataclass
from typing import Callable
import traceback
import re


class CommandRegisterError(Exception):
    pass


class WrongEventTypeError(CommandRegisterError):
    def __init__(self):
        msg = 'Wrong event type of a command, look at Register.EventType enum'
        super().__init__(self, msg) 


class UninitializedRegisterError(CommandRegisterError):
    def __init__(self):
        super().__init__(self, "Call `init_client` first")


class Register(metaclass=SingletonMeta):
    """
        Like Manager, but unified to enable adding non-textbased commands
        e.g. EditMessage, ChatAction...
    """
   
    ##################################################
    # All about delimiters and helpers
    ##################################################
 
    NON_NEW_MSG_COMMAND_DELIMITER = run.CommandDelimiter('!')
    NEW_MSG_COMMAND_DELIMITER = run.Query.COMMAND_DELIMITER 

    COMMAND_RE = re.compile(r'{}[^\W]+.*'.format(NEW_MSG_COMMAND_DELIMITER.in_re()))

    PREFIX_DELIMITER = Delimiter('_')

    PREFIXES = { 
        events.MessageEdited : 'edit', 
        events.MessageDeleted : 'del', 
        events.MessageRead : 'read', 
        events.ChatAction : 'chataction' , 
        events.UserUpdate : 'usrupdate', 
        events.Album : 'album',
    }    

    @staticmethod
    def to_type(event):
        """
            Return type of this event. 
            event - type or instance of an event
        """
        if not isinstance(event, type):
            return type(event)
        return event

    @classmethod
    def prefix(cls, etype):
        """
            Get prefix to different types of events
        """
        etype = cls.to_type(etype)
        pr = cls.PREFIXES.get(etype)
        if pr is None:
            return cls.NEW_MSG_COMMAND_DELIMITER.original
        return cls.NON_NEW_MSG_COMMAND_DELIMITER.original + pr + cls.PREFIX_DELIMITER.original
   
    ##################################################
    # Register handlers 
    ##################################################
 
    @dataclass
    class Handler:
        handler: Callable
        event: events.common.EventBuilder

    def reg(self, name, handler, about, etype=None):
        """
            Generic command handler
        """
        if etype == None or type(etype) == events.NewMessage:
            self.reg_new_msg(name, handler, about)
        else:
            self.reg_others(name, handler, about, etype) 

    @classmethod
    def reg_new_msg(cls, name, handler, about):
        """
            Register new message handler to our manager
        """
        run.app.add(name, handler, about, delimiter=cls.NEW_MSG_COMMAND_DELIMITER)
        
    def reg_others(self, name, handler, about, event):
        """
            Register non-new-message events directly as the client event handler.
            Also add it, just formally, with different delimiter
            (self.NON_NEW_MSG_COMMAND_DELIMITER) to the manager. Just so that
            we could get help, but no one could execute this handler. 

            P. S. If you do want to execute this handlers by typing, then i suggest
            you to create new `run` function like the one here, but with this command
            delimiter and don't forget to pass correct event type to the `app.exec`.
        """
        run.app.add(self.prefix(event) + name,
                handler, about, delimiter=self.NON_NEW_MSG_COMMAND_DELIMITER)
        if self.client is not None:
            self.client.add_event_handler(handler, event)
        else:
            self.delayed.append(self.Handler(handler, event))

    ##################################################
    # Two-step initialization
    ################################################## 

    def __init__(self):
        """
            'Pseudo' init
        """
        self.client = None
        self.delayed = []


    def init(self, client):
        """
            Complete registering handlers directly to the client
            when one is supplied. Also register our own `run` as
            the handler in this client.
        """
        self.client = client
        for handler in self.delayed:
            self.client.add_event_handler(handler.handler, handler.event)
         
        self.client.add_event_handler(
            self.run, events.NewMessage(pattern=self.COMMAND_RE)
        )

    @classmethod
    async def run(cls, event):
        """
            Process incoming message with our handlers and manager
        """
        txt = event.message.raw_text
        try:
            if cls.NEW_MSG_COMMAND_DELIMITER.is_command(txt):
                try:
                    sender = await run.app.exec(txt, event)
                except (CommandSyntaxError, PermissionsError, NonExistantCommandError) as e:
                    await event.reply(str(e))
                except ExecutionError as e:
                    print(str(e))
                    await event.reply(
                        'Incompatible commands, wrong arguments or just a buggy function'
                    )
                else:
                   await sender.send()
        except Exception as e:
            traceback.print_exc()


reg = Register()
init = reg.init


