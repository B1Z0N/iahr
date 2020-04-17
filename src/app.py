import re

from utils import SingletonMeta
from typing import Iterable, Union, Callable
from enum import Enum
from telethon import events

class SyntaxError(Exception):
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
            raise SyntaxError(*e.args)

        if res is None:
            raise SyntaxError()
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


class EntityGroup(Enum):
    ME = 1
    OTHERS = 2
    ALL = 3

    @classmethod
    def from_str(cls, s):
        return getattr(cls, s, None)


class Routine:
    @staticmethod
    def __allow(whitelist, blacklist, ent):
        pass
    
    @staticmethod
    def __ban(whitelist, blacklist, ent):
        pass
    
    @staticmethod
    def __is_allowed(whitelist, blacklist, ent):
        pass

    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        
        self.usrwhitelist = {EntityGroup.ME} 
        # blacklist is much more powerful than whitelist
        self.usrblacklist = set()
        
        self.chatwhitelist = {EntityGroup.ALL}
        self.chatblacklist = set()

    def help(self):
        return self.about
    
    def allow_usr(self, usr: str):
        self.__allow(self.usrwhitelist, self.usrblacklist, usr)

    def ban_usr(self, usr: str):
        self.__ban(self.usrwhitelist, self.usrblacklist, usr)
    
    def is_allowed_usr(self, usr: str):
        return self.__is_allowed(self.usrwhitelist, self.usrblacklist, usr)

    def allow_chat(self, chat: str):
        self.__allow(self.chatwhitelist, self.chatblacklist, chat)

    def ban_chat(self, chat: str):
        self.__ban(self.chatwhitelist, self.chatblacklist, chat)
    
    def is_allowed_chat(self, chat: str):
        return self.__is_allowed(self.chatwhitelist, self.chatblacklist, chat)


    def get_handler(self, usr: str, chat: str, subprop=None):
        if not is_allowed_usr(usr) or not is_allowed_chat(chat):
            return
        if usr is None or chat is None:
            return

        if subprop is None:
            return self.handler
        else:
            return getattr(self.handler, subprop, None)


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

    async def run(self):
        return await Executer.__run(
            self.query, self.dict, self.action
        )

    @classmethod
    async def __run(cls, query, dct, action):
        cmds = query.command.split('.')
        routine = dct[cmds[0]]
        subcommand = cmds[1] if len(cmds) > 1 else None
        handler = routine.get_handler(action.uid, action.chatid, subcommand)
        event = action.event

        if query.is_noargs():
            return await handler(event)
        elif query.is_subquery():
            res = await cls.__run(query.args, dct, event).res
            return await handler(event, res)
        else:
            return await handler(event, *query.args)


class Manager(metaclass=SingletonMeta):
   def __init__(self):
        self.commands = {}
    
    def add(self, command: str, handler: Callable, about: str):
        command = command.strip(' .').split('.')
        if len(command) != 1:
            raise SyntaxError("Commands shouldn't contain dots inside")
        
        self.commands[command[0]] = Routine(handler, about)
    
    async def exec(self, qstr, action: ActionData):
        runner = Executer(qstr, self.commands, action)
        return await runner.run()

app = Manager()
    
