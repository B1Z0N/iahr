from telethon import TelegramClient, events, types

from manager import CommandSyntaxError, IncompatibleSendersError, PermissionsError
from manager import COMMAND_DELIMITER as delimiter, COMMAND_DELIMITER_ESCAPED as edelimiter
from manager import app, ActionData
from utils import AccessList

import re

command_re = re.compile(r'{}[^\W]+.*'.format(edelimiter))

async def check_me(client):
    me = await client.get_me()
    myid = me.id
    def check(eid):
        return AccessList.ME if eid == myid else eid
    return check

async def newmsg_ngn(event: events.NewMessage):
    txt = event.message.raw_text
    me = await check_me(event.client)
    import traceback

    if txt.startswith(delimiter):
        cid = me(event.chat_id)
        uid = me(event.message.from_id)
        try:
            sender = await app.exec(txt, 
                                ActionData(event, uid, cid))
        except CommandSyntaxError:
            await event.reply('Wrong command syntax')
        except IncompatibleSendersError:
            await event.reply('This commands are incompatible')
        except PermissionsError:
            await event.reply("You can't use this command now")
        except Exception as e:
            traceback.print_exc()
        else:
            try:
                await sender.send()
            except Exception:
                traceback.print_exc()

async def reg(client):
    client.add_event_handler(
        newmsg_ngn,
        event=events.NewMessage(pattern=command_re)
    )

