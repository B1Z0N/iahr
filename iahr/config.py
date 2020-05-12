from telethon import events

from .utils import Delimiter, CommandDelimiter
from .utils import parenthesize, Delayed, SingletonMeta

import re, sys, logging


class IahrConfig(metaclass=SingletonMeta):
    """
        Single source of truth about configuration.
        This way all modules can access fresh info 
        at import time. 
        
        Needs to be initialized with `init` call.
        It is only for internal use, to update values
        from userspace use `config` function below. 
    """

    APP = None  # to be settled, but needed here for use in command execution time
    REG = Delayed()  # to be settled, but needed for use in import time

    ##################################################
    # Config methods
    ##################################################

    @classmethod
    def init(cls, app, reg):
        """ 
            Should be called with initial setup args.
            The core call to start a framework.
        """
        IahrConfig.APP = app
        IahrConfig.REG.init(reg.reg)

    @classmethod
    def _update(cls, preprocess, **kwargs):
        """
            Helper function to update the member if it's
            lowercase kwarg conterpart is not None.
        """
        for name, val in kwargs.items():
            if val is not None:
                setattr(cls, name.upper(), preprocess(val))


##################################################
# Functions for updating dependent config data
##################################################


def update_command_re(cmd: Delimiter):
    return re.compile(r'{}[^\W]+.*'.format(cmd.in_re()))


def update_add_pars(left, right, cmd, raw):
    return parenthesize(left, right, cmd, raw)


def update_logger(fmt, datefmt, out):
    if out in (sys.stdout, sys.stderr):
        handler_cls = logging.StreamHandler
    elif type(out) == str:
        handler_cls = logging.FileHandler
    else:
        raise RuntimeError(
            "out should be one of this: sys.stdout, sys.stdin, `filename`")
    logger = logging.getLogger('iahr')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt, datefmt)
    handler = handler_cls(out)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


##################################################
# Interface(not literally) for changing IahrConfig
##################################################


def config(left=None,
           right=None,
           raw=None,
           cmd=None,
           prefixes=None,
           me=None,
           others=None,
           log_format=None,
           log_datetime_format=None,
           log_out=None,
           session_fname=None):
    """
        Single entry to framework configuration, 
        just run this with some of updated values and 
        it will update IahrConfig accordingly.
    """

    cfg = IahrConfig

    cfg._update(Delimiter, left=left, right=right, raw=raw)
    cfg._update(CommandDelimiter, cmd=cmd)
    cfg._update(lambda x: x,
                prefixes=prefixes,
                me=me,
                others=others,
                log_format=log_format,
                log_datetime_format=log_datetime_format,
                log_out=log_out,
                session_fname=session_fname)

    cfg.COMMAND_RE = update_command_re(cfg.CMD)
    cfg.ADD_PARS = update_add_pars(cfg.LEFT, cfg.RIGHT, cfg.CMD, cfg.RAW)
    cfg.LOGGER = update_logger(cfg.LOG_FORMAT, cfg.LOG_DATETIME_FORMAT,
                               cfg.LOG_OUT)


def reset():
    """ 
        Reset(set) IahrConfig to default value
        Single source of truth about default
    """
    config(
        left='[',
        right=']',
        raw='r',
        cmd='.',
        prefixes={
            events.NewMessage:
            'onnewmsg_',  # additional handlers(not commands)
            events.MessageEdited: 'onedit_',
            events.MessageDeleted: 'ondel_',
            events.MessageRead: 'onread_',
            events.ChatAction: 'onchataction_',
            events.UserUpdate: 'onusrupdate_',
            events.Album: 'onalbum_',
        },
        me='me',
        others='*',
        log_format=
        '%(asctime)s:%(name)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s:',
        log_datetime_format='%m/%d/%Y %I:%M:%S %p',
        log_out=sys.stdout,
        session_fname='iahr.session')


reset()
