from telethon import events

from iahr.exception import IahrBaseError
from iahr import run
from iahr.utils import Delimiter, CommandDelimiter, EventService
from iahr.config import IahrConfig

import re
import traceback
from abc import ABC, abstractmethod


class IahrRoutineRegisterError(IahrBaseError):
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
        e.g. EditMessage, ...
    """

    ##################################################
    # Register handlers
    ##################################################

    def reg(self, name, handler, about, etype, tags):
        """
            Generic command registering
        """
        IahrConfig.LOGGER.info(f'registering:name={name}:about={about}')
        etype = EventService.to_type(etype)
        name = EventService.prefix(name) + name

        self.app.add(name, handler, about, etype, tags)

    async def run(self, event):
        if type(event) is events.NewMessage.Event:
            await self.run_new_msg(event)
        else:
            await self.run_others(event)

    async def run_new_msg(self, event):
        """
            Process incoming message with our handlers and manager
        """
        txt = event.message.raw_text
        IahrConfig.LOGGER.info(f'msg={txt}:usr={event.message.from_id}')
        try:
            if IahrConfig.CMD.is_command(txt):
                try:
                    sender = await self.app.exec(event, txt)
                except run.IahrNonExistantCommandError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    await event.reply(str(e) + IahrConfig.LOCAL['See cmds'])
                except run.IahrCommandSyntaxError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    await event.reply(str(e) + IahrConfig.LOCAL['See synhelp'])
                except run.IahrPermissionsError as e:
                    IahrConfig.LOGGER.error(f'{e}')
                    msg = str(e) + IahrConfig.LOCAL['See allowedusr']
                    await event.reply(msg)
                except run.IahrIgnoreError as e:
                    IahrConfig.LOGGER.info(
                        f'Empty handler due to chat {e.chat} ignore')
                except run.IahrExecutionError as e:
                    IahrConfig.LOGGER.error(str(e))
                    await event.reply(
                        IahrConfig.LOCAL['Incompatible commands'].format(
                            e.args[0]))
                    IahrConfig.LOGGER.debug(traceback.print_exc())
                except IahrBaseError as e:
                    await event.reply(str(e))
                else:
                    await sender.send()
        except Exception as e:
            IahrConfig.LOGGER.error('exception', exc_info=True)
            IahrConfig.LOGGER.debug(traceback.print_exc())

    async def run_others(self, event):
        try:
            await self.app.exec(event)
        except Exception as e:
            IahrConfig.LOGGER.error('exception', exc_info=True)
            IahrConfig.LOGGER.debug(traceback.print_exc())
