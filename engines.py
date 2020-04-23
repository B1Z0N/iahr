from telethon import TelegramClient, events, types

from manager import CommandSyntaxError, PermissionsError, \
        ExecutionError, NonExistantCommandError
from manager import COMMAND_DELIMITER as delimiter, COMMAND_DELIMITER_ESCAPED as edelimiter
from manager import app, ActionData
from register import reg

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
    print(txt)
    if txt.startswith(delimiter):
        cid = me(event.chat_id)
        uid = me(event.message.from_id)
        try:
            sender = await app.exec(
                txt, ActionData(event, uid, cid)
            )
        except (CommandSyntaxError, PermissionsError, NonExistantCommandError) as e:
            await event.reply(str(e))
        except ExecutionError as e:
            print(str(e))
            await event.reply(
                'Incompatible commands, wrong arguments or just a buggy function'
            )
        except Exception as e:
            traceback.print_exc()
        else:
            await sender.send()


async def init(client):
    reg.init(client)    
    client.add_event_handler(
        newmsg_ngn,
        event=events.NewMessage(pattern=command_re)
    )

