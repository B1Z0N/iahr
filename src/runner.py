from utils import AccessList, Tokenizer, Delimiter, ActionData

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

    @classmethod
    def unescape(cls, s):
        s = cls.LEFT_DELIMITER.unescape(s)
        s = cls.RIGHT_DELIMITER.unescape(s)
        s = cls.COMMAND_DELIMITER.unescape(s)
        return s

    ##################################################
    # All about parsing
    ##################################################
    
    def __init__(self, command: str, args):
        self.command = command
        self.args = args # Could be: List[str | Query]
    
    @classmethod
    def from_str(cls, qstr):
        qstr = cls.LEFT_DELIMITER.original + qstr + cls.RIGHT_DELIMITER.original
        try:
            tree = Tokenizer.from_str(qstr, cls.LEFT_DELIMITER, cls.RIGHT_DELIMITER)
        except Tokenizer.ParseError as e:
            raise CommandSyntaxError
        
        return cls.__to_q(tree)

    @classmethod
    def __single_word_helper(cls, args, subargs):
        if not args: return subargs
        elif len(args) == 1: return [cls.__to_q((args[0], subargs))]
        
        res = []
        for i, arg in enumerate(args):
            if cls.COMMAND_DELIMITER.is_command(arg):
                cmd, itsargs = arg[1:], args[i + 1:]
                res.append(cls(cmd, cls.__single_word_helper(itsargs, subargs)))
                break
            else:
                res.append(arg) 

        return res

    @classmethod
    def __to_q(cls, tree):
        command, args = tree
        if cls.COMMAND_DELIMITER.is_command(command):
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

    @classmethod
    async def __run(cls, query, dct, action):
        try:
            handler = \
                dct[query.COMMAND_DELIMITER.full_command(query.command)]\
                    .get_handler(action.uid, action.chatid)        
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


