import app
from telethon import TelegramClient, events, types

from senders import IncompatibleSendersError
from app import CommandSyntaxError, ActionData
from app import COMMAND_DELIMITER as delimiter, COMMAND_DELIMITER_ESCAPED as edelimiter

command_re = re.compile(r'{}[^\W]+.*'.format(edelimiter))

async def newmsg_ngn(event: events.NewMessage):
    txt = event.message.raw_text
    if txt.startswith('.'):
        cid = event.chat_id
        uid = event.message.user_id 
        try:
            sender = app.exec(event.message.raw_text, 
                                ActionData(event, cid, uid))
        except CommandSyntaxError:
            event.message.reply('Wrong command syntax')
        except IncompatibleSendersError:
            event.message.reply('This command are incompatible')
        else:
            sender.send()

async def reg(client):
    client.add_event_handler(
        newmsg_ngn,
        event=events.NewMessage(pattern=command_re)
    )

