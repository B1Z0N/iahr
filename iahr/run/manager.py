from telethon import events

from ..utils import SingletonMeta, ActionData, AccessList
from .runner import Executer, Query, Routine
from .runner import ExecutionError, CommandSyntaxError, PermissionsError, NonExistantCommandError, IgnoreError
from ..config import IahrConfig

from typing import Iterable, Union, Callable
from abc import ABC, abstractmethod
import json, os, atexit


class ABCManager(ABC):
    """
        ABC for defining custom Managers
    """
    def __init__(self):
        """
            Load state from file and register dumping to file
            atexit
        """
        # for new message events only(commands)
        self.commands = {}
        # for all other types of events, plain handlers, can't be combined
        self.handlers = { etype : {} for etype in IahrConfig.PREFIXES.keys() }
        # tags for quick search
        self.tags = {}
        # for errignore on chat level
        self.chatlist = AccessList(allow_others=False)
        # state for dumping and loading from file
        self.commands_state, self.handlers_state = self.load()
        
        atexit.register(self.dump)

    @abstractmethod
    def add(self, command: str, handler: Callable, about: str, delimiter):
        """ 
            Abstract method to add command to the manager dict
        """
        pass

    @abstractmethod
    async def exec(self, event, qstr=None):
        """ 
            Execute query string(for new message)
            Or just a handler for other event types
        """
        pass

    ##################################################
    # State management
    ##################################################

    @staticmethod
    def get_state(dct):
        return {name: cmd.get_state() for name, cmd in dct.items()}

    def dump(self):
        """
            Save state(commands and routines) to the file(IahrConfig.SESSION_FNAME)
        """
        IahrConfig.LOGGER.info('Dumping session and exiting')
        command_dct= self.get_state(self.commands)
        handler_dct = { 
            etype : self.get_state(handlers) for etype, handlers in self.handlers.items() 
        }
        dct = { 'commands' : command_dct, 'handlers' : handler_dct, 'chatlist' : self.chatlist }

        with open(IahrConfig.SESSION_FNAME, 'w+') as f:
            json.dump(dct, f, indent=4, cls=Routine.JSON_ENCODER)

    def load(self):
        """
            Load state(commands and routines) from file(IahrConfig.SESSION_FNAME)
        """
        fname = IahrConfig.SESSION_FNAME
        if os.path.exists(fname) and os.path.getsize(fname) > 0:
            with open(fname, 'r') as f:
                dct = json.load(f, cls=Routine.JSON_DECODER)
                self.chatlist = dct['chatlist']
                return dct['commands'], dct['handlers']
        else:
            return {}, {}

    def init_routine(self, command, handler, about, etype):
        """
            Check if routine that is being added is not in state,
            if it is, set her state appropriately
        """
        routine = Routine(handler, about)
        state = self.commands_state if etype is events.NewMessage else self.handlers[etype]
        if state := state.get(command):
            routine.set_state(state)
        return routine

    def full_command(self, etype, command):
        if etype is events.NewMessage:
            return IahrConfig.CMD.full_command(command)
        return command

    def add_command(self, etype, command, routine):
        if etype is events.NewMessage:
            self.commands[command] = routine
        else:
            self.handlers[etype][command] = routine

    ##################################################
    # Chat spam tactic management
    ##################################################

    def is_allowed_chat(self, chat: str):
        return self.chatlist.is_allowed(chat)

    def allow_chat(self, chat: str):
        return self.chatlist.allow(chat)

    def ban_chat(self, chat: str):
        return self.chatlist.ban(chat)

    def __repr__(self):
        return f'Manager({self.commands})'


class Manager(ABCManager):
    """
        Contains { command_name : routine } key-value pair
        manages addition of new commands and starting it's
        execution by Executer. Only for text-based commands!

        Manages session state(basically just access rights)
    """

    ##################################################
    # Routine management
    ##################################################

    def add(self, command: str, handler: Callable, about: str, etype: type, tags: set):
        IahrConfig.LOGGER.info(f'adding handler:name={command}:etype={etype}')

        command = self.full_command(etype, command)
        routine = self.init_routine(command, handler, about, etype)
        self.add_command(etype, command, routine)

        for tag in tags:
            if tag in self.tags:
                self.tags[tag].add(command)
            else:
                self.tags[tag] = { command }

    async def exec(self, event, qstr=None):
        if qstr is None:
            await self.exec_new_msg(event, qstr)
        else:
            await self.exec_others(event)

    async def exec_new_msg(self, event, qstr):
        IahrConfig.LOGGER.info(f'executing query:qstr={qstr}')
        action = await ActionData.from_event(event)

        is_ignored = not self.is_allowed_chat(action.chatid)
        runner = Executer(qstr, self.commands, action, is_ignored)
        return await runner.run()

    async def exec_others(self, event):
        etype = type(event)
        IahrConfig.LOGGER.info(f'executing handler:etype={etype}')

        action = await ActionData.from_event(event)
        is_ignored = not self.is_allowed_chat(action.chatid)
        handlers = self.handlers.get(etype)
        if handlers is None:
            return

        for handler in handlers:
            handler = handler.get_handler(action.uid, action.chatid)
            if handler is None:
                return

            sender = await handler(event)
            sender.send()
        