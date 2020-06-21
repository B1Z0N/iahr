from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..utils import AccessList
from ..config import IahrConfig
from .default_loc import localization

from typing import Union, Mapping, Sequence

##################################################
# Constants
##################################################


local = localization[IahrConfig.LOCAL['lang']]

admin_commands = { 
    IahrConfig.CMD.full_command(cmd) for cmd in { 
        'allowusr', 'allowchat', 'banusr', 'banchat',
        'errignore', 'errverbose'
    }
}

DEFAULT_TAG = 'default'
ADMIN_TAG = 'admin'


##################################################
# Utility functions
##################################################


def __process_list(lst: str, is_cmds=False):
    lst = lst.split()
    if is_cmds:
        cmddel = IahrConfig.CMD
        for i, cmd in enumerate(lst):
            if not cmddel.is_command(cmd):
                lst[i] = cmddel.full_command(cmd)

    return lst


async def __process_entities(event, entities):
    entities = __process_list(entity)

    for i, entity in enumerate(entities):
        if not AccessList.is_special(entity) and not is_integer(entity):
            entity = await event.client.get_entity(entity)
            entity = entity.id
            entities[i] = entity
    
    return entities


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

def __get_reverse_etype(etype_front_name):
    pre = IahrConfig.PREFIXES
    rev = dict(zip(pre.values(), pre.keys()))
    revetype = rev.get(etype_front_name)
    if revetype is None:
        return local['handlers']['nosuchtype'].format(etype=etype_front_name), False
    return revetype.__name__, True

async def __collect_routines(statements):
    pre, app = IahrConfig.PREFIXES, IahrConfig.APP
    res = {}

    for st in statements:
        for etype, prefix in pre.items():
            if st.startswith(prefix):
                res[st[len(prefix):]] = app.handlers[etype.__name__].get(st)
                break
        else:
            res[st] = app.commands[st]

    return res


async def __handlers_access_action(
    event, action: str, entities: Sequence[str], 
    prefix: str, handlers=None: Sequence[str], admintoo=False
):
    dct = IahrConfig.APP.handlers.get(prefix)
    if dct is None:
        return local['handlers']['nosuchtype'].format(prefix)

    all_handlers = handlers is None
    if all_handlers:
        handlers = dct.keys()

    entres = []
    for ent in entities:
        hndlres = {}
        for handler in handlers:
            applies = (prefix + handler) not in admin_commands \
                or not all_handlers or admintoo

            routine = dct.get(handler)
            if routine is None:
                continue

            if applies:
                hndlres[handler] = getattr(routine, action)(ent)
        
        entres.append((ent, hndlres))
    
    return entres
            

async def __commands_access_action(
    event, action: str, entities: Sequence[str], 
    commands=None: Sequence[str], admintoo=False
):
    dct = IahrConfig.APP.commands
    CMD = IahrConfig.CMD
    if dct is None:
        return local['nosuchcmd']

    all_commands = commands is None
    if all_commands:
        commands = dct.keys()

    for ent in entities:
        entres = []
        for command in commands:
            cmdres = {}
            applies = CMD.full_command(command) not in admin_commands or not all_commands or admintoo
            routine = dct.get(command)
            if routine is None:
                continue
            if applies:
                cmdres[cmd] = getattr(routine, action)(ent)
        entres.append((ent, cmdres))

    return entres


async def __tags_access_action(
    event, action: str, entity, tag, admintoo=False
):
    app = IahrConfig.APP
    entities = __process_entities(entity)
    tags = __process_list(tag)

    res = {}
    for tag in tags:
        dct = app.tags.get(tag)
        if dct is None:
            res[tag] = locals['nosuchtag']
            continue
        for name in dct.items():
            getattr()


async def __perm_format(event, lst):
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


async def __ignore_action(event, chat, action):
    app = IahrConfig.APP
    action = getattr(app, action)

    if chat is None:
        chat = await __chat_from_event(event)
        action(chat)
        return

    chats = __process_list(chat)

    for i, chat in enumerate(chats):
        if not AccessList.is_special(chat) and not is_integer(chat):
            chat = await event.client.get_chat(chat)
            chat = chat.id
        
        action(chat)


##################################################
# Routines themselves
##################################################


@TextSender(about=local['abouthelp'], take_event=False, tags={DEFAULT_TAG})
async def help():
    return local['help'].format(new_msg=IahrConfig.CMD.original)


@TextSender(about=local['aboutcommands'], tags={DEFAULT_TAG})
async def commands(event, cmd=None):
    app = IahrConfig.APP

    if cmd is None:
        return '\n'.join(f'**{cmd}**' for cmd in app.commands.keys())

    cmds, helplst = __process_list(cmd, is_cmds=True), []
    for cmd in cmds:
        val = app.commands.get(cmd)
        res = '**{}**:\n{}\n'\
            .format(cmd, local['nosuchcmd'] if val is None else val.help())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res


@TextSender(about=local['abouthandlers'], tags={DEFAULT_TAG})
async def handlers(event, etype=None, hndl=None):
    app = IahrConfig.APP

    if etype is None and hndl is not None:
        return local['handlers']['wrongordering']
    
    def for_etype(etype_name):
        handlers = app.handlers[etype_name]
        res = f'**{IahrConfig.PREFIXES[getattr(events, etype_name)]}**' + ':\n'
        for name in handlers.keys():
            res += f'  `{name}`'

        return res

    if hndl is None:
        if etype is None:
            return '\n'.join(map(for_etype, app.handlers.keys()))
        else:
            res, status = __get_reverse_etype(etype)
            return for_etype(res) if status else res

    hndls, helplst = __process_list(hndl), [ f'`{etype}`' + ':\n']
    res, status = __get_reverse_etype(etype)
    if not status:
        return res
    dct = app.handlers[res]

    for hndl in hndls:
        val = dct.get(hndl)
        res = '\t**{}**:\n{}\n'\
            .format(hndl, '\n    ' + local['handlers']['nosuchhndl'] if val is None else val.help())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res

    
@TextSender(about=local['abouttags'], tags={DEFAULT_TAG})
async def tags(event, tag=None):
    app = IahrConfig.APP

    if tag is None:
        return '\n'.join(f'**{tag}**' for tag in app.tags.keys())

    tags, helplst = __process_list(tag), []
    for tag in tags:
        val = app.tags.get(tag)
        res = f'**{tag}**:\n'
        if val is None:
            res += local['nosuchtag']
        else:
            res += '\n'.join(f'    **{cmd}**' for cmd in val)
        helplst.append(res)

    res = '\n'.join(helplst)
    return res

@VoidSender('allowusr', about=local['aboutallowusr'], tags={DEFAULT_TAG, ADMIN_TAG})
async def allow_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    await __access_action(event, 'allow_usr', usr, cmd=cmd)


@VoidSender('allowchat', about=local['aboutallowchat'], tags={DEFAULT_TAG, ADMIN_TAG})
async def allow_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    await __access_action(event, 'allow_chat', chat, cmd=cmd)


@VoidSender('banusr', about = local['aboutbanusr'], tags={DEFAULT_TAG, ADMIN_TAG})
async def ban_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    await __access_action(event, 'ban_usr', usr, cmd=cmd)


@VoidSender('banchat', about=local['aboutbanchat'], tags={DEFAULT_TAG, ADMIN_TAG})
async def ban_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    await __access_action(event, 'ban_chat', chat, cmd=cmd)


@TextSender('allowedchat', about=local['aboutallowedchat'], tags={DEFAULT_TAG})
async def is_allowed_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    res = await __access_action(event,
                                'is_allowed_chat',
                                chat,
                                cmd,
                                admintoo=True)
    return await __perm_format(event, res)


@TextSender('allowedusr', about=local['aboutallowedusr'], tags={DEFAULT_TAG})
async def is_allowed_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    res = await __access_action(event,
                                'is_allowed_usr',
                                usr,
                                cmd,
                                admintoo=True)
    return await __perm_format(event, res)
    

@VoidSender('errignore', about=local['aboutignore'], tags={DEFAULT_TAG, ADMIN_TAG})
async def ignore_chat(event, chat=None):
    await __ignore_action(event, chat, 'ban_chat')


@VoidSender('errverbose', about=local['aboutverbose'], tags={DEFAULT_TAG, ADMIN_TAG})
async def unignore_chat(event, chat=None):
    await __ignore_action(event, chat, 'allow_chat')


@TextSender(take_event=False, about=local['aboutsynhelp'], tags={DEFAULT_TAG})
async def synhelp():
    cfg = IahrConfig

    return local['synhelp'].format(
        new_msg=cfg.CMD.original, left=cfg.LEFT.original,
        right=cfg.RIGHT.original, raw=cfg.RAW.original
    )

