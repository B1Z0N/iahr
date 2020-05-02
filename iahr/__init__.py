from . import utils
from . import run
from . import reg
from . import commands
from . import config

async def init(client):
    app = run.Manager()
    register = reg.Register(client, app)
    config.init_config(app, register)
