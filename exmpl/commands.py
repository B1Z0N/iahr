from iahr.reg import TextSender, VoidSender
from telethon import events


@VoidSender(name='isaw', about='Notifies when someone edits the message', on_event=events.MessageEdited)
async def isaw(event):
    await event.message.reply("I saw what you did here, you bastard!")

@TextSender()
async def concat(_, *args):
    return ''.join(args)

@TextSender()
async def idx(_, s):
    return s

@TextSender(multiret=True)
async def split(_, s):
    return s.split()
