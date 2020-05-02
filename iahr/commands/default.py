from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..utils import AccessList
from ..config import IahrConfig


admin_commands = {'.allowusr', '.allowchat', '.banusr', '.banchat'}


def __process_list(single, is_cmds=False):
    if type(single) != str: return [single]
    lst = single.split()
    for i, cmd in enumerate(lst):
        if is_cmds and not IahrConfig.NEW_MSG.is_command(cmd):
            lst[i] = IahrConfig.NEW_MSG.full_command(cmd)
    return lst


@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    app = IahrConfig.APP

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

async def __perm_format(event, lst):
    res = ''
    for ent, perms in lst:
        perms = '\n  '.join(cmd + (' - enabled' if flag else ' - disabled') for cmd, flag in perms.items())
        if ent != IahrConfig.ME:
            ent = await event.client.get_entity(ent)
            ent = ent.username 
        res += '**{}**:\n  {}\n'.format(ent, perms)
    return res

@TextSender('allowedchat', 'Get chat allowed commands')
async def is_allowed_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    res = await __access_action(event, 'is_allowed_chat', chat, cmd, admintoo=True)
    return await __perm_format(event, res)
    

@TextSender('allowedusr', 'Get usr allowed commands')
async def is_allowed_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    res = await __access_action(event, 'is_allowed_usr', usr, cmd, admintoo=True)
    return await __perm_format(event, res)


