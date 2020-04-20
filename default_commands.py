from telethon import events

from senders import TextSender, VoidSender, MultiArgs
from manager import app

import asyncio



@TextSender(about='Get help about a command or list of all commands')
async def help(event, cmd=None):
    if cmd is not None:
        res = cmd + ': ' + app.commands[cmd].help()
    else:
        helplst = ['**' + cmd  + '**' + ': \n' + routine.help() + '\n' for cmd, routine in app.commands.items()]
        res = '\n'.join(helplst)
    
    return res

is_integer = lambda x: x.lstrip('-').isdigit()

async def __access_action(event, action: str, entity: str, cmd=None):
    if not is_integer(entity):
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

@TextSender(take_event=False)
async def concat(*args):
    return ''.join(args)

@TextSender(take_event=False)
async def idx(thing):
    return thing

@TextSender(take_event=False)
async def upper(txt):
    return txt.upper()


@TextSender(take_event=False, multiret=True)
async def split(txt):
    return txt.split()

@TextSender(take_event=False, multiret=True)
async def nstr(n, s):
    return [s] * int(n) 

@VoidSender('altyp')
async def always_typing(event, seconds):
    async with event.client.action(event.chat_id, 'typing'):
        await asyncio.sleep(int(seconds))

async def smsg(event, txt):
    await event.client.send_message(event.chat_id, txt)

@TextSender(on_event=events.MessageEdited)
async def edit(event):
    await smsg(event, "I saw what you did here")


@VoidSender()
async def nmsg(event, n, txt):
    n = int(n)
    if n > 15:
        await smsg(event, "**telepyth**: Am i a joke to u?")
    else:
        for i in range(n):
            await smsg(event, txt)
