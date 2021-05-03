from iahr.config import IahrConfig

from .default import default
from .chat import chat
from .audio import audio

if IahrConfig.CUSTOM.get('enable_gdrive', True):
    from .online_files import online_files
