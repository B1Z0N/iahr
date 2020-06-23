import pytest

import os
import sys
from copy import deepcopy

from telethon import events

from iahr.config import IahrConfig as icfg, config as cfg
from iahr import config

PREFIXES = {
    'MessageEdited': 'edit',
    'MessageDeleted': 'del',
    'MessageRead': 'read',
}

TRUE_PREFIXES = {
    getattr(events, evstr): pref
    for evstr, pref in PREFIXES.items()
}


def test_config():
    prev_add_pars = icfg.ADD_PARS

    cfg(left='{',
        right='}',
        raw='e',
        cmd='!',
        prefixes=PREFIXES,
        me='my',
        others='/',
        log_format='%(name)s',
        log_datetime_format='%m',
        local='russian',
        data_folder='folder',
        custom={'current_entity': '_'},
        mode='DEBUG')

    assert icfg.LEFT.original == '{'
    assert icfg.RIGHT.original == '}'
    assert icfg.RAW.original == 'e'
    assert icfg.CMD.original == '!'
    assert icfg.PREFIXES == TRUE_PREFIXES
    assert icfg.REVERSE_PREFIXES == dict(
        zip(TRUE_PREFIXES.values(), TRUE_PREFIXES.keys()))
    assert icfg.ME == 'my'
    assert icfg.OTHERS == '/'
    assert icfg.LOG_FORMAT == '%(name)s'
    assert icfg.LOG_DATETIME_FORMAT == '%m'
    assert icfg.COMMAND_RE == config.update_command_re(icfg.CMD)
    assert icfg.LOCAL['lang'] == 'russian'
    assert icfg.SESSION_FNAME == os.path.join('folder', 'iahr.session')
    assert icfg.LOG_OUT == os.path.join('folder', 'iahr.log')
    assert icfg.DATA_FOLDER == 'folder'

    assert icfg.LOGGER == config.update_logger(icfg.LOG_FORMAT,
                                               icfg.LOG_DATETIME_FORMAT,
                                               icfg.LOG_OUT)
    assert prev_add_pars != icfg.ADD_PARS

    config.reset()
