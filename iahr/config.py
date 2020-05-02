from telethon import events

from .utils import Delimiter, CommandDelimiter, parenthesify, Delayed, SingletonMeta

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


class IahrConfig(metaclass=SingletonMeta):
    LEFT, RIGHT, RAW = Delimiter('['), Delimiter(']'), Delimiter('r')
    NEW_MSG, NON_NEW_MSG = CommandDelimiter('.'), CommandDelimiter('!')
    
    PREFIX = Delimiter('_')
    PREFIXES = {
        events.MessageEdited : 'onedit',
        events.MessageDeleted : 'ondel',
        events.MessageRead : 'onread',
        events.ChatAction : 'onchataction' ,
        events.UserUpdate : 'onusrupdate',
        events.Album : 'onalbum',     
    }
    
    ME, OTHERS = 'me', '*'
    
    LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s:'
    LOG_DATETIME_FORMAT, LOG_OUT = '%m/%d/%Y %I:%M:%S %p', sys.stdout

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

    ##################################################
    # Config methods
    ##################################################

    @classmethod
    def init_config(cls, app, reg):
        IahrConfig.APP = app
        IahrConfig.REG.init(reg.reg)
    

def __update(preprocess, **kwargs):
    for name, val in kwargs.items():
        if val is not None:
            setattr(IahrConfig, name.upper(), preprocess(val))
            

def config(left=None, right=None, raw=None, new_msg=None, 
            non_new_msg=None, prefix=None, prefixes=None, 
            me=None, others=None, log_format=None, 
            log_datetime_format=None, log_out=None,
            session_fname=None):
    __update(Delimiter, left=left, right=right, raw=raw, prefix=prefix)
    __update(CommandDelimiter, new_msg=new_msg, non_new_msg=non_new_msg)
    __update(
        lambda x: x, prefixes=prefixes, me=me,
        others=others, log_format=log_format,
        log_datetime_format=log_datetime_format,
        log_out=log_out, session_fname=session_fname
    )
     
    if new_msg:
        IahrConfig.COMMAND_RE = re.compile(
            r'{}[^\W]+.*'.format(IahrConfig.NEW_MSG.in_re())
        )
    if left or right or new_msg or raw:
        IahrConfig.ADD_PARS = parenthesify(
            IahrConfig.LEFT, IahrConfig.RIGHT, IahrConfig.NEW_MSG, IahrConfig.RAW
        )
    if log_format or log_datetime_format or log_out:
        IahrConfig.LOGGER = create_logger(
            IahrConfig.LOG_FORMAT, IahrConfig.LOG_DATETIME_FORMAT, IahrConfig.LOG_OUT
        )
 
