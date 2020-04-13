import re

from typing import Iterable, Union


class Query:
    # should be different
    LEFT_DELIMITER = '['
    RIGHT_DELIMITER = ']'
    # matches all [some text] including [some \[text\]] 
    DELIMITER_RE = re.compile(r'\[([^\]\[\\]*(?:\\.[^\]\[\\]*)*)]')
    
    class SyntaxError(Exception):
        """ 
            Plug exception to tell that some input is faulty 
        """
        pass

    def __init__(self, command: str, args):
        self.command = command
        self.args = args # Could be: List[str], Query, None
    
    @classmethod
    def from_str(cls, qstr):
        try:
            res = cls.__parse(qstr, final)
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
                is_single_arg = not qstr.startswith(cls.LEFT_DELIMITER) or \
                                not qstr.endswith(cls.RIGHT_DELIMITER)
                args = [qstr] if is_single_arg else re.findall(cls.DELIMITER_RE, qstr)
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

