import re

from typing import Iterable, Union


class Query:
    # should be different
    LEFT_DELIMITER = '['
    RIGHT_DELIMITER = ']'
    # matches all [some text] including [some \[text\]] 
    DELIMITER_RE = re.compile(r'\[([^\]\[\\]*(?:\\.[^\]\[\\]*)*)]')
    

    def __init__(command: str, args: Union[Iterable[str], Query]]):
        self.command = command
        self.args = args    
    
    @classmethod
    def parse(cls, qstr, final=False) -> Union[Query, None]: 
        qstr = qstr.strip()
        if qstr.startswith('.'):
            command = qstr[1:qstr.index(' ')]
            qstr = qstr[qstr.index('_'):].strip()
 
            subcommand = cls.parse(qstr)
            if subcommand is None:
                is_single_arg = not qstr.startswith(self.LEFT_DELIMITER) or \
                                not qstr.endswith(self.RIGHT_DELIMITER)
                args = [qstr] if is_single_arg else re.findall(DELIMITER_RE, qstr)
            else:
                args = subcommand
            
            return cls(command, args)

