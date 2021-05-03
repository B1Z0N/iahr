from telethon import events

import mimetypes, os

from iahr.reg import TextSender, VoidSender, MultiArgs, any_send
from iahr.config import IahrConfig
from iahr.commands.exception import IahrBuiltinCommandError
from iahr.utils import AccessList, EventService, async_wrap

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from .utils import local, create_gdrive_folder


##################################################
# Routines themselves
##################################################

# creates local webserver and auto handles authentication.
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
folder_id = create_gdrive_folder(drive, 'iahr_folder')

@async_wrap
def upload_to_gdrive(path):
    file = drive.CreateFile({
        'title' : os.path.basename(path),
        'mimeType' : mimetypes.guess_type(path)[0], 
        'parents': [{"kind": "drive#fileLink", "id": folder_id}]
    })
    file.SetContentFile(path)
    file.Upload()

    permission = file.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
    return file['alternateLink']

@TextSender(about=local['aboutopenonline'])
async def openonline(event):
    if (reply := await event.message.get_reply_message()) is not None:
        doc = await reply.download_media(file=IahrConfig.MEDIA_FOLDER)
        if (current := os.path.getsize(doc)/(1024*1024)) > \
            (maxsize := IahrConfig.CUSTOM.get('openonline_max_size_mb', 15)):
            raise IahrBuiltinCommandError('Too large file size({}), should be less than {}'.format(
                current, maxsize
            ))
        return await upload_to_gdrive(doc)
    
    raise IahrBuiltinCommandError('No reply in the event, can\'t deduce document.')
