from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..run import app, Query
from .utils import AccessList

import asyncio

delimiter = Query.COMMAND_DELIMITER


@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    if cmd is not None:
        val = app.commands.get(delimiter.original + cmd)
        if val is None:
            res = "No such command(check full help and pass it without dot)"
        else:
            res = '**' + cmd + '**: ' + val.help()
    else:
        helplst = ['**' + cmd  + '**' + ': \n' + routine.help() + '\n' for cmd, routine in app.commands.items()]
        res = '\n'.join(helplst)
    
    return res



is_integer = lambda x: x.lstrip('-').isdigit()

async def __access_action(event, action: str, entity: str, cmd=None):
    if not AccessList.is_special(entity) and not is_integer(entity):
        entity = await event.client.get_entity(entity)
        entity = entity.id

    if cmd is not None:
        getattr(app.commands[cmd], action)(entity)
    else:
        for routine in app.commands.values():
            getattr(routine, action)(entity)


@VoidSender('allowusr', 'Allow [UNAME] or "$others" to run a command or all commands')
async def allow_usr(event, usr, cmd=None):        
    await __access_action(event, 'allow_usr', usr, cmd=cmd)

@VoidSender('allowchat', 'Allow [CHATNAME] or "$others" to run a command or all commands')
async def allow_chat(event, chat, cmd=None):
    await __access_action(event, 'allow_chat', chat, cmd=cmd)

@VoidSender('banusr', 'Ban [UNAME] or "$others" from running a command or all commands')
async def ban_usr(event, usr, cmd=None):
    await __access_action(event, 'ban_usr', usr, cmd=cmd)

@VoidSender('banchat', 'Ban [CHATNAME] or "$others" from running a command or all commands')
async def ban_chat(event, chat, cmd=None):
   await  __access_action(event, 'ban_chat', chat, cmd=cmd)












