from . import utils
from . import run
from . import reg
from . import commands
from . import config
from . import localization


async def init(client, app=None, register=None):
    app = run.Manager() if app is None else app
    register = reg.Register(client, app) if register is None else register
    config.IahrConfig.init(register.app, register)
