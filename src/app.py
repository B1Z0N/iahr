import re

from utils import SingletonMeta
from typing import Iterable, Union, Callable


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


class Routine:
    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        self.rights = {'me'}
 
    def help(self):
        return self.about
    
    def toggle_allow(self, usr: str):
        if usr not in self.rights:
            self.rights.add(usr)
        else:
            self.rights.remove(usr)

    def is_allowed(self, usr: str):
        return usr in self.rights
    
    def get_handler(self, subprop=None):
        if subprop is None:
            return self.handler
        else:
            return getattr(self.handler, subprop, None)


class Executer:
    def __init__(self, qstr, commands):
        self.query = Query.from_str(qstr)
        self.dict = commands

    def run(self):
        return Executer.__run(self.query, self.dict)

    @classmethod
    def __run(cls, query, dct):
        cmds = query.command.split('.')
        handler = dct[cmds[0]].get_handler(cmds[1] if len(cmds) > 1 else None)
        
        if query.is_noargs():
            return handler()
        elif query.is_subquery():
            res = cls.__run(query.args, dct)
            return handler(res)
        else:
            return handler(*query.args)


class Manager(metaclass=SingletonMeta):

    def __help(self, cmd=None):
        if cmd is not None:
            return cmd + ': ' + self.commands[cmd].help()

        helplst = [cmd + ': ' + routine.help() for cmd, routine in self.commands.items()]
        return '\n'.join(helplst)

    def __allow(self, cmd: str, usr: str):
        self.commands[cmd].toggle_allow(usr)

    def __init__(self):
        self.commands = {
            'help' : Routine(self.__help, 
                        'Get help on command or full help'),
            'allow' : Routine(self.__allow, 
                        'Toggle execution rights of a command for "me", "others" or "UNAME"'),
        }
    
    def add(self, command: str, handler: Callable, about: str):
        command = command.strip(' .').split('.')
        if len(command) != 1:
            raise SyntaxError("Commands shouldn't contain dots inside")
        
        self.commands[command[0]] = Routine(handler, about)
    
    def exec(self, command: str):
        runner = Executer(command, self.commands)
        return runner.run()

app = Manager()
app1 = Manager()

assert(app == app1)
assert(app.commands == app1.commands)
