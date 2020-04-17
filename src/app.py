from telethon import events

from utils import SingletonMeta, AccessList
from senders import ABCSender, IncompatibleSendersError

import re
from enum import Enum
from typing import Iterable, Union, Callable


class CommandSyntaxError(Exception):
    """ 
        Plug exception to tell that some input is faulty 
    """
    pass



class Query:
    """ 
        Class-representation of our command string in python code
    """

    LEFT_DELIMITER = '['
    RIGHT_DELIMITER = ']'
    # matches all [some text] including [some \[text\]] 
    DELIMITER_RE = re.compile(r'\[([^\]\[\\]*(?:\\.[^\]\[\\]*)*)]')
    
    def __init__(self, command: str, args):
        self.command = command
        self.args = args # Could be: List[str], Query, None
    
    def is_subquery(self):
        return type(self.args) == type(self)

    def is_noargs(self):
        return self.args is None

    def is_simple_args(self):
        return type(self.args) == list

    @classmethod
    def from_str(cls, qstr):
        try:
            res = cls.__parse(qstr)
        except ValueError as e:
            raise CommandSyntaxError(*e.args)

        if res is None:
            raise CommandSyntaxError()
        return res
 
    @classmethod
    def __parse(cls, qstr): 
        qstr = qstr.strip() + ' '
        if qstr.startswith('.'):
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
        if not is_allowed_usr(usr) or not is_allowed_chat(chat):
            return
        if usr is None or chat is None:
            return
        
        return self.handler

@dataclass
class ActionData:
    event: event.common.EventCommon
    uid: int
    chatid: int


class Executer:
    def __init__(self, qstr, commands, action: ActionData):
        self.query = Query.from_str(qstr)
        self.dict = commands
        self.action = action

    async def run(self) -> ABCSender:
        return await Executer.__run(
            self.query, self.dict, self.action
        )

    @classmethod
    async def __run(cls, query, dct, action) -> ABCSender:
        handler = dct[query.command].get_handler(action.uid, action.chatid)        

        if query.is_noargs():
            return await handler(action.event)
        elif query.is_subquery():
            subquery = query.args
            sender = await cls.__run(subquery, dct, action)
            if type(handler) != type(sender):
                raise IncompatibleSendersError             
            return await handler(action.event, *sender.res.args)
        else:
            return await handler(action.event, *query.args)


class Manager(metaclass=SingletonMeta):
   def __init__(self):
        self.commands = {}
    
    def add(self, command: str, handler: Callable, about: str):
        command = command.strip(' .').split('.')
        if len(command) != 1:
            raise CommandSyntaxError("Commands shouldn't contain dots inside")
        
        self.commands[command[0]] = Routine(handler, about)
    
    async def exec(self, qstr, action: ActionData):
        runner = Executer(qstr, self.commands, action)
        return await runner.run()

app = Manager()
    
