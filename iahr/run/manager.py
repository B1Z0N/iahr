from ..utils import SingletonMeta, ActionData, AccessList
from .runner import Executer, Query, Routine
from .runner import ExecutionError, CommandSyntaxError, PermissionsError, NonExistantCommandError
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
        self.commands = {}
        self.tags = {}
        self.chatlist = AccessList(allow_others=False)
        self.state = self.load()
        atexit.register(self.dump)

    @abstractmethod
    def add(self, command: str, handler: Callable, about: str, delimiter):
        """ 
            Abstract method to add command to the manager dict
        """
        pass

    @abstractmethod
    async def exec(self, qstr, event):
        """ 
            Execute query string
        """
        pass

    ##################################################
    # State management
    ##################################################

    def dump(self):
        """
            Save state(commands and routines) to the file(IahrConfig.SESSION_FNAME)
        """
        IahrConfig.LOGGER.info('Dumping session and exiting')
        dct = {name: cmd.get_state() for name, cmd in self.commands.items()}
        dct = { 'commands' : dct, 'chatlist' : self.chatlist }
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
                return dct['commands']
        else:
            return {}

    def init_routine(self, command, handler, about):
        """
            Check if routine that is being added is not in state,
            if it is, set her state appropriately
        """
        routine = Routine(handler, about)
        if state := self.state.get(command):
            routine.set_state(state)
        return routine

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

    def add(self, command: str, handler: Callable, about: str, tags, delimiter=None):
        """
            Add a handler and it's name to the list
        """
        IahrConfig.LOGGER.info(f'adding handler:name={command}:about={about}')

        if delimiter is not None:
            command = delimiter.full_command(command)
        routine = self.init_routine(command, handler, about)

        self.commands[command] = routine

        for tag in tags:
            if tag in self.tags:
                self.tags[tag].add(command)
            else:
                self.tags[tag] = { command }


    async def exec(self, qstr, event):
        """
            Execute query where qstr is raw command text
        """
        print(self.tags)
        IahrConfig.LOGGER.info(f'executing query:qstr={qstr}')
        action = await ActionData.from_event(event)

        is_ignored = not self.is_allowed_chat(action.chatid)
        runner = Executer(qstr, self.commands, action, is_ignored)
        return await runner.run()
