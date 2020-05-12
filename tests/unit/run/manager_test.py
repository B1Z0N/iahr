import pytest

from iahr.run import Manager
from iahr.config import IahrConfig

from copy import deepcopy
import os, sys, atexit

@pytest.fixture
def gen_handler():
    i = 1
    def do(cmd):
        return cmd, lambda *args, **kwargs: i, 'about'
    return do

@pytest.fixture
def compare_handlers():
    me = IahrConfig.ME
    def do(app, fst, snd):
        fst = app.commands[fst].get_handler(me, me)()
        snd = app.commands[snd].get_handler(me, me)()
        return fst == snd

    return do

def test_dump(gen_handler, compare_handlers):
    sessionf = IahrConfig.SESSION_FNAME
    before = None

    if os.path.exists(sessionf):
        with open(sessionf) as f:
            before = f.read()
        os.remove(sessionf)
    
    app = Manager()
    app.add(*gen_handler('.do'))
    app.add(*gen_handler('.do1'))
    assert compare_handlers(app, '.do', '.do1')

    if before is not None:
        app.dump()
        with open(sessionf) as f:
            assert before == f.read()
