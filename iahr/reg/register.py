from telethon import events

from .. import run
from ..utils import Delimiter, CommandDelimiter, ev_to_type, ev_prefix
from ..config import IahrConfig

import re
from abc import ABC, abstractmethod


class RoutineRegisterError(Exception):
    pass


class ABCRegister:
    def __init__(self, client, app):
        self.client = client
        self.app = app

        self.client.add_event_handler(
            self.run, events.NewMessage(pattern=IahrConfig.COMMAND_RE))

        for etype in IahrConfig.PREFIXES.keys():
            self.client.add_event_handler(self.run, etype())

    @abstractmethod
    def reg(self, name, handler, about, event_type, tags):
        pass

    @abstractmethod
    def run(self, event):
        pass


class Register(ABCRegister):
    """
        Like Manager, but unified to enable adding non-textbased commands
        e.g. EditMessage, ChatAction...
    """

    ##################################################
    # Register handlers
    ##################################################

    def reg(self, name, handler, about, etype, tags):
        """
            Generic command registering
        """
        IahrConfig.LOGGER.info(f'registering:name={name}:about={about}')
        etype = ev_to_type(etype)
        name = ev_prefix(name) + name
        
        self.app.add(name, handler, about, etype, tags)

    async def run(self, event):
        etype = type(event)

        if etype == events.NewMessage:
            self.run_new_msg(event)
        else:
            self.run_others(event)

    async def run_new_msg(self, event):
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
                    await event.reply(str(e) + IahrConfig.LOCAL['See cmds'])
                except run.CommandSyntaxError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    await event.reply(str(e) + IahrConfig.LOCAL['See synhelp'])
                except run.PermissionsError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    msg = str(
                        e
                    ) + IahrConfig.LOCAL['See allowedusr']
                    await event.reply(msg)
                except run.IgnoreError as e:
                    IahrConfig.LOGGER.info(f'Empty handler due to chat {e.chat} ignore')
                except run.ExecutionError as e:
                    IahrConfig.LOGGER.error(str(e))
                    await event.reply(
                        IahrConfig.LOCAL['Incompatible commands'].format(e.args[0])
                    )
                else:
                    await sender.send()
        except Exception as e:
            IahrConfig.LOGGER.error('exception', exc_info=True)

    async def run_others(self, event):
        await self.app.exec(event)
