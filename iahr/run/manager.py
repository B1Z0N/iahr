from telethon import events

from iahr.utils import SingletonMeta, ActionData, AccessList
from iahr.config import IahrConfig, IahrConfigError
from iahr.run.runner import Executer, Query, Routine
from iahr.run.runner import ExecutionError, CommandSyntaxError, PermissionsError, NonExistantCommandError, IgnoreError

from typing import Iterable, Union, Callable
from abc import ABC, abstractmethod
import json, os, atexit


class PrefixMismatchError(IahrConfigError):
    """
        Exception to raise, when IahrConfig.PREFIXES were changed
        but session file remains with old ones
    """
    def __init__(self, events: set):
        before = events
        after = set(IahrConfig.PREFIXES.values())

        msg = '\n\n\tIt seems, that you\'ve changed your config '
        msg += '\n\tand event prefixes don\'t match now:\n'
        msg += f'\n\told ones: {before}\n\tnew ones: {after}'
        msg += '\n\n\tRevert changes in config or remove iahr.session file '
        msg += '\n\tor manually rename prefixes in it'

        super().__init__(msg)

    @classmethod
    def check_events(cls, events: set):
        events = set(events)
        if events != set(IahrConfig.PREFIXES.values()):
            raise cls(events)


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
        self.handlers = {
            prefix: {}
            for prefix in IahrConfig.REVERSE_PREFIXES.keys()
        }
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
        command_dct = self.get_state(self.commands)
        handler_dct = {
            prefix: self.get_state(handlers)
            for prefix, handlers in self.handlers.items()
        }
        dct = {
            'commands': command_dct,
            'handlers': handler_dct,
            'chatlist': self.chatlist
        }

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

                PrefixMismatchError.check_events(handlers.keys())

                return commands, handlers
        else:
            return {}, {
                prefix: {}
                for prefix in IahrConfig.REVERSE_PREFIXES.keys()
            }

    def init_routine(self, etype, name, fun, about):
        """
            Check if routine that is being added is not in state,
            if it is, set her state appropriately
        """
        if etype is events.NewMessage:
            state = self.commands_state
            allow_selfact = False
        else:
            prefix = IahrConfig.PREFIXES[etype]
            state = self.handlers_state[prefix]
            allow_selfact = True
        routine = Routine(fun, about, allow_selfact=allow_selfact)
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
            prefix = IahrConfig.PREFIXES[etype]
            self.handlers[prefix][name] = routine

    def add_tags(self, etype, tags, name, routine):
        if etype is not events.NewMessage:
            name = IahrConfig.PREFIXES[etype] + name
        for tag in tags:
            if tag in self.tags:
                self.tags[tag][name] = routine
            else:
                self.tags[tag] = {name: routine}

    ##################################################
    # Chat spam tactic management
    ##################################################

    def is_ignored_chat(self, chat: str):
        return self.chatlist.is_allowed(chat)

    def verbose_chat(self, chat: str):
        return self.chatlist.allow(chat)

    def ignore_chat(self, chat: str):
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

    def add(self, name: str, handler: Callable, about: str, etype: type,
            tags: set):
        IahrConfig.LOGGER.info(f'adding handler:name={name}:etype={etype}')

        name = self.full_name(etype, name)
        routine = self.init_routine(etype, name, handler, about)

        self.add_routine(etype, name, routine)
        self.add_tags(etype, tags, name, routine)

    async def exec(self, event, qstr=None):
        action = await ActionData.from_event(event)
        is_ignored = not self.is_ignored_chat(action.chatid)
    
        if qstr is not None:
            return await self.exec_new_msg(event, qstr, action, is_ignored)
        else:
            return await self.exec_others(event, action, is_ignored)

    async def exec_new_msg(self, event, qstr, action: ActionData, is_ignored):
        IahrConfig.LOGGER.info(f'executing query:qstr={qstr}')

        runner = Executer(qstr, self.commands, action, is_ignored)
        return await runner.run()

    async def exec_others(self, event, action: ActionData, is_ignored):
        etype = type(event)._event_name.split('.')[0]
        IahrConfig.LOGGER.info(f'executing handler:etype={etype}')

        prefix = IahrConfig.PREFIXES[getattr(events, etype)]
        handlers = self.handlers[prefix]

        for handler, routine in handlers.items():
            handler = routine.get_handler(action.uid, action.chatid)
            if handler is None:
                continue

            sender = await handler(event)
            await sender.send()
