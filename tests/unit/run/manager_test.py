import pytest

from iahr.run import Manager
from iahr.config import IahrConfig

from copy import deepcopy
import os, sys, atexit

from telethon import events


@pytest.fixture
def gen_handler():
    i = 1

    def do(cmd):
        return cmd, lambda *args, **kwargs: i, 'about', events.NewMessage, set()

    return do


@pytest.fixture
def compare_handlers():
    me = IahrConfig.ME

    def do(app, fst, snd):
        fst = app.commands[fst].get_handler(me, me)()
        snd = app.commands[snd].get_handler(me, me)()
        return fst == snd

    return do

