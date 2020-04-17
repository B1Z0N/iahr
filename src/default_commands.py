from telethon import events

from app import InfoParameter
from senders import TextSender, eventless


@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    if cmd is not None:
        res = cmd + ': ' + app.commands[cmd].help()
    else:
        helplst = [cmd + ': ' + routine.help() for cmd, routine in app.commands.items()]
        res = '\n'.join(helplst)
    
    return res


def __access_action(action: str, entity: str, cmd=None):
    if cmd is not None:
        getattr(app.commands[cmd], action)(entity)
    else:
        for routine in app.commands.values():
            getattr(routine, action)(entity)


@VoidSender('.allowusr', 'Allow [UNAME] or "$others" to run a command or all commands')
async def allow_usr(_, usr, cmd=None):        
    __access_action('allow_usr', usr, cmd=cmd)

@VoidSender('.allowchat', 'Allow [CHATNAME] or "$others" to run a command or all commands')
async def allow_chat(_, chat, cmd=None):
    __access_action('allow_chat', chat, cmd=cmd)

@VoidSender('banusr', 'Ban [UNAME] or "$others" from running a command or all commands')
async def ban_usr(_, usr, cmd=None):
    __access_action('ban_usr', usr, cmd=cmd)

@VoidSender('banchat', 'Ban [CHATNAME] or "$others" from running a command or all commands')
async def ban_chat(_, chat, cmd=None):
    __access_action('ban_chat', chat, cmd=cmd)


