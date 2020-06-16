from telethon import events

from ..reg import TextSender, VoidSender, MultiArgs
from ..utils import AccessList
from ..config import IahrConfig

admin_commands = {
    '.allowusr', '.allowchat', '.banusr', '.banchat',
    '.ignore', '.unignore',
}
nosuchcmd = """
    No such command(try checking full list: `.cmds`)
"""
nosuchtag = """
    No such tag(try checking full list: `.tags`)
"""
DEFAULT_TAG = 'default'
ADMIN_TAG = 'admin'


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


@TextSender(about="""
    Get general info to start with
""", take_event=False, tags={DEFAULT_TAG})
async def help():
    return \
r"""

Get help about syntax 
with **{new_msg}synhelp**.

See **{new_msg}cmds** for the list 
of available commands. 

Pass command to get detailed info:
    
    `{new_msg}cmds cmds`

See **{new_msg}tags** for the list 
of available tags.

Pass tag to get detailed info
and commands with this tag:
    
    `{new_msg}tags help`

""".format(new_msg=IahrConfig.CMD.original)


@TextSender(about="""
    Get help about a command or list of all commands
""", tags={DEFAULT_TAG})
async def cmds(event, cmd=None):
    app = IahrConfig.APP

    if cmd is None:
        return '\n'.join(f'**{cmd}**' for cmd in app.commands.keys())

    cmds, helplst = __process_list(cmd, is_cmds=True), []
    for cmd in cmds:
        val = app.commands.get(cmd)
        res = '**{}**:\n{}\n'.format(cmd,
                                     nosuchcmd if val is None else val.help())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res

    
@TextSender(about="""
    Get the list of all tags or list of commands tagged
""", tags={DEFAULT_TAG})
async def tags(event, tag=None):
    app = IahrConfig.APP

    if tag is None:
        return '\n'.join(f'**{tag}**' for tag in app.tags.keys())

    tags, helplst = __process_list(tag), []
    print(tags)
    for tag in tags:
        val = app.tags.get(tag)
        res = f'**{tag}**:\n'
        if val is None:
            res += nosuchcmd
        else:
            res += '\n'.join(f'    **{cmd}**' for cmd in val)
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


@VoidSender('allowusr', """
    Allow usr to run a command

        by nick, id or phone number all comands:

        `.allowusr uname`
        
        all users some commands:
        
        `.allowusr * [cmd1 cmd2 cmd3]`
        
        me or the user that you are replying to
        
        `.allowusr cmd=command`
""", tags={DEFAULT_TAG, ADMIN_TAG})
async def allow_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    await __access_action(event, 'allow_usr', usr, cmd=cmd)


@VoidSender('allowchat', """
    Allow a command to be runned in this chat

        by chatname or id all commands:
        
        `.allowchat chatname`
        
        all chats some commands(except admin ones)
        
        `.allowchat * [cmd1 cmd2 cmd3]`
        
        the chat that you are writing this in:
        
        `.allowchat cmd=command`
""", tags={DEFAULT_TAG, ADMIN_TAG})
async def allow_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    await __access_action(event, 'allow_chat', chat, cmd=cmd)


@VoidSender('banusr', """
    Ban usr from running a command

        by nick, id or phone number all comands:
        
        `.banusr uname`
        
        all users some commands:
        
        `.banusr * [cmd1 cmd2 cmd3]`
        
        me or the user that you are replying to
        
        `.banusr cmd=command`
""", tags={DEFAULT_TAG, ADMIN_TAG})
async def ban_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    await __access_action(event, 'ban_usr', usr, cmd=cmd)


@VoidSender('banchat', """
    Ban command from running in this chat

        by chatname or id all commands:
        
        `.allowchat chatname`
        
        all chats some commands(except admin ones)
        
        `.allowchat * [cmd1 cmd2 cmd3]`
        
        the chat that you are writing this in:
        
        `.allowchat cmd=command`
""", tags={DEFAULT_TAG, ADMIN_TAG})
async def ban_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    await __access_action(event, 'ban_chat', chat, cmd=cmd)


async def __perm_format(event, lst):
    res = ''
    for ent, perms in lst:
        perms = '\n  '.join(cmd + (' - enabled' if flag else ' - disabled')
                            for cmd, flag in perms.items())
        if ent != IahrConfig.ME:
            ent = await event.client.get_entity(ent)
            ent = ent.username
        res += '**{}**:\n  {}\n'.format(ent, perms)
    return res


@TextSender('allowedchat', """
    Get the commands allowed in a chat:

        by chatname or id:
        
        `.allowedchat chatname command`
        
        in current chat
        
        `.allowedchat cmd=command`
        
        list of commands, list of chats
        
        `.allowedchat [chat1 chat2] [cmd1 cmd2 cmd3]`
""", tags={DEFAULT_TAG})
async def is_allowed_chat(event, chat=None, cmd=None):
    if chat is None:
        chat = await __chat_from_event(event)
    res = await __access_action(event,
                                'is_allowed_chat',
                                chat,
                                cmd,
                                admintoo=True)
    return await __perm_format(event, res)


@TextSender('allowedusr', """
    Get the commands allowed to a usr:

        by usernaem, id or phone number:
        
        `.allowedusr usrname command`
        
        current user or the user 
        that you are replying to
        
        `.allowedusr cmd=command`
        
        list of commands, list of users
        
        `.allowedusr [usr1 usr2] [cmd1 cmd2 cmd3]`
""", tags={DEFAULT_TAG})
async def is_allowed_usr(event, usr=None, cmd=None):
    if usr is None:
        usr = await __usr_from_event(event)
    res = await __access_action(event,
                                'is_allowed_usr',
                                usr,
                                cmd,
                                admintoo=True)
    return await __perm_format(event, res)


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
    

@VoidSender('ignore', """
    Ignore a chat when processing commands from
    banned users. Reduces spam level.

        by chatname or id all commands:
        
        `.ignore chatname`
        
        all chats
        
        `.ignore *`
        
        the chat that you are writing this in:
        
        `.ignore`
""", tags={DEFAULT_TAG, ADMIN_TAG})
async def ignore_chat(event, chat=None):
    await __ignore_action(event, chat, 'ban_chat')


@VoidSender('unignore', """
    Enable chat when processing commands from
    banned users. Increases spam level, but
    also increases clarity.

        by chatname or id all commands:
        
        `.unignore chatname`
        
        all chats
        
        `.unignore *`
        
        the chat that you are writing this in:
        
        `.unignore`
""", tags={DEFAULT_TAG, ADMIN_TAG})
async def unignore_chat(event, chat=None):
    await __ignore_action(event, chat, 'allow_chat')


@TextSender(take_event=False, about="""
    Get help about syntax rules
""", tags={DEFAULT_TAG})
async def synhelp():
    cfg = IahrConfig

    return \
r"""
Hy, my name is [iahr](https://github.com/B1Z0N/iahr/). 

------------------------------------

All commands start with "`{new_msg}`",
arguments can be passed too: 

    `{new_msg}cmds help` or `{new_msg}cmds {left}help{right}`

------------------------------------

Pros of using brackets is that you can 
pass args with spaces, but don't forget 
to escape special symbols in brackets:

    `{new_msg}cmds {left}very weird command \\{new_msg}\\{left}\\{right}{right}`

------------------------------------

Also there are `raw args`:

    `{new_msg}cmds {raw}{left}very weird command {new_msg}{left}{right}{right}{raw}`

------------------------------------

You could use keyword args:
    allow me to run `cmds` command

    `{new_msg}allowusr usr=me cmd=cmds`

    allow ... to run all commands

    `{new_msg}allowusr [usr=wery weird user with = sign]`

Or even like this:

    `{new_msg}do [what={new_msg}do1 other {new_msg}do2]`

------------------------------------

And the most important thing, 
you can chain commands, as long 
as they support each others return 
types:

    `{new_msg}do1 {left}{new_msg}do2 {left}arg1{right}{right} {left}{new_msg}do3{right}`

The brackets will add up automatically:

    `{new_msg}do1 {new_msg}do2 arg1 {new_msg}do3`
        means
    `{left}{new_msg}do1 {left}{new_msg}do2 {left}arg1{right} {left}{new_msg}do3{right}{right}{right}`

------------------------------------

Hey, **buddy**, use me tenderly and 
don't forget about your **IMAGINATION**!

""".format(
    new_msg=cfg.CMD.original, left=cfg.LEFT.original,
    right=cfg.RIGHT.original, raw=cfg.RAW.original
    )

