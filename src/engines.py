import app
from telethon import TelegramClient, events, types

from senders import IncompatibleSendersError:
from app import CommandSyntaxError:
command_re = re.compile(r'\.[^\W]+.*')


async def msg_ngn(event: events.NewMessage):
    txt = event.message.raw_text
    if txt.startswith('.'):
        try:
            sender = app.exec(event.message.raw_text, event)
        except CommandSyntaxError:
            event.message.reply('Wrong command syntax')
        except IncompatibleSendersError:
            event.message.reply('This command are incompatible')
        else:
            sender.send()

async def reg(client):
    client.add_event_handler(
        msg_ngn,
        event=events.NewMessage(pattern=command_re)
    )


