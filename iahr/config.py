from telethon import events

from iahr.utils import Delimiter, CommandDelimiter
from iahr.utils import parenthesize, Delayed, SingletonMeta
from iahr.exception import IahrBaseError
from iahr import localization

import re, logging, json, os
import sys

from dotenv import load_dotenv

# constants
CONFIG_DATA_FOLDER_ENV_NAME = 'IAHR_DATA_FOLDER'
DATA_FOLDER = os.getenv(CONFIG_DATA_FOLDER_ENV_NAME)
if DATA_FOLDER is None:
    DATA_FOLDER = 'data'

CONFIG_FNAME = 'config.json'
SESSION_FNAME = 'iahr.session'
LOG_FNAME = 'iahr.log'

##################################################
# Exceptions
##################################################


class IahrConfigError(IahrBaseError):
    """
        Base exception class for this module
    """
    pass


class EventsError(IahrConfigError):
    """
        Exception to raise when events
        are not ok
    """

    TELETHON_EVENTS_URL = \
        'https://docs.telethon.dev/en/latest/quick-references/events-reference.html'

    TELETHON_EVENTS = {
        'MessageEdited',
    }

    def __init__(self, events: set):
        should_be = self.TELETHON_EVENTS.difference(events)
        should_not_be = events.difference(self.TELETHON_EVENTS)

        msg = '\n\n\tSomething wrong with your event strings:\n'
        msg += f'\tthese should be there: {should_be}\n' if should_be else ''
        msg += f'\tthese should not be there: {should_not_be}\n' if should_not_be else ''
        msg += f'\n\tsee telethon docs: {self.TELETHON_EVENTS_URL}\n'

        super().__init__(msg)

    @classmethod
    def check_events(cls, events: set):
        if events != cls.TELETHON_EVENTS:
            raise cls(events)


class UnknownLocalizationError(IahrConfigError):
    """
        Exception to raise when no such
        language available in iahr.localization module
    """

    IAHR_AVAILABLE_LANGS = [
        var for var in dir(localization) if not var.startswith("__")
    ]
    IAHR_LOCALIZATION_URL = \
        'https://github.com/B1Z0N/iahr/blob/master/README.md#localization'

    def __init__(self, lang: str):
        msg = f"""\n
        Currently, there are no such language in Iahr: `{lang}`,
        but you always can add one yourself: {self.IAHR_LOCALIZATION_URL}.

        These localizations available: {self.IAHR_AVAILABLE_LANGS}
        """
        super().__init__(msg)

    @classmethod
    def lang_from_str(cls, lang: str):
        if lang not in cls.IAHR_AVAILABLE_LANGS:
            raise cls(lang)
        return getattr(localization, lang)


##################################################
# Config class
##################################################


class IahrConfig(metaclass=SingletonMeta):
    """
        Single source of truth about configuration.
        This way all modules can access fresh info 
        at import time. 
        
        Needs to be initialized with `init` call.
        It is only for internal use, to update values
        from userspace use `config` function below. 
    """

    APP = None  # to be settled, but needed here for use in routine execution time
    REG = Delayed()  # Register in import time
    BARE_REG = None  # Register in runtime

    ##################################################
    # Config methods
    ##################################################

    @classmethod
    def init(cls, reg):
        """ 
            Should be called with initial setup args.
            The core call to start a framework.
        """
        cls.APP = reg.app
        cls.REG.init(reg.reg)
        cls.BARE_REG = reg

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
# and utility functions
##################################################


def update_command_re(cmd: Delimiter):
    return re.compile(r'{}[^\W]+.*'.format(cmd.in_re()))


def update_add_pars(left, right, cmd, raw):
    return parenthesize(left, right, cmd, raw)


def update_logger(fmt, datefmt, out, lvl: str = None):
    if out in (sys.stdout, sys.stderr):
        handler_cls = logging.StreamHandler
    elif type(out) == str:
        handler_cls = logging.FileHandler
    else:
        raise RuntimeError(
            "out should be one of this: sys.stdout, sys.stdin, `filename`")

    lvl = getattr(logging, str(lvl), logging.INFO)

    logger = logging.getLogger('iahr')
    logger.setLevel(lvl)
    formatter = logging.Formatter(fmt, datefmt)
    handler = handler_cls(out)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def prefixes_from_str(prefixes):
    EventsError.check_events(set(prefixes.keys()))

    return {getattr(events, key): val for key, val in prefixes.items()}


def reverse_prefixes_from_str(prefixes):
    return dict(zip(prefixes.values(), prefixes.keys()))


def config_from_file():
    global DATA_FOLDER, CONFIG_FNAME

    os.makedirs(DATA_FOLDER, exist_ok=True)
    config_fname = os.path.join(DATA_FOLDER, CONFIG_FNAME)

    if os.path.exists(config_fname) and os.path.getsize(config_fname) > 0:
        with open(config_fname) as f:
            config_data = json.load(f)
    else:
        with open(config_fname, 'w') as f:
            f.write('{}')
        config_data = {}

    config(**config_data)


##################################################
# Interface for changing IahrConfig
##################################################


def config(left=None,
           right=None,
           raw=None,
           cmd=None,
           prefixes=None,
           me=None,
           others=None,
           noone=None,
           log_format=None,
           log_datetime_format=None,
           log_lvl=None,
           local=None,
           data_folder=None,
           media_folder=None,
           edit_to_respond=None,
           custom=None):
    """
        Single entry to framework configuration, 
        just run this with some of updated values and 
        it will update IahrConfig accordingly.
    """
    global SESSION_FNAME, LOG_FNAME
    cfg = IahrConfig

    cfg._update(Delimiter, left=left, right=right, raw=raw)
    cfg._update(CommandDelimiter, cmd=cmd)
    cfg._update(UnknownLocalizationError.lang_from_str, local=local)
    cfg._update(prefixes_from_str, prefixes=prefixes)
    cfg._update(reverse_prefixes_from_str, reverse_prefixes=cfg.PREFIXES)
    cfg._update(lambda x: x,
                me=me,
                others=others,
                noone=noone,
                log_format=log_format,
                log_datetime_format=log_datetime_format,
                data_folder=data_folder,
                media_folder=media_folder,
                custom=custom,
                edit_to_respond=edit_to_respond,
                log_lvl=log_lvl)

    os.makedirs(cfg.DATA_FOLDER, exist_ok=True)
    cfg.SESSION_FNAME = os.path.join(cfg.DATA_FOLDER, SESSION_FNAME)
    cfg.LOG_OUT = os.path.join(cfg.DATA_FOLDER, LOG_FNAME)

    cfg.COMMAND_RE = update_command_re(cfg.CMD)
    cfg.ADD_PARS = update_add_pars(cfg.LEFT, cfg.RIGHT, cfg.CMD, cfg.RAW)
    cfg.LOGGER = update_logger(cfg.LOG_FORMAT, cfg.LOG_DATETIME_FORMAT,
                               cfg.LOG_OUT, cfg.LOG_LVL)

    os.makedirs(cfg.MEDIA_FOLDER, exist_ok=True)


def reset():
    """ 
        Reset(set) IahrConfig to default value
        Single source of truth about default
    """
    global DATA_FOLDER, SESSION_FNAME, LOG_FNAME

    log_format = '%(asctime)s:%(name)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s:'
    log_datetime_format = '%m/%d/%Y %I:%M:%S %p'
    log_lvl = 'INFO'
    IahrConfig.LOGGER = update_logger(log_format, log_datetime_format, sys.stdout, log_lvl)

    config(
        left='[',
        right=']',
        raw='r',
        cmd='.',
        prefixes={
            # additional handlers(not commands)
            'MessageEdited': 'onedit',
        },
        me='me',
        others='*',
        noone='-',
        log_format=log_format,
        log_datetime_format=log_datetime_format,
        log_lvl=log_lvl,
        local='english',
        data_folder=DATA_FOLDER,
        media_folder='media',
        edit_to_respond=False,
        custom={  # custom user config dictionary
            # entity to deduce user of chat in access rights actions
            # (e.g. `allowchat`, `banusr`)
            'current_entity': '$',
        })


##################################################
# Setting config on import
##################################################

reset()
config_from_file()
