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
        self.handlers = { etype.__name__ : {} for etype in IahrConfig.PREFIXES.keys() }
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
        return {key: val.get_state() for key, val in dct.items()}

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
                handlers = dct['handlers'] 
                commands = dct['commands']

                return commands, handlers
        else:
            return {}, {etype.__name__ : {} for etype in IahrConfig.PREFIXES.keys()}

    def init_routine(self, name, fun, about, etype):
        """
            Check if routine that is being added is not in state,
            if it is, set her state appropriately
        """
        state = self.commands_state if etype is events.NewMessage else self.handlers_state[etype.__name__]
        routine = Routine(fun, about)
        if state := state.get(name):
            routine.set_state(state)
        return routine

    def full_name(self, etype, command):
        if etype is events.NewMessage:
            return IahrConfig.CMD.full_command(command)
        return command

    def add_routine(self, etype, name, routine):
        if etype is events.NewMessage:
            self.commands[name] = routine
        else:
            self.handlers[etype.__name__][name] = routine

    def add_tags(self, tags, name):
        for tag in tags:
            if tag in self.tags:
                self.tags[tag].add(name)
            else:
                self.tags[tag] = { name }

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

    def add(self, name: str, handler: Callable, about: str, etype: type, tags: set):
        IahrConfig.LOGGER.info(f'adding handler:name={name}:etype={etype}')

        name = self.full_name(etype, name)
        routine = self.init_routine(name, handler, about, etype)

        self.add_routine(etype, name, routine)
        self.add_tags(tags, name)

    async def exec(self, event, qstr=None):
        action = await ActionData.from_event(event)
        is_ignored = not self.is_allowed_chat(action.chatid)

        if qstr is not None:
            return await self.exec_new_msg(event, qstr, action, is_ignored)
        else:
            return await self.exec_others(event, action, is_ignored)

    async def exec_new_msg(self, event, qstr, action: ActionData, is_ignored):
        IahrConfig.LOGGER.info(f'executing query:qstr={qstr}')

        runner = Executer(qstr, self.commands, action, is_ignored)
        return await runner.run()

    async def exec_others(self, event, action: ActionData, is_ignored):
        etype = type(event)
        IahrConfig.LOGGER.info(f'executing handler:etype={etype}')

        handlers = self.handlers.get(etype.__name__)
        if handlers is None:
            return

        for handler in handlers:
            handler = handler.get_handler(action.uid, action.chatid)
            if handler is None:
                continue

            sender = await handler(event)
            await sender.send()
        