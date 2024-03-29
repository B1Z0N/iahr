from telethon import events

from iahr.config import IahrConfig
from iahr.commands.default.localization import localization
from iahr.utils import AccessList, EventService

from typing import Union, Mapping, Sequence

##################################################
# Constants
##################################################

DEFAULT_TAG = 'default'
ADMIN_TAG = 'admin'

local = localization[IahrConfig.LOCAL['lang']]

admin_commands = {
    IahrConfig.CMD.full_command(cmd)
    for cmd in
    {'allowusr', 'allowchat', 'banusr', 'banchat', 'errignore', 'errverbose'}
}

##################################################
# Utility functions
##################################################


def process_list(lst: str, is_cmds=False):
    lst = str(lst).split()
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

to_bool = lambda bstr: str(bstr).lower() in ['true', 'yes', 'y']


# backend for .{allow|ban|allowed}{chat|usr} commands
async def commands_access_action(event,
                                 action: str,
                                 entity: str,
                                 commands=None,
                                 admintoo=False):
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


# backend for .{allow|ban|allowed}{chat|usr} handlers
async def handlers_access_action(event,
                                 action: str,
                                 entity: str,
                                 prefix: str,
                                 handlers=None,
                                 admintoo=False):
    entities = await __process_entities(event, entity)
    dct = IahrConfig.APP.handlers.get(prefix)
    if dct is None:
        return local['handlers']['nosuchtype'].format(etype=prefix)

    all_handlers = handlers is None
    if all_handlers:
        handlers = dct.keys()
    else:
        handlers = process_list(handlers)

    entres = {}
    for ent in entities:
        hndlres = {}
        for handler in handlers:
            applies = (prefix + handler
                       ) not in admin_commands or not all_handlers or admintoo
            routine = dct.get(handler)
            if routine is None:
                continue
            if applies:
                hndlres[handler] = getattr(routine, action)(ent)

        entres[ent] = hndlres

    return entres


# backend for .{allow|ban|allowed}{chat|usr} tags
async def tags_access_action(event,
                             action: str,
                             entity,
                             tag=None,
                             admintoo=False):

    print(event, action, entity, tag, admintoo, sep='\n')
    app = IahrConfig.APP
    entities = await __process_entities(event, entity)

    all_tags = tag is None
    if all_tags:
        tags = app.tags.keys()
    else:
        tags = process_list(tag)

    entres = {}
    admin_commands = set(app.tags[ADMIN_TAG].keys())
    print(admin_commands)
    for ent in entities:
        tagres = {}
        for tag in tags:
            if (tag == ADMIN_TAG and all_tags) and not admintoo:
                continue
            elif (dct := app.tags.get(tag)) is None:
                tagres[tag] = False
            else:
                tagres[tag] = True
                for name, routine in dct.items():
                    if name in admin_commands and tag != ADMIN_TAG:
                        continue
                    tagres[tag] = getattr(routine, action)(ent) and tagres[tag]
        entres[ent] = tagres

    import pprint
    pprint.PrettyPrinter(indent=4).pprint(entres)
    return entres


enabled = ' - ' + local['enabled']
disabled = ' - ' + local['disabled']


async def perm_format(event, ent_perms: dict):
    res = ''
    for ent, perms in ent_perms.items():
        perms = '\n  '.join(perm + (enabled if flag else disabled)
                            for perm, flag in perms.items())
        if not AccessList.is_special(ent):
            ent = await event.client.get_entity(ent)
            ent = ent.username
        res += '**{}**:\n  {}\n'.format(ent, perms)
    return res


async def generic_access_action(event, action, action_type, ent, *args,
                                **kwargs):
    if ent == IahrConfig.CUSTOM['current_entity']:
        if action.endswith('chat'):
            ent = await EventService.chatid_from(event)
        elif action.endswith('usr'):
            ent = await EventService.userid_from(event, deduce=True)

    if action_type == 'commands':
        return await commands_access_action(event, action, ent, *args,
                                            **kwargs)
    elif action_type == 'handlers':
        return await handlers_access_action(event, action, ent, *args,
                                            **kwargs)
    elif action_type == 'tags':
        return await tags_access_action(event, action, ent, *args, **kwargs)
    else:
        return local['unknownactiontype'].format(action_type)


async def ignore_action(event, chat, action):
    app = IahrConfig.APP
    action = getattr(app, action)

    if chat == IahrConfig.CUSTOM['current_entity']:
        chat = await EventService.chatid_from(event)
        action(chat)
        return

    chats = __process_entities(event, chat)
    for chat in chats:
        action(chat)
