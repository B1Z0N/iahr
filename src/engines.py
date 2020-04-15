import app
from telethon import TelegramClient, events, types

command_re = re.compile(r'\.[^\W]+.*')


async def msg_ngn(event: events.NewMessage):
    app.exec(event.message.raw_text, event)


async def reg(client):
    client.add_event_handler(
        msg_ngn,
        event=events.NewMessage(pattern=command_re)
    )


