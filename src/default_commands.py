from telethon import event

from app import InfoParameter, app, EntityGroup as grp
from senders import TextSender


@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    if cmd is not None:
        res = cmd + ': ' + app.commands[cmd].help()
    else:
        helplst = [cmd + ': ' + routine.help() for cmd, routine in app.commands.items()]
        res = '\n'.join(helplst)
    
    return event.message, res


@TextSender('.allowusr', 'Allow "me", "others", "all" or $UNAME to run a command')
async def allow_usr(event, usr, cmd=None):        
    client = par.event.client
    group = grp.from_str(usr)    
    usr = client.get_entity(usr).id if group is None else group 

    if cmd is not None:
        app.commands[cmd].allow_usr(usr)
    else:
        for routine in app.commands.values():
            routine.allow_usr(usr) 


@TextSender
async def allow_chat(par, chat=None, cmd=None):
    pass


@TextSender
async def ban_usr(par, usr=None, cmd=None):
    pass


@TextSender
async def ban_chat(par, chat=None, cmd=None):
    pass

        

