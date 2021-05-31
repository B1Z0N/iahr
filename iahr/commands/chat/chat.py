from telethon import events

from iahr.reg import TextSender, VoidSender, MultiArgs, any_send
from iahr.config import IahrConfig
from iahr.utils import AccessList, EventService

from .utils import mention, local, CHAT_TAG

##################################################
# Routines themselves
##################################################


@VoidSender(about=local['tagall']['about'], tags={CHAT_TAG})
async def tagall(event):
    cid = await EventService.chatid_from(event)
    users = await event.client.get_participants(cid)

    max_users = int(IahrConfig.CUSTOM.get('tagall_max_number', 50))
    if len(users) > max_users:
        await any_send(event, local['tagall']['toomuch'].format(max_users))
    else:
        await any_send(event,
                       ' '.join(
                           EventService.mention(u, with_link=True)
                           for u in users if not u.bot and not u.is_self),
                       parse_mode='html')
