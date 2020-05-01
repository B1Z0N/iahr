from telethon import events

from . import senders
from ..utils import SingletonMeta, Delimiter, CommandDelimiter
from .. import run
from ..config import IahrConfig

from dataclasses import dataclass
from typing import Callable
import re

class CommandRegisterError(Exception):
    pass


class Register:
    """
        Like Manager, but unified to enable adding non-textbased commands
        e.g. EditMessage, ChatAction...
    """
   
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
        pr = IahrConfig.PREFIXES.get(etype)
        if pr is None:
            return IahrConfig.NEW_MSG.original
        return pr + IahrConfig.PREFIX.original
   
    ##################################################
    # Register handlers 
    ##################################################
 

    def reg(self, name, handler, about, etype=None):
        """
            Generic command handler
        """
        IahrConfig.LOGGER.info(f'registering:name={name}:about={about}')

        if etype == None or type(etype) == events.NewMessage:
            self.reg_new_msg(name, handler, about)
        else:
            self.reg_others(name, handler, about, etype) 

    def reg_new_msg(self, name, handler, about):
        """
            Register new message handler to our manager
        """
        self.app.add(name, handler, about, delimiter=IahrConfig.NEW_MSG)
        
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
        self.app.add(self.prefix(event) + name,
                handler, about, delimiter=IahrConfig.NON_NEW_MSG)
        self.client.add_event_handler(handler, event)

    def __init__(self, client, app):
        self.client = client
        self.app = app
 

        self.client.add_event_handler(
            self.run, events.NewMessage(pattern=IahrConfig.COMMAND_RE)
        )
           
 
    async def run(self, event):
        """
            Process incoming message with our handlers and manager
        """
        txt = event.message.raw_text
        IahrConfig.LOGGER.info(f'msg={txt}:usr={event.message.from_id}')
        try:
            if IahrConfig.NEW_MSG.is_command(txt):
                try:
                    sender = await self.app.exec(txt, event)
                except (run.CommandSyntaxError, run.PermissionsError, run.NonExistantCommandError) as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    await event.reply(str(e))
                except run.ExecutionError as e:
                    IahrConfig.LOGGER.error(str(e))
                    await event.reply(
                        'Incompatible commands, wrong arguments or just a buggy function'
                    )
                else:
                   await sender.send()
        except Exception as e:
            IahrConfig.LOGGER.error('exception', exc_info=True)


async def init(client):
    reg = Register(client, run.app)
    senders.reg.init(reg.reg)

