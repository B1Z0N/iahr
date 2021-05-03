from telethon import events, tl

from pydub import AudioSegment

from iahr.config import IahrConfig
from iahr.reg.senders import ABCSender, any_send, create_sender
from iahr.commands.exception import IahrBuiltinCommandError
from iahr.utils import AccessList, EventService
from .localization import localization

from typing import Union, Mapping, Sequence
from dataclasses import dataclass
from functools import wraps

import traceback, tempfile


##################################################
# Constants
##################################################


AUDIO_TAG = 'audio'

local = localization[IahrConfig.LOCAL['lang']]


##################################################
# Utility
##################################################


class FileAudioSegment:
    def __init__(self, path):
        self.set_path(path)
        self.track = AudioSegment.from_file(self.path, format=self.pydub_extension)

    TELEGRAM_TO_PYDUB_FORMATS = {
        'mp3' : 'mp3',
        'oga' : 'ogg',
        'ogg' : 'ogg',
        'wav' : 'wav'
    }
    
    def set_path(self, path):
        self.path = path
        self.without_extension = ''.join(self.path.split('.')[:-1])
        self.tg_extension = self.path.split('.')[-1]
        self.pydub_extension = self.TELEGRAM_TO_PYDUB_FORMATS.get(self.tg_extension, self.tg_extension)

    def move(self, track):
        self.track = track
        return self


@create_sender
class AudioSender(ABCSender):

    async def send(self):
        IahrConfig.LOGGER.info(f'sending audio:{self.res}')
        
        audiof = self.res.get()
        outfile = audiof.track.export(
            f'{audiof.without_extension}.edited.{audiof.tg_extension}', 
            format=audiof.pydub_extension
        )
        cid = await EventService.chatid_from(self.event)
        await self.event.client.send_file(cid, outfile, reply_to=self.event.message, voice_note=True)

    async def invoke(self, *args, **kwargs):
        if len(args) >= 1 and isinstance(args[0], FileAudioSegment):
            audiof = args[0]
            self.res = audiof.move(await self.fun(*args, **kwargs))
        elif (reply := await self.event.message.get_reply_message()) is not None:
            audio = reply.document

            if audio.mime_type.split('/')[0] != 'audio':
                raise IahrBuiltinCommandError(f'Not an audio format: {typ}.')
            
            audiof = FileAudioSegment(await reply.download_media(file=IahrConfig.MEDIA_FOLDER))
            self.res = audiof.move(await self.fun(audiof, *args, **kwargs))
        else:
            self.res = await self.fun(*arsg, **kwargs)
            # raise IahrBuiltinCommandError('No voice and no audio file found in the event.')


def get_ms(t: str) -> int:
    if t.endswith('ms'):
        return int(t[:-2])
    elif t.endswith('s'):
        return int(t[:-1]) * 1000
    else:
        return int(t)