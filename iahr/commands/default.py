from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..run import app, Query
from ..utils import AccessList

import asyncio
from pprint import pformat


delimiter = Query.COMMAND_DELIMITER
admin_commands = {'.allowusr', '.allowchat', '.banusr', '.banchat'}


@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    if cmd is not None:
        val = app.commands.get(cmd)
        if val is None:
            res = "No such command(check full help and pass it without dot)"
        else:
            res = '**' + cmd + '**: ' + val.help()
    else:
        helplst = ['**' + cmd  + '**' + ': \n' + routine.help() + '\n' for cmd, routine in app.commands.items()]
        res = '\n'.join(helplst)
    
    return res



is_integer = lambda x: str(x).lstrip('-').isdigit()

async def __usr_from_event(event):
    reply = await event.message.get_reply_message()
    if reply is None:
        me = await AccessList.check_me(event.client)
        res = me(event.message.from_id)
    else:
        res = reply.from_id
    return res

async def __chat_from_event(event):
    return await event.message.get_chat().id

async def __access_action(event, action: str, entity: str, cmd, admintoo=False):
    if not AccessList.is_special(entity) and not is_integer(entity):
        entity = await event.client.get_entity(entity)
        entity = entity.id

    if cmd is not None:
        return getattr(app.commands[cmd], action)(entity)
    else:
        res = {}
        for name, routine in app.commands.items(): 
            if name not in admin_commands or admintoo:
                res[name] = getattr(routine, action)(entity)
            
        return res


@VoidSender('allowusr', 'Allow [UNAME] or "$others" to run a command or all commands')
async def allow_usr(event, usr=None, cmd=None):        
    if usr is None:
        usr = await __usr_from_event(event)
    await __access_action(event, 'allow_usr', usr, cmd=cmd)

@VoidSender('allowchat', 'Allow [CHATNAME] or "$others" to run a command or all commands')
async def allow_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    await __access_action(event, 'allow_chat', chat, cmd=cmd)

@VoidSender('banusr', 'Ban [UNAME] or "$others" from running a command or all commands')
async def ban_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    await __access_action(event, 'ban_usr', usr, cmd=cmd)

@VoidSender('banchat', 'Ban [CHATNAME] or "$others" from running a command or all commands')
async def ban_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    await  __access_action(event, 'ban_chat', chat, cmd=cmd)

@TextSender('allowedchat', 'Get chat allowed commands')
async def is_allowed_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    res = await __access_action(event, 'is_allowed_chat', chat, cmd, admintoo=True)
    return pformat(res)
    

@TextSender('allowedusr', 'Get usr allowed commands')
async def is_allowed_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    print(usr)
    res = await __access_action(event, 'is_allowed_usr', usr, cmd, admintoo=True)
    return pformat(res)

