from telethon import events

from iahr.reg import TextSender, VoidSender, MultiArgs
from iahr.config import IahrConfig
from iahr.utils import AccessList, EventService, ParseModeSetter

from .utils import mention, local, CHATRELATED_TAG

##################################################
# Routines themselves
##################################################


@VoidSender(about=local['tagall']['about'], tags={CHATRELATED_TAG})
async def tagall(event):
    cid = await EventService.chatid_from(event)
    users = await event.client.get_participants(cid)

    max_users = int(IahrConfig.CUSTOM.get('tagall_max_number', 50))
    if len(users) > max_users:
        await event.message.reply(local['tagall']['toomuch'].format(max_users))
        return 

    with ParseModeSetter(event, 'html') as html_event:
        await html_event.message.reply(' '.join([mention(u, with_link=True) for u in users if not u.bot and not u.is_self]))
