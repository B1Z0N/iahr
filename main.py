import os
import re
import sys
from datetime import datetime, timedelta
import asyncio
from telethon import TelegramClient, events, types, tl, Button
import signal
from dotenv import load_dotenv
from pathlib import Path
from wand.image import Image

from utils import bordered, to_staro_slav, is_cyrrillic
from init_client import make_client

PICUTRES_PATH = os.path.join(os.path.expanduser('~'), 'Pictures/')
HELP_TEXT = '''
.fr <text> - send framed text
.toggle_frame - toggle frame type
.flip_stickers - toggle stickers flipping
.toggle_dot - if do append dot to the messages
.status - display status
.help - display this message
'''

client: TelegramClient = None
flip_stickers = False
append_dot = False
frame_type = 'single'
stickers_map = {}


async def on_new_message_me(event: events.NewMessage):
    command: str; text: str
    command, text = event.pattern_match.groups()
    msg: tl.custom.message.Message = event.message
    print(f'command: {command}')

    if command == 'stop_ai':
        await msg.delete()
        await client.send_message(
            'me',
            'AI server stopped...'
        )
        await handle_exit()

    elif command == 'get_msg':
        (entity_like, cnt) = re.match(r'(\w+)(?:\s+)?(?:(\d+))?', text).groups()
        cnt = int(cnt) if cnt else 5
        try:
            entity = await client.get_entity(entity_like)
        except ValueError as _:
            await client.send_message('me', 'User not found.')
        else:
            msgs = await client.get_messages(entity, limit=cnt)
            msgs.reverse()
            await client.forward_messages('me', msgs)

    elif command == 'flip_stickers':
        global flip_stickers
        flip_stickers = not flip_stickers
        await msg.delete()
        await client.send_message(
            'me',
            'Now I{} flip stickers!'.format(
                '' if flip_stickers else ' don\'t'
            )
        )

    elif command == 'toggle_frame':
        global frame_type
        frame_type = 'double' if frame_type == 'single' else 'single'
        await msg.delete()
        await client.send_message(
            'me',
            'Now using {} message frame'.format(frame_type)
        )

    elif command == 'toggle_dot':
        global append_dot
        append_dot = not append_dot
        await client.send_message(
            'me',
            'Now I{} append dot to the end!'.format(
                '' if append_dot else ' don\'t'
            )
        )

    elif not msg.entities and command == 'fr':
        framed = bordered(text, fr_type=frame_type)
        await msg.delete()
        await client.send_message(
            msg.chat_id,
            framed,
            parse_mode='html',
            link_preview='false',
            reply_to=msg.reply_to_msg_id
        )

    elif command in ('st', 'ст'):
        await msg.delete()
        _text = to_staro_slav(text) if is_cyrrillic(text) else text
        await msg.respond(_text, reply_to=msg.reply_to_msg_id)

    elif command == 'status':
        text = '\n'.join([
            f'Flipping stickers: {flip_stickers}',
            f'Frame type: {frame_type}',
            f'Appending dot: {append_dot}',

        ])
        await client.send_message(
            'me',
            f'<code>{text}</code>',
            reply_to=msg.id,
            parse_mode='HTML'
        )

    elif command == 'help':
        await client.send_message('me', HELP_TEXT, reply_to=msg.id)

    if not command and append_dot and text[-1].isalpha():
        await msg.delete()
        await msg.respond(
            text + '.',
            reply_to=msg.reply_to_msg_id
        )


async def on_new_message_other(event: events.NewMessage):
    msg: tl.custom.message.Message = event.message
    if (
        not msg.is_private and
        msg.sticker and
        msg.sticker.mime_type.endswith('webp') and
        flip_stickers
    ):
        global stickers_map
        temp_path = os.path.join(PICUTRES_PATH, 'tl.webp')
        await msg.download_media(file=temp_path)
        img = Image(filename=temp_path)
        img.flop()
        img.save(filename=temp_path)
        sent: tl.custom.Message = await msg.reply(file=temp_path)
        stickers_map[msg.id] = (sent.chat_id, sent.id)
        os.remove(temp_path)


async def on_message_delete(event: events.MessageDeleted):
    global stickers_map
    stickerids = [i for i in event.deleted_ids if i in stickers_map]
    for _id in stickerids:
        chat_id, msg_id = stickers_map[_id]
        await client.delete_messages(chat_id, msg_id)
        del stickers_map[_id]


def terminate(sigNum, frame):
    print(f'\nStarting graceful shutdown...')
    # _loop = client.loop
    asyncio.ensure_future(
        client.disconnect(),
        loop=client.loop
    ).add_done_callback(
        lambda _: print('Disconnected.')
    )


async def handle_exit():
    await client.disconnect()

# signal.signal(signal.SIGTERM, terminate)
# signal.signal(signal.SIGINT, terminate)


async def main():
    client.add_event_handler(
        on_new_message_me,
        event=events.NewMessage(
            pattern=r'(?:\.(\w+))?\s*(?:(.+))?',
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
    load_dotenv()
    client = make_client()
    loop = client.loop
    loop.run_until_complete(main())
    loop.close()
