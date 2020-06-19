from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..utils import AccessList
from ..config import IahrConfig
from .default_loc import localization


##################################################
# Constants
##################################################


local = localization[IahrConfig.LOCAL['lang']]

admin_commands = {
    '.allowusr', '.allowchat', '.banusr', '.banchat',
    '.ignore', '.unignore'
}

DEFAULT_TAG = 'default'
ADMIN_TAG = 'admin'


##################################################
# Utility functions
##################################################


def __process_list(single, is_cmds=False):
    """
        'first second', True -> ['.first', '.second']
        'first second', False -> ['first', 'second']
    """
    if type(single) != str: return [single]
    lst = single.split()
    if is_cmds:
        for i, cmd in enumerate(lst):
            if not IahrConfig.CMD.is_command(cmd) and not cmd.startswith('on'):
                lst[i] = IahrConfig.CMD.full_command(cmd)
    return lst


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


async def __access_action(event,
                          action: str,
                          entity: str,
                          cmd,
                          admintoo=False):
    app = IahrConfig.APP

    entities = __process_list(entity)

    for i, entity in enumerate(entities):
        if not AccessList.is_special(entity) and not is_integer(entity):
            entity = await event.client.get_entity(entity)
            entity = entity.id
            entities[i] = entity

    all_cmds = cmd is None
    if not all_cmds:
        cmds = __process_list(cmd, is_cmds=True)
    else:
        cmds = app.commands.keys()

    entres = []
    for entity in entities:
        cmdres = {}
        for cmd in cmds:
            applies = cmd not in admin_commands or \
                (not AccessList.is_special(entity) and not all_cmds) or admintoo

            if applies:
                routine = app.commands.get(cmd)
                if routine is not None:
                    cmdres[cmd] = getattr(routine, action)(entity)

        entres.append((entity, cmdres))

    return entres


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


@TextSender(about=local['aboutcmds'], tags={DEFAULT_TAG})
async def cmds(event, cmd=None):
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
    

@VoidSender('ignore', about=local['aboutignore'], tags={DEFAULT_TAG, ADMIN_TAG})
async def ignore_chat(event, chat=None):
    await __ignore_action(event, chat, 'ban_chat')


@VoidSender('unignore', about=local['aboutunignore'], tags={DEFAULT_TAG, ADMIN_TAG})
async def unignore_chat(event, chat=None):
    await __ignore_action(event, chat, 'allow_chat')


@TextSender(take_event=False, about=local['aboutsynhelp'], tags={DEFAULT_TAG})
async def synhelp():
    cfg = IahrConfig

    return local['synhelp'].format(
        new_msg=cfg.CMD.original, left=cfg.LEFT.original,
        right=cfg.RIGHT.original, raw=cfg.RAW.original
    )


import re
import atexit

varname_re = re.compile('[a-zA-Z_][a-zA-Z_0-9]*')
alias_template = """
async def doalias(event, {passargs}):
    global args, body
    local_body = body
    passargs = [{passargs}]

    if args and passargs:
        print(args, passargs)
        for arg, parg in zip(args, passargs):
            local_body = local_body.replace('$' + arg, parg)

    local_body = cfg.CMD.unescape(local_body)
    local_body = cfg.LEFT.unescape(local_body)
    local_body = cfg.RIGHT.unescape(local_body)

    event.message.raw_text = local_body
    await cfg.BARE_REG.run(event)
"""

def __parse_alias(event, signature: str):
    global varname_re
    strip = lambda x: x.strip()

    signature, body = map(strip, re.split(':', signature, 1))
    name, *args = map(strip, signature.split())

    for varname in (name, *args):
        if re.match(varname_re, varname) is None:
            event.message.reply(
                local['alias_name_err'].format(varname=varname)
            )
            return
    
    return name, args, body


@VoidSender(about=local['aboutalias'], tags={DEFAULT_TAG, ADMIN_TAG})
async def alias(event, signature: str, about=None):
    global aliases, alias_template

    res = __parse_alias(event, signature)
    if res is None:
        return
    
    name, args, body = res

    scope = {'args' : args, 'body' : body, 'cfg' : IahrConfig}
    exec(
        alias_template.format(passargs=', '.join(args)), 
        scope
    )
    VoidSender(name=name, about=about)(scope['doalias'])

    def remove():
        del IahrConfig.APP.commands[name]

    atexit.register(remove)
