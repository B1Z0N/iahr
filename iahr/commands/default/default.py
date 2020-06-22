from telethon import events

from iahr.reg import TextSender, VoidSender, MultiArgs
from iahr.config import IahrConfig
from .utils import local, DEFAULT_TAG, ADMIN_TAG
from .utils import usr_from_event, chat_from_event, commands_access_action, \
    handlers_access_action, tags_access_action, process_list, ignore_action

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
        res = '**{}**:\n{}\n'\
            .format(cmd, local['nosuchcmd'] if val is None else val.help())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res


@TextSender(about=local['abouthandlers'], tags={DEFAULT_TAG})
async def handlers(event, etype=None, hndl=None):
    app = IahrConfig.APP

    if etype is None and hndl is not None:
        return local['handlers']['wrongordering']
    
    def for_etype(etype_name):
        handlers = app.handlers[etype_name]
        res = f'**{IahrConfig.PREFIXES[getattr(events, etype_name)]}**' + ':\n'
        for name in handlers.keys():
            res += f'  `{name}`'

        return res

    if hndl is None:
        if etype is None:
            return '\n'.join(map(for_etype, app.handlers.keys()))
        else:
            res, status = get_reverse_etype(etype)
            return for_etype(res) if status else res

    hndls, helplst = process_list(hndl), [ f'`{etype}`' + ':\n']
    res, status = get_reverse_etype(etype)
    if not status:
        return res
    dct = app.handlers[res]

    for hndl in hndls:
        val = dct.get(hndl)
        res = '\t**{}**:\n{}\n'\
            .format(hndl, '\n    ' + local['handlers']['nosuchhndl'] if val is None else val.help())
        helplst.append(res)

    res = '\n'.join(helplst)
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
            res += local['nosuchtag'].format(tag)
        else:
            res += '\n'.join(f'    **{cmd}**' for cmd in val.keys())
        helplst.append(res)

    res = '\n'.join(helplst)
    return res


@VoidSender('errignore', about=local['aboutignore'], tags={DEFAULT_TAG, ADMIN_TAG})
async def ignore_chat(event, chat):
    await ignore_action(event, chat, 'ignore_chat')


@VoidSender('errverbose', about=local['aboutverbose'], tags={DEFAULT_TAG, ADMIN_TAG})
async def unignore_chat(event, chat):
    await ignore_action(event, chat, 'verbose_chat')


@TextSender(take_event=False, about=local['aboutsynhelp'], tags={DEFAULT_TAG})
async def synhelp():
    cfg = IahrConfig

    return local['synhelp'].format(
        new_msg=cfg.CMD.original, left=cfg.LEFT.original,
        right=cfg.RIGHT.original, raw=cfg.RAW.original
    )


async def generic_access_action(
    event, action, action_type,
    ent, *args, **kwargs
):
    if ent == IahrConfig.CUSTOM['current_entity']:
        if action.endswith('chat'):
            ent = await chat_from_event(event)
        elif action.endswith('usr'):
            ent = await usr_from_event(event)

    if action_type == 'commands':
        await commands_access_action(event, action, ent, *args, **kwargs)
    elif action_type == 'handlers':
        await handlers_access_action(event, action, ent, *args, **kwargs)
    elif action_type == 'tags':
        await tags_access_action(event, action, ent, *args, **kwargs)
    else:
        await event.message.reply(local['unknownactiontype'].format(action_type))


@VoidSender('allowchat', about=local['aboutallowchat'], tags={DEFAULT_TAG, ADMIN_TAG})
async def allowchat(event, act_t, chat, *args, admintoo='False', **kwargs):
    await generic_access_action(
        event, 'allow_chat', act_t, chat, *args, admintoo=bool(admintoo), **kwargs
    )


@VoidSender('banchat', about=local['aboutbanchat'], tags={DEFAULT_TAG, ADMIN_TAG})
async def banchat(event, act_t, chat, *args, admintoo='False', **kwargs):
    await generic_access_action(
        event, 'ban_chat', act_t, chat, *args, admintoo=bool(admintoo), **kwargs
    )


@VoidSender('allowusr', about=local['aboutallowusr'], tags={DEFAULT_TAG, ADMIN_TAG})
async def allowusr(event, act_t, usr, *args, admintoo='False', **kwargs):
    await generic_access_action(
        event, 'allow_usr', act_t, usr, *args, admintoo=bool(admintoo), **kwargs
    )


@VoidSender('banusr', about=local['aboutbanusr'], tags={DEFAULT_TAG, ADMIN_TAG})
async def banusr(event, act_t, usr, *args, admintoo='False', **kwargs):
    await generic_access_action(
        event, 'ban_usr', act_t, usr, *args, admintoo=bool(admintoo), **kwargs
    )   
        
