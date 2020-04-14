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
    
    def is_subquery():
        return type(self.args) == type(self)

    def is_noargs():
        return self.args is None

    def is_simple_args():
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


def test_query(qstr):
    q = Query.from_str(qstr)
    def print_query(q):
        print("Command:", q.command)
        if type(q.args) == type([]):
            print("Args:", q.args)
        elif q.args is None:
            pass
        else: 
            print_query(q.args)
        
    print_query(q)

test_query(input())


class Routine:
    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        self.allow_me = True
        self.allow_others = False
    
    def help(self):
        return self.about
    
    def toggle_allow_others():
        self.allow_others = not self.allow_others

    def toggle_allow_me():
        self.allow_me = not self.allow_me
    
    def get_handler(self, subprop=None):
        if subprop is None:
            return self.handler
        else:
            return getattr(self.handler, subprop, None)


class Executer:
    def __init__(self, qstr, commands):
        self.query = Query.from_str(qstr)
        self.dict = commands

    def run():
        return __run(self.query, self.dict)

    @staticmethod
    def __run(query, dct):
        cmds = query.command.split('.')
        handler = self.dct[cmds[0]].get_handler(cmds[1] if len(cmds) > 1 else None)
        
        if query.is_noargs():
            return handler()
        elif query.is_subquery():
            res =  __run(query.args)
            return handler(res)
        else:
            return handler(*self.args)
        
    
class Manager(metaclass=SingletonMeta):
    commands = {}
    
    def add(command: str, handler: Callable, about: str):
        command = command.strip().split('.')
        if len(command) != 1:
            raise SyntaxException("Commands shouldn't contain dots inside")
        
        commands[command[0]] = Routine(handler, about)
   
    def exec(command: str):
        runner = Executer(command, self.commands)
        return runner.run()

app = Manager()

