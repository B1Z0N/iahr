from telethon import events, tl

from pydub import AudioSegment

from iahr.config import IahrConfig
from iahr.commands.exception import IahrBuiltinCommandError
from iahr.utils import AccessList, EventService
from .localization import localization

from typing import Union, Mapping, Sequence
from functools import wraps

import traceback, tempfile


##################################################
# Constants
##################################################


AUDIO_TAG = 'audio'

local = localization[IahrConfig.LOCAL['lang']]


##################################################
# Utility functions
##################################################


def audio_specific(fun):
    @wraps(fun)
    async def _(event, *args, **kwargs):
        if (reply := await event.message.get_reply_message()) is not None:
            audio = reply.document
            if audio.mime_type is None:
                raise IahrBuiltinCommandError('No audio format.')

            typ, ext = audio.mime_type.split('/')
            if typ != 'audio':
                raise IahrBuiltinCommandError(f'Not an audio format: {typ}.')
            
            file = tempfile.NamedTemporaryFile(mode='w+b')
            file.write(audio.file_reference)

            name_attribute = next(filter(lambda x: isinstance(x, tl.types.DocumentAttributeFilename), audio.attributes))
            ext = name_attribute.file_name.split('.')[-1]
            return fun(
                AudioSegment.from_file(file.name, format=ext),
                *args, **kwargs
            )

        raise IahrBuiltinCommandError('No voice and no audio file found in the event.')

    return _