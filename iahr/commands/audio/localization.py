# localization for default routines
from iahr.config import IahrConfig

localization = {}

##################################################
# English
##################################################

localization['english'] = {
    'aboutcrop': """
    Crop an  audio track.

    Example:

    `.audiocrop 2s 5s`
        
    the same

    `.audiocrop 2000 5000`
""",
    'aboutreverse': """
    Reverse an audio track
""",
    'aboutdistort': """
    Distort an audio track
""",
    'aboutspeak': """
    Text to voice
""",
    'notanaudio': """
    Not an audio format, but "{}"
"""
}

##################################################
# Russian
##################################################

localization['russian'] = {
    'aboutcrop': """
    Обрезать аудио

    Например:

    `.audiocrop 2s 5s`
        
    то же самое

    `.audiocrop 2000 5000`
""",
    'aboutreverse': """
    Аудио в обратном порядке
""",
    'aboutdistort': """
    Добавить шума в аудио
""",
    'aboutspeak': """
    Текст в голос
""",
    'notanaudio': """
    Документ не в аудио формате, а "{}"
"""
}
