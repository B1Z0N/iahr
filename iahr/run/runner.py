from ..utils import AccessList, ActionData, Delimiter
from ..utils import Tokenizer, parenthesify, ParseError

from telethon import events

import re
from dataclasses import dataclass
from typing import Callable


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
    def __init__(self, e):
        super().__init__("Wrong syntax, see **.synhelp**:({})".format(str(e)))


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


class CommandDelimiter(Delimiter):
    def full_command(self, cmd):
        return self.original + cmd
        
    def is_command(self, s):
        return s.startswith(self.original)

class Query:
    """ 
        Class-representation of our command string in python code
    """

    ##################################################
    # All about delimiters
    ##################################################
    
    # argument delimiters
    LEFT_DELIMITER = Delimiter(r'[')
    RIGHT_DELIMITER = Delimiter(r']')
    COMMAND_DELIMITER = CommandDelimiter(r'.')
    RAW_DELIMITER = Delimiter(r'r')    

    add_pars = parenthesify(LEFT_DELIMITER, RIGHT_DELIMITER, COMMAND_DELIMITER, RAW_DELIMITER)

    KWARGS_RE = re.compile(r'(?<!\\)=')

    @classmethod
    def unescape(cls, s):
        s = cls.LEFT_DELIMITER.unescape(s)
        s = cls.RIGHT_DELIMITER.unescape(s)
        s = cls.COMMAND_DELIMITER.unescape(s)
        return s

    ##################################################
    # All about parsing
    ##################################################
    
    def __init__(self, command: str, args, kwargs):
        self.command = command
        self.args = list(args) # Could be: List[str | Query]
        self.kwargs = dict(kwargs) # Could be: Dict[str: [str | Query]]
    
    @classmethod
    def from_str(cls, qstr):
        qstr = cls.LEFT_DELIMITER.original + qstr + cls.RIGHT_DELIMITER.original
        try:
            qstr = cls.add_pars(qstr)     
            tree = Tokenizer.from_str(qstr, cls.LEFT_DELIMITER, cls.RIGHT_DELIMITER)
        except ParseError as e:
            raise CommandSyntaxError(str(e))
        print(tree) 
        return cls.__to_q(tree)

    @classmethod
    def __process_args(cls, rawargs):
        if not rawargs: return [], {}
        args, kwargs = [], {}
        def divide(arg): 
            if type(arg) == cls:
                args.append(arg)
            elif len(arg) == 2:
                kwargs[arg[0]] = arg[1] 
            else:
                args.append(arg[0])

        rawargs = map(cls.__to_q, rawargs) 
        [divide(arg) for arg in rawargs]
        return args, kwargs

    @classmethod
    def __to_q(cls, tree):
        command, args = tree
        args, kwargs = cls.__process_args(args) 

        if cls.COMMAND_DELIMITER.is_command(command):
            return cls(command[1:], args, kwargs)
        else:
            return (*re.split(cls.KWARGS_RE, command, 1), ) 


class Routine:
    """
        Class that contains raw command handler and manages permissions to use it
        in chats and by users
    """
    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        self.usraccess = AccessList(allow_others=False)
        self.chataccess = AccessList(allow_others=True)       
 
    def help(self):
        return self.about
 
    ##################################################
    # Rights to run this handler
    ##################################################
    
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
        if usr is None or chat is None:
            return
        if not self.is_allowed_usr(usr) or not self.is_allowed_chat(chat):
            return

        return self.handler


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

    
    async def __process_args(rawargs, rawkwargs, subprocess: Callable):
        if not rawargs and not rawkwargs: return [], {}
        print(rawargs, rawkwargs)
        args, kwargs = [], {}
        for arg in rawargs:
            if type(arg) == Query:
                call = await subprocess(arg)
                args.extend(call.res.args)
            else:
                args.append(arg)

        for key, val in rawkwargs.items():
            if type(val) == Query:
                call = await subprocess(val)
                kwargs[key] = call.res.args[0]
            else:
                kwargs[key] = val

        return args, kwargs

    @classmethod
    async def __run(cls, query, dct, action):
        async def proc(subquery):
            return await cls.__run(subquery, dct, action)
        
        try:
            handler = \
                dct[query.COMMAND_DELIMITER.full_command(query.command)]\
                    .get_handler(action.uid, action.chatid)        
        except KeyError:
            raise NonExistantCommandError(query.command)
        if handler is None: 
            raise PermissionsError(query.command)
        
        try:
            args, kwargs = await cls.__process_args(query.args, query.kwargs, proc) 
            return await handler(action.event, *args, **kwargs)
        except (AttributeError, ValueError, TypeError) as e:
            raise ExecutionError(*e.args)


