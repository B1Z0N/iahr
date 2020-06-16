from telethon import events

from .. import run
from ..utils import Delimiter, CommandDelimiter
from ..config import IahrConfig

import re
from abc import ABC, abstractmethod


class CommandRegisterError(Exception):
    pass


class ABCRegister:
    def __init__(self, client, app):
        self.client = client
        self.app = app

        self.client.add_event_handler(
            self.run, events.NewMessage(pattern=IahrConfig.COMMAND_RE))

    @abstractmethod
    def reg(self, name, handler, about, event_type):
        pass

    @abstractmethod
    def run(self, event):
        pass


class Register(ABCRegister):
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
        return IahrConfig.CMD.original if pr is None else pr

    ##################################################
    # Register handlers
    ##################################################

    def reg(self, name, handler, about, etype, tags):
        """
            Generic command handler
        """
        IahrConfig.LOGGER.info(f'registering:name={name}:about={about}')

        if etype == None:
            self.reg_new_msg(name, handler, about, tags)
        else:
            self.reg_others(name, handler, about, etype, tags)

    def reg_new_msg(self, name, handler, about, tags):
        """
            Register new message handler to our manager
        """
        self.app.add(name, handler, about, tags, delimiter=IahrConfig.CMD)

    def reg_others(self, name, handler, about, event, tags):
        """
            Register non-new-message events directly as the client event handler.
            Also add it, just formally, with different delimiter
            (self.NON_NEW_MSG_COMMAND_DELIMITER) to the manager. Just so that
            we could get help, but no one could execute this handler. 

            P. S. If you do want to execute this handlers by typing, then i suggest
            you to create new `run` function like the one here, but with this command
            delimiter and don't forget to pass correct event type to the `app.exec`.
        """
        self.app.add(self.prefix(event) + name, handler, about, tags)
        self.client.add_event_handler(handler, event)

    async def run(self, event):
        """
            Process incoming message with our handlers and manager
        """
        txt = event.message.raw_text
        IahrConfig.LOGGER.info(f'msg={txt}:usr={event.message.from_id}')
        try:
            if IahrConfig.CMD.is_command(txt):
                try:
                    sender = await self.app.exec(txt, event)
                except run.NonExistantCommandError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    await event.reply(str(e) + '\n\nsee **.help**')
                except run.CommandSyntaxError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    await event.reply(str(e) + '\n\nsee **.synhelp**')
                except run.PermissionsError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    msg = str(
                        e
                    ) + '\n\nsee **.allowedusr**, if you are allowed to ◔ ⌣ ◔'
                    await event.reply(msg)
                except run.IgnoreError as e:
                    IahrConfig.LOGGER.info(f'Empty handler due to chat {e.chat} ignore')
                except run.ExecutionError as e:
                    IahrConfig.LOGGER.error(str(e))
                    await event.reply('{}:\n\n`{}`\n\n{}'.format(
                        'Incompatible commands, wrong arguments or just a buggy function',
                        e.args[0], 'Is that what you truly meant?'))
                else:
                    await sender.send()
        except Exception as e:
            IahrConfig.LOGGER.error('exception', exc_info=True)
