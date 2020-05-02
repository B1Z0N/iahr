from telethon import events

from .utils import Delimiter, CommandDelimiter, parenthesify, Delayed

import re, logging, sys

def create_logger(fmt, datefmt, out):
    if out in (sys.stdout, sys.stderr):
        handler_cls = logging.StreamHandler
    else:
        handler_cls = logging.FileHandler

    logger = logging.getLogger('iahr')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt, datefmt)
    handler = handler_cls(out)
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
    
    ME = 'me'
    OTHERS ='*'
    
    LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s:'
    LOG_DATETIME_FORMAT = '%m/%d/%Y %I:%M:%S %p'
    LOG_OUT = sys.stdout

    SESSION_FNAME = 'iahr.session'
  
    # to be settled, but needed here
    # for use in command execution time
    APP = None
    # to be settled, but needed
    # for use in import time
    REG = Delayed()

    ##################################################
    # Config based on config data above
    ##################################################

    COMMAND_RE = re.compile(r'{}[^\W]+.*'.format(NEW_MSG.in_re()))
    ADD_PARS = parenthesify(LEFT, RIGHT, NEW_MSG, RAW)
    LOGGER = create_logger(LOG_FORMAT, LOG_DATETIME_FORMAT, LOG_OUT)


def init_config(app, reg):
    IahrConfig.APP = app
    IahrConfig.REG.init(reg.reg)

