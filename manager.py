from telethon import events

from utils import SingletonMeta, AccessList, Tokenizer

import re
from enum import Enum
from typing import Iterable, Union, Callable
from dataclasses import dataclass
from  abc import ABC, abstractmethod


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

    @classmethod
    def unescape(cls, s):
        l, el = cls.LEFT_DELIMITER, cls.ELEFT_DELIMITER
        r, er = cls.RIGHT_DELIMITER, cls.ERIGHT_DELIMITER
        d, ed = COMMAND_DELIMITER, COMMAND_DELIMITER_ESCAPED
        return s.replace(el, l).replace(er, r).replace(ed, d)

    def full_command(self):
        return COMMAND_DELIMITER + self.command
    
    def __init__(self, command: str, args):
        self.command = command
        self.args = args # Could be: List[str | Query]
    
    @classmethod
    def from_str(cls, qstr):
        qstr = cls.LEFT_DELIMITER + qstr + cls.RIGHT_DELIMITER
        try:
            tree = Tokenizer.from_str(qstr, cls.LEFT_DELIMITER, cls.RIGHT_DELIMITER)
        except Tokenizer.ParseError as e:
            raise CommandSyntaxError
        print(tree) 
        return cls.__to_q(tree)

    @classmethod
    def __single_word_helper(cls, args, subargs):
        if not args: return subargs
        elif len(args) == 1: return [cls.__to_q((args[0], subargs))]
        
        res = []
        for i, arg in enumerate(args):
            if arg.startswith(COMMAND_DELIMITER):
                cmd, itsargs = arg[1:], args[i + 1:]
                res.append(cls(cmd, cls.__single_word_helper(itsargs, subargs)))
                break
            else:
                res.append(arg) 

        return res

    @classmethod
    def __to_q(cls, tree):
        command, args = tree
        if command.startswith(COMMAND_DELIMITER):
            args = [cls.__to_q(arg) if type(arg) == tuple else arg for arg in args]
            command, *subcomms = command.split()
            args = cls.__single_word_helper(subcomms, args)
            return cls(command[1:], args)
        else:
            return command


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
            handler = dct[query.full_command()].get_handler(action.uid, action.chatid)        
        except KeyError:
            raise NonExistantCommandError(query.command)

        if handler is None:
            raise PermissionsError(query.command)

        try:
            args = []
            for arg in query.args:
                if type(arg) == Query:
                    call = await cls.__run(arg, dct, action)
                    args.extend(call.res.args)
                else:
                    args.append(arg)
            return await handler(action.event, *args)
        except (AttributeError, ValueError, TypeError) as e:
            raise ExecutionError(*e.args)


class Manager(metaclass=SingletonMeta):
    """
        Contains { command_name : routine } key-value pair
        manages addition of new commands and starting it's
        execution by Executer. Only for text-based commands!
    """
    def __init__(self):
        self.commands = {}
    
    def add(self, command: str, handler: Callable, about: str, delimiter=COMMAND_DELIMITER):
        command = command.strip(' ' + delimiter).split(delimiter)
        if len(command) != 1:
            raise CommandSyntaxError("Commands shouldn't contain '{}' inside".format(delimiter))
        self.commands[delimiter + command[0]] = Routine(handler, about)

    async def exec(self, qstr, action: ActionData):
        """
            Execute query where qstr is raw command text
            and action is info about event and it's authors
        """
        runner = Executer(qstr, self.commands, action)
        return await runner.run()

app = Manager()

