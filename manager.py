from telethon import events

from utils import SingletonMeta, AccessList

import re
from enum import Enum
from typing import Iterable, Union, Callable
from dataclasses import dataclass

COMMAND_DELIMITER = '.'
COMMAND_DELIMITER_ESCAPED = r'\.'


class ExecutionError(RuntimeError):
    """
        Raise when next sender doesn't accept args from previous one
        or when wrong arguments were passed to the command
        or when a command function is buggy
    """
    pass

class CommandSyntaxError(ExecutionError):
    """ 
        Plug exception to tell that some input is faulty 
    """
    def __init__(self):
        super().__init__("Wrong syntax, see **.synhelp**")

class PermissionsError(ExecutionError):
    """
        Exception telling that this user or this chat can't use particular command
    """
    def __init__(self, command):
        super().__init__("You can't use **{}** command".format(command))

class NonExistantCommandError(ExecutionError):
    """
        Exception telling that this command is not registered yet
    """
    def __init__(self, command):
        super().__init__("**{}** command does not exist".format(command))


class Query:
    """ 
        Class-representation of our command string in python code
    """
    # argument delimiters
    LEFT_DELIMITER = '['
    RIGHT_DELIMITER = ']'
    # escaped ones(if it is special to re syntax)
    ELEFT_DELIMITER = r'\['
    ERIGHT_DELIMITER = r'\]'

    # matches all [some text] including [some \[text\]] 
    DELIMITER_RE = re.compile(
        r'{0}([^{1}{0}\{1}*(?:\\.[^{1}{0}\{1}*)*)]'.format(
            ELEFT_DELIMITER, ERIGHT_DELIMITER
        ))
    
    def __init__(self, command: str, args):
        self.command = command
        self.args = args # Could be: List[str], Query, None
    
    def is_subquery(self):
        """ 
            If it's args are just another query
        """
        return type(self.args) == type(self)

    def is_noargs(self):
        """
            If it takes no args(except an event)
        """
        return self.args is None

    def is_simple_args(self):
        """
            If it takes a list of args
        """
        return type(self.args) == list

    @classmethod
    def from_str(cls, qstr):

        try:
            res = cls.__parse(qstr)
        except ValueError as e:
            raise CommandSyntaxError

        if res is None:
            raise CommandSyntaxError
        return res
 
    @classmethod
    def __parse(cls, qstr): 
        qstr = qstr.strip() + ' '
        if qstr.startswith(COMMAND_DELIMITER):
            command = qstr[1:qstr.index(' ')]
            qstr = qstr[qstr.index(' '):].strip()
 
            subcommand = cls.__parse(qstr)
            if subcommand is None and qstr:
                is_single_word_args = not qstr.startswith(cls.LEFT_DELIMITER) or \
                                      not qstr.endswith(cls.RIGHT_DELIMITER)
                args = qstr.split() if is_single_word_args else re.findall(cls.DELIMITER_RE, qstr)
            else:
                args = subcommand
            
            return cls(command, args)


class Routine:
    """
        Class that contains raw command handler and manages permissions to use it
        in chats and by users
    """
    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        self.usraccess = AccessList(is_allow_others=False)
        self.chataccess = AccessList(is_allow_others=True)       
 
    def help(self):
        return self.about
    
    def allow_usr(self, usr: str):
        self.usraccess.allow(usr)
    def ban_usr(self, usr: str):
        self.usraccess.ban(usr)
    def is_allowed_usr(self, usr: str):
        return self.usraccess.is_allowed(usr)

    def allow_chat(self, chat: str):
        self.chataccess.allow(chat)
    def ban_chat(self, chat: str):
        self.chataccess.ban(chat)
    def is_allowed_chat(self, chat: str):
        return self.chataccess.is_allowed(chat)

    def get_handler(self, usr: str, chat: str):
        """
            Try to get handler if allowed
        """
        if not self.is_allowed_usr(usr) or not self.is_allowed_chat(chat):
            return
        if usr is None or chat is None:
            return
        return self.handler

@dataclass
class ActionData:
    """
        Contains event and shortcut info about it's author
        
        TODO:
            may be eliminated, easying client code, by getting 
            uid and chatid automatically from event, but i'm not
            sure it is possible on every type of event
    """
    event: events.common.EventCommon
    uid: int
    chatid: int


class Executer:
    """ 
        Glues together
        1. Query(by getting command name and it's args)
        2. Routine(got by command name)

        And thus pipes all needed handlers directly 
        and checks if commands are compatible
    """
    def __init__(self, qstr, commands, action: ActionData):
        self.query = Query.from_str(qstr)
        self.dict = commands
        self.action = action

    async def run(self):
        return await Executer.__run(
            self.query, self.dict, self.action
        )

    @classmethod
    async def __run(cls, query, dct, action):
        try:
            handler = dct[query.command].get_handler(action.uid, action.chatid)        
        except KeyError:
            raise NonExistantCommandError(query.command)

        if handler is None:
            raise PermissionsError(query.command)

        try:
            if query.is_noargs():
                return await handler(action.event)
            elif query.is_subquery():
                subquery = query.args
                sender = await cls.__run(subquery, dct, action)
                return await handler(action.event, *sender.res.args)
            else:
                return await handler(action.event, *query.args)
        except (AttributeError, ValueError, TypeError) as e:
            raise ExecutionError(*e.args)


class Manager(metaclass=SingletonMeta):
    """
        Contains { command_name : routine } key-value pair
        manages addition of new commands and starting it's
        execution by Executer
    """
    def __init__(self):
        self.commands = {}
    
    def add(self, command: str, handler: Callable, about: str):
        command = command.strip(' ' + COMMAND_DELIMITER).split(COMMAND_DELIMITER)
        if len(command) != 1:
            raise CommandSyntaxError("Commands shouldn't contain dots inside")
        self.commands[command[0]] = Routine(handler, about)

    async def exec(self, qstr, action: ActionData):
        """
            Execute query where qstr is raw command text
            and action is info about event and it's authors
        """
        runner = Executer(qstr, self.commands, action)
        return await runner.run()

app = Manager()

