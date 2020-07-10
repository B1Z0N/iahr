from telethon import events

from iahr.reg import TextSender, VoidSender, MultiArgs
from iahr.config import IahrConfig
from .utils import *

##################################################
# Routines themselves
##################################################


@TextSender(about=local['abouthelp'], take_event=False, tags={DEFAULT_TAG})
async def help():
    return local['help'].format(new_msg=IahrConfig.CMD.original)


@TextSender(about=local['aboutcommands'], tags={DEFAULT_TAG})
async def commands(event, cmd=None):
    app = IahrConfig.APP

    if cmd is None:
        return '\n'.join(f'**{cmd}**' for cmd in app.commands.keys())

    cmds, helplst = process_list(cmd, is_cmds=True), []
    for cmd in cmds:
        val = app.commands.get(cmd)
        res = '**{}**:\n{}\n'.format(
            cmd, local['nosuchcmd'] if val is None else val.help())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res


@TextSender(about=local['abouthandlers'], tags={DEFAULT_TAG})
async def handlers(event, prefix=None, hndl=None):
    app = IahrConfig.APP
    nosuchhndl = local['handlers']['nosuchhndl']
    nosuchtype = local['handlers']['nosuchtype']

    if prefix is None and hndl is not None:
        return local['handlers']['wrongordering']

    if hndl is None:
        if prefix is None:
            dct = {
                prefix: hndls.keys()
                for prefix, hndls in app.handlers.items()
            }
        else:
            dct = app.handlers.get(prefix)
            if dct is None:
                return nosuchtype.format(etype=prefix)
            dct = {prefix: dct.keys()}
    else:  # hndl is not None and prefix is not None
        dct = app.handlers.get(prefix)
        if dct is None:
            return nosuchtype.format(etype=prefix)
        dct = {
            prefix: [(hndl, None)[dct.get(hndl) is None]
                     for hndl in process_list(hndl)]
        }

    res = ''
    for prefix, names in dct.items():
        res += f'**{prefix}**\n'
        res += '\n\t' if names else ''
        res += '\n    '.join(
            nosuchhndl.format(name) if name is None else f'`{name}`'
            for name in names)
        res += '\n\n'

    return res


@TextSender(about=local['abouttags'], tags={DEFAULT_TAG})
async def tags(event, tag=None):
    app = IahrConfig.APP

    if tag is None:
        return '\n'.join(f'**{tag}**' for tag in app.tags.keys())

    tags, helplst = process_list(tag), []
    for tag in tags:
        val = app.tags.get(tag)
        res = f'**{tag}**:\n'
        if val is None:
            res += local['nosuchtag'].format(tag=tag)
        else:
            res += '\n'.join(f'    **{cmd}**' for cmd in val.keys())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res


@VoidSender('errignore',
            about=local['aboutignore'],
            tags={DEFAULT_TAG, ADMIN_TAG})
async def ignore_chat(event, chat):
    await ignore_action(event, chat, 'ignore_chat')


@VoidSender('errverbose',
            about=local['aboutverbose'],
            tags={DEFAULT_TAG, ADMIN_TAG})
async def unignore_chat(event, chat):
    await ignore_action(event, chat, 'verbose_chat')


@TextSender(take_event=False, about=local['aboutsynhelp'], tags={DEFAULT_TAG})
async def synhelp():
    cfg = IahrConfig

    return local['synhelp'].format(new_msg=cfg.CMD.original,
                                   left=cfg.LEFT.original,
                                   right=cfg.RIGHT.original,
                                   raw=cfg.RAW.original)


@TextSender(take_event=False,
            about=local['aboutaccesshelp'],
            tags={DEFAULT_TAG})
async def accesshelp():
    cfg = IahrConfig

    return local['accesshelp'].format(new_msg=cfg.CMD.original,
                                      left=cfg.LEFT.original,
                                      right=cfg.RIGHT.original,
                                      raw=cfg.RAW.original,
                                      current=cfg.CUSTOM['current_entity'])


@VoidSender('allowchat',
            about=local['seeaccesshelp'],
            tags={DEFAULT_TAG, ADMIN_TAG})
async def allowchat(event, act_t, chat, *args, admintoo='False', **kwargs):
    res = await generic_access_action(event,
                                      'allow_chat',
                                      act_t,
                                      chat,
                                      *args,
                                      admintoo=to_bool(admintoo),
                                      **kwargs)

    if type(res) is str:
        await event.message.reply(res)


@VoidSender('banchat',
            about=local['seeaccesshelp'],
            tags={DEFAULT_TAG, ADMIN_TAG})
async def banchat(event, act_t, chat, *args, admintoo='False', **kwargs):
    res = await generic_access_action(event,
                                      'ban_chat',
                                      act_t,
                                      chat,
                                      *args,
                                      admintoo=to_bool(admintoo),
                                      **kwargs)

    if type(res) is str:
        await event.message.reply(res)


@VoidSender('allowusr',
            about=local['seeaccesshelp'],
            tags={DEFAULT_TAG, ADMIN_TAG})
async def allowusr(event, act_t, usr, *args, admintoo='False', **kwargs):
    res = await generic_access_action(event,
                                      'allow_usr',
                                      act_t,
                                      usr,
                                      *args,
                                      admintoo=to_bool(admintoo),
                                      **kwargs)

    if type(res) is str:
        await event.message.reply(res)


@VoidSender('banusr',
            about=local['seeaccesshelp'],
            tags={DEFAULT_TAG, ADMIN_TAG})
async def banusr(event, act_t, usr, *args, admintoo='False', **kwargs):
    res = await generic_access_action(event,
                                      'ban_usr',
                                      act_t,
                                      usr,
                                      *args,
                                      admintoo=to_bool(admintoo),
                                      **kwargs)

    if type(res) is str:
        await event.message.reply(res)


@TextSender('allowedusr', about=local['seeaccesshelp'], tags={DEFAULT_TAG})
async def allowedusr(event, act_t, usr, *args, **kwargs):
    res = await generic_access_action(event,
                                      'is_allowed_usr',
                                      act_t,
                                      usr,
                                      *args,
                                      admintoo=True,
                                      **kwargs)

    if type(res) is str:
        return res

    return await perm_format(event, res)


@TextSender('allowedchat', about=local['seeaccesshelp'], tags={DEFAULT_TAG})
async def allowedchat(event, act_t, chat, *args, **kwargs):
    res = await generic_access_action(event,
                                      'is_allowed_chat',
                                      act_t,
                                      chat,
                                      *args,
                                      admintoo=True,
                                      **kwargs)

    if type(res) is str:
        return res

    return await perm_format(event, res)
