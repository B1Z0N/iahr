import pytest

import sys
from copy import deepcopy

from telethon import events

from iahr.config import IahrConfig as icfg, config as cfg
from iahr import config


PREFIXES = {
    events.MessageEdited: 'edit',
    events.MessageDeleted: 'del',
    events.MessageRead: 'read',
    events.ChatAction: 'chataction',
    events.UserUpdate: 'usrupdate',
    events.Album: 'album',
}


def test_config():
    prev_add_pars = icfg.ADD_PARS

    cfg(
        left='{', right='}', raw='e', new_msg='!', 
        non_new_msg='.', prefix='k', prefixes=PREFIXES, me='my',
        others='/', log_format='%(name)s', log_datetime_format='%m', 
        session_fname='ses'
    )

    assert icfg.LEFT.original == '{'
    assert icfg.RIGHT.original == '}'
    assert icfg.RAW.original == 'e'
    assert icfg.NEW_MSG.original == '!'
    assert icfg.NON_NEW_MSG.original == '.'
    assert icfg.PREFIX.original == 'k'
    assert icfg.PREFIXES == PREFIXES
    assert icfg.ME == 'my'
    assert icfg.OTHERS == '/'
    assert icfg.LOG_FORMAT == '%(name)s'
    assert icfg.LOG_DATETIME_FORMAT == '%m'
    assert icfg.SESSION_FNAME == 'ses'
    assert icfg.COMMAND_RE == config.update_command_re(icfg.NEW_MSG)

    assert icfg.LOGGER == config.update_logger(
        icfg.LOG_FORMAT, icfg.LOG_DATETIME_FORMAT, icfg.LOG_OUT
    )
    assert prev_add_pars != icfg.ADD_PARS

    config.reset()

