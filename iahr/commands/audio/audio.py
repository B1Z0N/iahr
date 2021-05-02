from telethon import events

from pydub import AudioSegment

from iahr.reg import MultiArgs, MediaSender
from iahr.config import IahrConfig
from iahr.utils import AccessList, EventService

from .utils import local, AUDIO_TAG, audio_specific


##################################################
# Routines themselves
##################################################


# @MediaSender(about=local['aboutcrop'], tags={AUDIO_TAG}, name='audiocrop')
# @audio_specific
# async def crop(track: AudioSegment, start, stop):
#     pass


@MediaSender(about=local['aboutreverse'], tags={AUDIO_TAG}, name='audioreverse')
@audio_specific
async def reverse(track: AudioSegment):
    return track.reverse()

# @MediaSender(about=local['distort'], tags={AUDIO_TAG}, name='audiodistort')
# async def distort(event, track):
#     pass