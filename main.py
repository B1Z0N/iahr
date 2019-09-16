#!/usr/bin/python3
import sys
import re
import asyncio
from threading import Timer
from datetime import datetime, timedelta
import asyncio
from telethon import TelegramClient, events
import signal

from border_msg import bordered
from appconfig import load_config

ME_ID = 343097987
OFFSET_2 = timedelta(hours=2)

cfg = load_config()
client = TelegramClient('telethon_session_1', cfg['api_id'], cfg['api_hash'])


async def delaysendto(secs, userstr, msgstr):
    await asyncio.sleep(secs)
    await client.send_message(userstr, msgstr)


@client.on(events.NewMessage)
async def new_msg_evt(event):
    msg = event.message
    if (msg.entities == None and msg.out and len(msg.message) > 0):

        if (msg.message.startswith('.fr')):
            framed = bordered(re.sub('^.fr *', '', msg.message))
            await client.edit_message(event.to_id,
                                      message=msg.id,
                                      text=framed,
                                      link_preview=False,
                                      parse_mode='html')
    if (msg.message.startswith('.t') and msg.to_id.user_id == ME_ID):
        _match = re.match(r'^\.t ([.\d]+ [:\d]+) *\[(.+)\] *(.+)',
                          msg.message)
        if (_match != None):
            _time = datetime.strptime(_match.group(1), '%d.%m.%y %H:%M:%S')
            secs = (_time - datetime.now() - OFFSET_2).total_seconds()
            print('remaining seconds:', secs, 'msg:', _match.group(3))
            await delaysendto(secs, _match.group(2), _match.group(3))

def terminate(sigNum, frame):
    print(f'\nGraceful shutdown...')
    client.loop.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, terminate)
signal.signal(signal.SIGINT, terminate)

async def main():
    await client.start()
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
