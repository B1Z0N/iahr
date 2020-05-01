from ..utils import SingletonMeta, ActionData
from .runner import Executer, Query, Routine
from .runner import ExecutionError, CommandSyntaxError, PermissionsError, NonExistantCommandError
from ..config import IahrConfig

from typing import Iterable, Union, Callable


class Manager(metaclass=SingletonMeta):
    """
        Contains { command_name : routine } key-value pair
        manages addition of new commands and starting it's
        execution by Executer. Only for text-based commands!
    """
    def __init__(self):
        self.commands = {}
    
    def add(self, command: str, handler: Callable, about: str, delimiter=None):
        """
            Add a handler and it's name to the list
        """
        delimiter = IahrConfig.NEW_MSG if delimiter is None else delimiter
        command = delimiter.full_command(command)
        IahrConfig.LOGGER.info(f'adding handler:name={command}:about={about}')
        self.commands[command] = Routine(handler, about)

    async def exec(self, qstr, event):
        """
            Execute query where qstr is raw command text
        """
        IahrConfig.LOGGER.info(f'executing query:qstr={qstr}')
        action = await ActionData.from_event(event)
        runner = Executer(qstr, self.commands, action)
        return await runner.run()

    def __repr__(self):
        return f'Manager({self.commands})'


app = Manager()


