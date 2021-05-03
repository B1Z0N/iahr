from telethon import events, tl

from iahr.config import IahrConfig
from iahr.utils import AccessList, EventService
from .localization import localization

from typing import Union, Mapping, Sequence

import traceback


##################################################
# Constants
##################################################

local = localization[IahrConfig.LOCAL['lang']]

##################################################
# Utility functions
##################################################


def create_gdrive_folder(drive, folder_name):
    folders = (drive.ListFile  ({'q': "mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList())

    titles =  [x['title'] for x in folders]
    if folder_name in titles:
        for item in folders:
            if item['title'] == folder_name:
                return item['id']
  
    file_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file0 = drive.CreateFile(file_metadata)
    file0.Upload()
    return file0['id']

TELEGRAM_TO_GOOGLE_FORMATS = {
    'doc'
}
