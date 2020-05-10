from iahr.reg import TextSender, VoidSender
from telethon import events


@VoidSender(name='isaw',
            on_event=events.MessageEdited,
            about="""
    Notifies when someone edits the message
""")
async def isaw(event):
    await event.message.reply("I saw what you did here, you bastard!")


@TextSender(about="""
    Concatenate unlimited number of args
""")
async def concat(_, *args):
    return ''.join(str(arg) for arg in args)


@TextSender(about="""
    Return single argument passed
""", take_event=False)
async def idx(s):
    return s


@TextSender(multiret=True,
            about="""
    Split string with spaces, return list
""")
async def split(_, s):
    return s.split()


@TextSender(multiret=True,
            about="""
    Return list of two args
        
        `.kwtest 1 2`

        `.kwtest arg1=1 arg2=2`

        `.kwtest r[arg2=arg.[[]]r 1`
""")
async def kwtest(_, arg1, arg2):
    return arg1, arg2


@TextSender(about="""

""", on_event=events.NewMessage)
async def directly_on_new_message(event):
    return 'directly_on_new_message'
    