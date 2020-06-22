
from telethon import events

from iahr.config import IahrConfig
from .default_loc import localization
from iahr.utils import AccessList

from typing import Union, Mapping, Sequence


##################################################
# Constants
##################################################


DEFAULT_TAG = 'default'
ADMIN_TAG = 'admin'

local = localization[IahrConfig.LOCAL['lang']]

admin_commands = { 
    IahrConfig.CMD.full_command(cmd) for cmd in { 
        'allowusr', 'allowchat', 'banusr', 'banchat',
        'errignore', 'errverbose'
    }
}

local = localization[IahrConfig.LOCAL['lang']]


##################################################
# Utility functions
##################################################


def process_list(lst: str, is_cmds=False):
    lst = lst.split()
    if is_cmds:
        cmddel = IahrConfig.CMD
        for i, cmd in enumerate(lst):
            if not cmddel.is_command(cmd):
                lst[i] = cmddel.full_command(cmd)

    return lst


async def __process_entities(event, entities: str):
    entities = process_list(str(entities))

    for i, entity in enumerate(entities):
        if not AccessList.is_special(entity):
            if not __is_integer(entity):
                entity = await event.client.get_entity(entity)
                entities[i] = entity.id
            # make sure everything is being stored as an int
            entities[i] = int(entities[i])
    
    return entities


__is_integer = lambda x: str(x).lstrip('-').isdigit()


async def usr_from_event(event):
    reply = await event.message.get_reply_message()
    me = await AccessList.check_me(event.client)
    if reply is None:
        res = int(event.message.from_id)
    else:
        res = int(reply.from_id)
    return me(res)


async def chat_from_event(event):
    me = await AccessList.check_me(event.client)
    chat = await event.message.get_chat()
    return me(chat.id)


# backend for .{allow|ban}{chat|usr} commands
async def commands_access_action(
    event, action: str, entity: str, 
    commands=None, admintoo=False
):
    entities = await __process_entities(event, entity)
    dct = IahrConfig.APP.commands
    CMD = IahrConfig.CMD
    if dct is None:
        return local['nosuchcmd']

    all_commands = commands is None
    if all_commands:
        commands = dct.keys()
    else:
        commands = process_list(commands, is_cmds=True)

    entres = {}
    for ent in entities:
        cmdres = {}
        for command in commands:
            applies = command not in admin_commands or not all_commands or admintoo
            routine = dct.get(command)
            if routine is None:
                continue
            if applies:
                cmdres[command] = getattr(routine, action)(ent)
        entres[ent] = cmdres

    return entres


# backend for .{allow|ban}{chat|usr} handlers
async def handlers_access_action(
    event, action: str, entity: str, 
    prefix: str, handlers=None, admintoo=False
):
    entities = await __process_entities(event, entity)
    dct = IahrConfig.APP.handlers.get(prefix)
    if dct is None:
        msg = local['handlers']['nosuchtype'].format(etype=etype_front_name)
        await event.message.reply(msg)
        return

    all_handlers = handlers is None
    if all_handlers:
        handlers = dct.keys()
    else:
        handlers = process_list(handlers)

    print('\n\n', entities, handlers, '\n\n')

    entres = {}
    for ent in entities:
        hndlres = {}
        for handler in handlers:
            applies = (prefix + handler) not in admin_commands or not all_handlers or admintoo
            routine = dct.get(handler)
            if routine is None:
                continue
            if applies:
                hndlres[handler] = getattr(routine, action)(ent)

        entres[ent] = hndlres
    
    return entres


# backend for .{allow|ban}{chat|usr} tags
async def tags_access_action(
    event, action: str, entity, tag=None, admintoo=False
):
    app = IahrConfig.APP
    entities = await __process_entities(event, entity)
    
    all_tags = tag is None
    if all_tags:
        tags = app.tags.keys()
    else:
        tags = process_list(tag)

    tagres = {}
    for ent in entities:
        for tag in tags:
            applies = tag != ADMIN_TAG or not all_tags or admintoo
            dct = app.tags.get(tag)
            if dct is None:
                tagres[tag] = local['nosuchtag'].format(tag)
                continue
            for name, routine in dct.items():
                getattr(routine, action)(ent)
    
    return tagres


async def perm_format(event, lst):
    global local # :)

    enabled = ' - ' + local['enabled']
    disabled = ' - ' + local['disabled']

    res = ''
    for ent, perms in lst:
        perms = '\n  '.join(cmd + (enabled if flag else disabled)
                            for cmd, flag in perms.items())
        if ent != IahrConfig.ME:
            ent = await event.client.get_entity(ent)
            ent = ent.username
        res += '**{}**:\n  {}\n'.format(ent, perms)
    return res


async def ignore_action(event, chat, action):
    app = IahrConfig.APP
    action = getattr(app, action)

    if chat == IahrConfig.CUSTOM['current_entity']:
        chat = await chat_from_event(event)
        action(chat)
        return

    chats = await __process_entities(event, chat)
    for chat in chats:
        action(chat)

