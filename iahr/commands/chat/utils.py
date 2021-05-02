from telethon import events, tl

from iahr.config import IahrConfig
from iahr.commands.chat.localization import localization
from iahr.utils import AccessList, EventService

from typing import Union, Mapping, Sequence

import traceback


##################################################
# Constants
##################################################


CHAT_TAG = 'chat'

local = localization[IahrConfig.LOCAL['lang']]


##################################################
# Utility functions
##################################################


def mention(user: tl.types.User, with_link=False):
    if user.username:
        return f'@{user.username}'
    name = user.first_name
    if user.last_name:
        name += ' ' + user.last_name
    if with_link:
        return f'<a href="tg://user?id={user.id}">{name}</a>'
    return name
