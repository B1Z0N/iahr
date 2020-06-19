from . import utils
from . import localization
from . import config
from . import run
from . import reg
from . import commands


async def init(client, app=None, register=None):
    app = run.Manager() if app is None else app
    register = reg.Register(client, app) if register is None else register
    config.IahrConfig.init(register)
