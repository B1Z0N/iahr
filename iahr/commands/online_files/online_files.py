from telethon import events

import mimetypes, os

from iahr.reg import TextSender, VoidSender, MultiArgs, any_send
from iahr.config import IahrConfig
from iahr.commands.exception import IahrBuiltinCommandError, IahrCantDeduceDocumentError, IahrDocumentSizeTooLarge
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
        'title':
        os.path.basename(path),
        'mimeType':
        mimetypes.guess_type(path)[0],
        'parents': [{
            "kind": "drive#fileLink",
            "id": folder_id
        }]
    })
    file.SetContentFile(path)
    file.Upload()

    permission = file.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })
    return file['alternateLink']


@TextSender(about=local['aboutopenonline'])
async def openonline(event):
    if (reply := await event.message.get_reply_message()) is not None:
        IahrDocumentSizeTooLarge.check(reply.document.size,
                                       'openonline_max_size_mb', 15)

        doc = await reply.download_media(file=IahrConfig.MEDIA_FOLDER)
        return (await upload_to_gdrive(doc), os.remove(doc))[0]

    raise IahrCantDeduceDocumentError()
