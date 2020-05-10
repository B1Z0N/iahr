from ..utils import SingletonMeta, ActionData
from .runner import Executer, Query, Routine
from .runner import ExecutionError, CommandSyntaxError, PermissionsError, NonExistantCommandError
from ..config import IahrConfig

from typing import Iterable, Union, Callable
from abc import ABC, abstractmethod
import json, os, atexit


class ABCManager(ABC):

    def __init__(self):
        self.commands = {}
        self.state = self.load()
        atexit.register(self.dump)

    @abstractmethod
    def add(self, command: str, handler: Callable, about: str, delimiter):
        pass

    @abstractmethod
    async def exec(self, qstr, event):
        pass

    ##################################################
    # State management
    ##################################################

    def dump(self):
        dct = {name: cmd.get_state() for name, cmd in self.commands.items()}
        with open(IahrConfig.SESSION_FNAME, 'w+') as f:
            json.dump(dct, f, indent=4, cls=Routine.JSON_ENCODER)

    def load(self):
        fname = IahrConfig.SESSION_FNAME
        if os.path.exists(fname) and os.path.getsize(fname) > 0:
            with open(fname, 'r') as f:
                return json.load(f, cls=Routine.JSON_DECODER)
        else:
            return {}

    def init_routine(self, command, handler, about):
        routine = Routine(handler, about)
        if state := self.state.get(command):
            routine.set_state(state)
        return routine

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

    def add(self, command: str, handler: Callable, about: str, delimiter=None):
        """
            Add a handler and it's name to the list
        """
        IahrConfig.LOGGER.info(f'adding handler:name={command}:about={about}')

        if delimiter is not None:
            command = delimiter.full_command(command)
        routine = self.init_routine(command, handler, about)

        self.commands[command] = routine

    async def exec(self, qstr, event):
        """
            Execute query where qstr is raw command text
        """
        IahrConfig.LOGGER.info(f'executing query:qstr={qstr}')
        action = await ActionData.from_event(event)
        runner = Executer(qstr, self.commands, action)
        return await runner.run()

