import os
from datetime import datetime, timedelta
import asyncio
from telethon import TelegramClient, events, types, tl
import signal
from dotenv import load_dotenv
from pathlib import Path
from wand.image import Image

from utils import bordered

load_dotenv(verbose=True)

ME_ID = 343097987
OFFSET_2 = timedelta(hours=2)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PICUTRES_PATH = os.path.join(os.path.expanduser('~'), 'Pictures/')

client = TelegramClient('telethon_session_1', API_ID, API_HASH)
flip_stickers = True
frame_type = 'single'
stickers_map = {}


async def on_new_message_me(event: events.NewMessage):
    command, text = event.pattern_match.groups()
    msg: tl.custom.message.Message = event.message
    print(f'command: {command}')
    if command == 'stop_ai':
        await client.disconnect()
    if command == 'flip_stickers':
        global flip_stickers
        flip_stickers = not flip_stickers
        await msg.delete()
        await client.send_message(
            'me',
            'Now I%s flip stickers!' % ('' if flip_stickers else ' don\'t')
        )
    if command == 'toggle_frame':
        global frame_type
        frame_type = 'double' if frame_type == 'single' else 'single'
        await msg.delete()
        await client.send_message(
            'me',
            'Now using %s message frame' % frame_type
        )
    if not msg.entities and command == 'fr':
        framed = bordered(text, fr_type=frame_type)
        await msg.delete()
        await client.send_message(
            msg.chat_id,
            framed,
            parse_mode='html',
            link_preview='false',
            reply_to=msg.reply_to_msg_id
        )


async def on_new_message_other(event: events.NewMessage):
    msg: tl.custom.message.Message = event.message
    if msg.sticker and msg.sticker.mime_type.endswith('webp') and flip_stickers:
        global stickers_map
        temp_path = os.path.join(PICUTRES_PATH, 'tl.webp')
        await msg.download_media(file=temp_path)
        img = Image(filename=temp_path)
        img.flop()
        img.save(filename=temp_path)
        sent: tl.custom.Message = await msg.reply(file=temp_path)
        stickers_map[msg.id] = {'chat_id': sent.chat_id, 'message_id': sent.id}
        os.remove(temp_path)


async def on_message_delete(event: events.MessageDeleted):
    global stickers_map
    stickerids = [stickers_map[i]
                  for i in event.deleted_ids if stickers_map[i]]
    for info in stickerids:
        await client.delete_messages(info['chat_id'], info['message_id'])
    for _id in event.deleted_ids:
        del stickers_map[_id]
        


def terminate(sigNum, frame):
    print(f'\nGraceful shutdown...')
    # client.loop.stop
    # sys.exit(0)


# signal.signal(signal.SIGTERM, terminate)
# signal.signal(signal.SIGINT, terminate)


async def main():
    client.add_event_handler(
        on_new_message_me,
        event=events.NewMessage(
            pattern=r'\.(\w+)\s*(?:(.+))?',
            outgoing=True
        )
    )
    client.add_event_handler(
        on_new_message_other,
        event=events.NewMessage(
            incoming=True
        )
    )
    client.add_event_handler(
        on_message_delete,
        event=events.MessageDeleted()
    )
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
