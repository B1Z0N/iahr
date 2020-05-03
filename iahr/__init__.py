from . import utils
from . import run
from . import reg
from . import commands
from . import config

async def init(client):
    app = run.Manager()
    register = reg.Register(client, app)
    config.IahrConfig.init(app, register)

