import re

from utils import SingletonMeta
from typing import Iterable, Union, Callable
from enum import Enum

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


class UsrGroup(Enum):
    ME = 1
    OTHERS = 2
    ALL = 3    

    
class ChatGroup(UsrGroups):
    pass


class Routine:
    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        
        self.usrwhitelist = {UsrGroup.ME} 
        # blacklist is much more powerful than whitelist
        self.usrblacklist = set()
        
        self.chatwhitelist = {ChatGroup.ALL}
        self.chatblacklist = set()

    def help(self):
        return self.about
    
    def allow_usr(self, usr: str):
        self.usrwhitelist.add(usr)
        if usr in self.usrblacklist:
            self.usrblacklist.remove(usr)

    def ban_usr(self, usr: str):
        self.usrblacklist.add(usr)
        if usr in self.usrwhitelist:
            self.usrwhitelist.remove(usr)
    
    def is_allowed_usr(self, usr: str):
        return usr in self.usrwhitelist and usr not in self.usrblacklist

    def allow_chat(self, chat: str):
        self.chatwhitelist.add(chat)
        if chat in self.chatblacklist:
            self.chatblacklist.remove(chat)

    def ban_chat(self, chat: str):
        self.chatblacklist.add(chat)
        if chat in self.chatwhitelist:
            self.chatwhitelist.remove(chat)
    
    def is_allowed_chat(self, chat: str):
        return chat in self.chatwhitelist and chat not in self.chatblacklist

    def get_handler(self, usr: str, chat: str, subprop=None):
        if not is_allowed_usr(usr) or not is_allowed_chat(chat):
            return

        if subprop is None:
            return self.handler
        else:
            return getattr(self.handler, subprop, None)


class Executer:
    def __init__(self, qstr, commands, event):
        self.query = Query.from_str(qstr)
        self.dict = commands
        self.event = event

    async def run(self):
        return await Executer.__run(self.query, self.dict, self.event)

    @classmethod
    async def __run(cls, query, dct, event):
        cmds = query.command.split('.')
        handler = dct[cmds[0]].get_handler(cmds[1] if len(cmds) > 1 else None)
        
        if query.is_noargs():
            return await handler(event)
        elif query.is_subquery():
            res = await cls.__run(query.args, dct, event)
            return await handler(event, res)
        else:
            return await handler(event, *query.args)


class Manager(metaclass=SingletonMeta):

    async def __help(self, cmd=None):
        if cmd is not None:
            return cmd + ': ' + self.commands[cmd].help()

        helplst = [cmd + ': ' + routine.help() for cmd, routine in self.commands.items()]
        return '\n'.join(helplst)

    async def __rights(self, action: str):
        async def _(entity: str, cmd=None):
            if cmd is not None:
                getattr(self.commands[cmd], action)(entity)
            else:
                for routine in self.commands.values():
                    getattr(routine, action)(entity)
        return _

    def __init__(self):
        self.commands = {
            'help': Routine(self.__help, 
            'Get help on command or full help'),
            'allowusr': Routine(self.__rights('allow_usr'), 
            'Allow "me", "others", "all" or "UNAME" to run particular command'),
            'banusr': Routine(self.__rights('ban_usr'), 
            'Ban "me", "others", "all" or "UNAME" from running particular command'),
            'allowchat': Routine(self.__rights('allow_chat'), 
            'Allow chats with "me", "others", "all" or "CHATNAME" to run a command'),
            'banchat': Routine(self.__rights('ban_chat'), 
            'Ban chats with "me", "others", "all" or "CHATNAME" from running a command'),
        }
    
    def add(self, command: str, handler: Callable, about: str):
        command = command.strip(' .').split('.')
        if len(command) != 1:
            raise SyntaxError("Commands shouldn't contain dots inside")
        
        self.commands[command[0]] = Routine(handler, about)
    
    async def exec(self, command: str, event):
        runner = Executer(command, self.commands)
        return await runner.run(event)

app = Manager()
    
