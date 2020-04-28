from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..run import app, Query
from ..utils import AccessList

import asyncio
from pprint import pformat


delimiter = Query.COMMAND_DELIMITER
admin_commands = {'.allowusr', '.allowchat', '.banusr', '.banchat'}

def __process_list(single, is_cmds=False):
    if type(single) != str: return [single]
    lst = single.split()
    return [
        Query.COMMAND_DELIMITER.full_command(cmd) for cmd in lst
    ] if is_cmds else lst


@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    if cmd is not None:
        cmds = __process_list(cmd, is_cmds=True)
    else:
        cmds = app.commands.keys()
    
    helplst, nosuch = [], "No such command(try checking full help)" 
    for cmd in cmds:
        val = app.commands.get(cmd)
        res = '**{}**:\n{}\n'.format(
            cmd, nosuch if val is None else app.commands[cmd].help()
        )
        helplst.append(res)

    res = '\n'.join(helplst)
    return res



is_integer = lambda x: str(x).lstrip('-').isdigit()

async def __usr_from_event(event):
    reply = await event.message.get_reply_message()
    me = await AccessList.check_me(event.client)
    if reply is None:
        res = event.message.from_id
    else:
        res = reply.from_id
    return me(res)

async def __chat_from_event(event):
    chat = await event.message.get_chat()
    return chat.id

async def __access_action(event, action: str, entity: str, cmd, admintoo=False):
    entities = __process_list(entity)
    for i, entity in enumerate(entities):
        if not AccessList.is_special(entity) and not is_integer(entity):
            entity = await event.client.get_entity(entity)
            entity = entity.id
            entities[i] = entity
    print(entities) 
    all_cmds = cmd is None
    if not all_cmds:
        cmds = __process_list(cmd, is_cmds=True)
    else:
        cmds = app.commands.keys()
            
    
    entres = {}
    for entity in entities:
        cmdres = {}
        for cmd in cmds:
            if cmd not in admin_commands or (not AccessList.is_special(entity) and not all_cmds) or admintoo:
                routine = app.commands.get(cmd)
                if routine is not None:
                    cmdres[cmd] = getattr(routine, action)(entity)
        entres[entity] = cmdres
            
    return entres


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
    print(usr)
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
    res = await __access_action(event, 'is_allowed_usr', usr, cmd, admintoo=True)
    return pformat(res)

