from telethon import events

from .utils import Delimiter, CommandDelimiter, parenthesify

import re, logging, sys

def create_logger(fmt, datefmt, out=None, is_file=False):
    out = sys.stdout if out is None else out

    logger = logging.getLogger('iahr')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt, datefmt)
    if is_file:
        handler = logging.FileHandler(out)
    else:
        handler = logging.StreamHandler(out)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
 

class IahrConfig:
    LEFT = Delimiter('[')
    RIGHT = Delimiter(']')
    RAW = Delimiter('r')
    NEW_MSG = CommandDelimiter('.')
    NON_NEW_MSG = CommandDelimiter('!')
    PREFIX = Delimiter('_')
    PREFIXES = {
        events.MessageEdited : 'onedit',
        events.MessageDeleted : 'ondel',
        events.MessageRead : 'onread',
        events.ChatAction : 'onchataction' ,
        events.UserUpdate : 'onusrupdate',
        events.Album : 'onalbum',     
    }
    
    COMMAND_RE = re.compile(r'{}[^\W]+.*'.format(NEW_MSG.in_re()))
    
    ME = 'me'
    OTHERS ='*'

    ADD_PARS = parenthesify(LEFT, RIGHT, NEW_MSG, RAW)

    LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s:'
    LOG_DATETIME_FORMAT = '%m/%d/%Y %I:%M:%S %p'
    LOGGER = create_logger(LOG_FORMAT, LOG_DATETIME_FORMAT)

