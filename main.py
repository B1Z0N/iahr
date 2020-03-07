import os
import re
import sys
import subprocess
import urllib.parse as url
import asyncio
from typing import List
# import signal
import requests
from telethon import TelegramClient, events, types, tl, Button, client
from dotenv import load_dotenv
from wand.image import Image

from utils import bordered, to_staro_slav, is_cyrrillic, mention
from init_client import make_client

PICUTRES_PATH = os.path.join(os.path.expanduser('~'), 'Pictures/')
HELP_TEXT = '''
.fr <text> - send framed text
.flip_stickers - toggle stickers flipping
.flip - flip sticker to which reply message is
.toggle_frame - toggle frame type
.toggle_dot - if do append dot to the messages
.toggle_tagall - toggle tagging
.status - display status
.help - display this message
.[st|ст] <text> - staroslav text
'''
VOICE_API_URL: str
TAG_ALL_LIMIT = 50

client: TelegramClient = None
flip_stickers = False
append_dot = False
frame_type = 'single'
stickers_map = {}
allow_tag_all = True


async def flip_sticker(msg: tl.custom.message.Message):
    global stickers_map
    temp_path = 'tl.webp'
    await msg.download_media(file=temp_path)

    img = Image(filename=temp_path)
    img.flop()
    img.save(filename=temp_path)

    sent: tl.custom.Message = await msg.reply(file=temp_path)
    stickers_map[msg.id] = (sent.chat_id, sent.id)
    os.remove(temp_path)


async def on_new_message_me(event: events.NewMessage):
    global allow_tag_all
    global flip_stickers
    global frame_type
    global append_dot

    command: str
    text: str
    command, text = event.pattern_match.groups()
    msg: tl.custom.message.Message = event.message

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
        flip_stickers = not flip_stickers
        await msg.delete()
        await client.send_message(
            'me',
            'Now I{} flip stickers!'.format(
                '' if flip_stickers else ' don\'t'
            )
        )

    elif command == 'toggle_frame':
        frame_type = 'double' if frame_type == 'single' else 'single'
        await msg.delete()
        await client.send_message(
            'me',
            'Now using {} message frame'.format(frame_type)
        )

    elif command == 'toggle_dot':
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
            parse_mode='HTML',
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
            f'Allow tag all: {allow_tag_all}'
        ])
        await client.send_message(
            'me',
            f'<code>{text}</code>',
            reply_to=msg.id,
            parse_mode='HTML'
        )

    elif command == 'help':
        await client.send_message('me', HELP_TEXT, reply_to=msg.id)

    elif command in ('say', 'сей', 'гл'):
        await msg.delete()
        wav_name = 'temp__.wav'
        temp_name = 'temp__.ogg'

        # May be broken due to API changes!
        try:
            resp = requests.get(
                f'{VOICE_API_URL}/say',
                params={'q': url.quote(text)},
                timeout=5
            )
        except requests.exceptions.Timeout as e:
            await client.send_message(
                'me',
                'Timeout making voice API request'
            )
            return
        open(wav_name, 'wb').write(resp.content)

        subprocess.run(
            [
                'ffmpeg',
                '-i',
                wav_name,
                '-acodec',
                'libopus',
                temp_name,
                '-y'
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        await client.send_file(
            msg.chat_id,
            temp_name,
            voice_note=True,
            reply_to=msg.reply_to_msg_id
        )
        os.unlink(temp_name)
        os.unlink(wav_name)

    elif command == 'flip':
        target: tl.custom.Message = await msg.get_reply_message()
        if (target and target.sticker):
            target.sticker
            await msg.delete()
            await flip_sticker(target)

    if command == 'toggle_tagall':
        await msg.delete()
        allow_tag_all = not allow_tag_all
        await client.send_message(
            'me',
            'Now I{} allow tagging all participants'.format(
                '' if allow_tag_all else ' don\'t'
            )
        )

    if command == 'chat_id':
        await msg.delete()
        await client.send_message(
            'me',
            f'{msg.chat.title}: <code>{msg.chat_id}</code>',
            parse_mode='HTML'
        )

    if command == 'user_id':
        await msg.delete()
        users = await client.get_participants(msg.chat_id, search=text, limit=20)
        await client.send_message(
            'me',
            '\n'.join(f'{mention(u)}: <code>{u.id}</code>' for u in users),
            parse_mode='HTML'
        )

    if not command and append_dot and text[-1].isalpha():
        await msg.delete()
        await msg.respond(
            text[0].upper() + text[1:] + '.',
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
        await flip_sticker(msg)


async def on_new_message_all(event: events.NewMessage):
    command: str
    text: str
    command, text = event.pattern_match.groups()
    msg: tl.custom.message.Message = event.message
    if command == 'tagall' and allow_tag_all:
        users = await client.get_participants(msg.chat_id)
        if len(users) > TAG_ALL_LIMIT:
            return
        u: tl.types.User = {}
        msg_str = ' '.join(
            mention(u)
            for u in users
            if not u.bot and not u.is_self
        )
        sent = await msg.respond(msg_str, parse_mode='HTML')
        stickers_map[msg.id] = (sent.chat_id, sent.id)


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
    command_re = re.compile(r'(?:\.(\w+))?\s*(?:(.+))?', re.DOTALL)
    client.add_event_handler(
        on_new_message_me,
        event=events.NewMessage(pattern=command_re, outgoing=True)
    )
    client.add_event_handler(
        on_new_message_all,
        event=events.NewMessage(pattern=command_re)
    )
    client.add_event_handler(
        on_new_message_other,
        event=events.NewMessage(incoming=True)
    )
    client.add_event_handler(
        on_message_delete,
        event=events.MessageDeleted()
    )
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    load_dotenv()

    VOICE_API_URL = os.getenv('VOICEAPI_URL')
    client = make_client()
    loop = client.loop
    loop.run_until_complete(main())
    loop.close()
