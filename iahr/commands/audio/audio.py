from telethon import events

from pydub import AudioSegment
from pydub.generators import WhiteNoise

from iahr.reg import MultiArgs, MediaSender
from iahr.config import IahrConfig
from iahr.utils import AccessList, EventService

from .utils import local, AUDIO_TAG, AudioSender, FileAudioSegment, get_ms

##################################################
# Routines themselves
##################################################


@AudioSender(about=local['aboutcrop'], tags={AUDIO_TAG}, name='audiocrop')
async def crop(audiof: FileAudioSegment, start, stop):
    start, stop = get_ms(start), get_ms(stop)
    return audiof.track[start:stop]


@AudioSender(about=local['aboutreverse'],
             tags={AUDIO_TAG},
             name='audioreverse')
async def reverse(audiof: FileAudioSegment):
    return audiof.track.reverse()


@AudioSender(about=local['aboutdistort'],
             tags={AUDIO_TAG},
             name='audiodistort')
async def distort(audiof: FileAudioSegment):
    noise = WhiteNoise().to_audio_segment(duration=len(audiof.track))
    return audiof.track.overlay(noise)


@AudioSender(about=local['aboutspeak'], tags={AUDIO_TAG}, name='speak')
async def speak(txt: str):
    pass
