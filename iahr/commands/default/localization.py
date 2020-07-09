# localization for default routines
from iahr.config import IahrConfig

localization = {}

##################################################
# English
##################################################

localization['english'] = {
    'nosuchcmd':
    """
    No such command(try checking full list: `.commands`)
""",
    'nosuchtag':
    '\n    No such tag: **{tag}**\n\n    try checking full list: `.tags`',
    'abouthelp':
    """
    Get general info about how to start
""",
    'help':
    r"""
Hy, my name is [iahr](https://github.com/B1Z0N/iahr/). 

------------------------------------

Get help about syntax 
with **{new_msg}synhelp**.

See **{new_msg}commands** for the list 
of commands. 

Pass command to get detailed info:

    `{new_msg}commands commands`

See **{new_msg}tags** for the list 
of tags.

Pass tag to get commands 
with this tag:

    `{new_msg}tags default`

------------------------------------

Hey, **buddy**, use me tenderly and 
don't forget about your **IMAGINATION**!
""",
    'aboutcommands':
    """
    Get the list of all commands or info about command

        Commands list:

        `.commands`

        Info about command:

        `.commands commands`
""",
    'abouthandlers':
    """
    Get the info about handlers.
    Handler is a reaction to some event:

        Handlers list(divided by event types):

        `.handlers`

        Handlers on specific event type:

        `.handlers onedit`

        Info about handlers(specify event type):

        `.handlers onedit [hndl1 hndl2]`
""",
    'handlers': {
        'wrongordering':
        'You can\'t pass handlers, not specifying event type first\n',
        'nosuchtype': 'No such event type **{etype}**\n\nCheck **.handlers**!',
        'nosuchhndl': 'No such handler, try checking full list: **.handlers**'
    },
    'abouttags':
    """
    Get the list of all tags or list of commands tagged,

        Tags list:

        `.tags`

        Commands tagged with `default`:

        `.tags default`
""",
    'enabled':
    'enabled',
    'disabled':
    'disabled',
    'unknownactiontype':
    'Unknown type to operate on: **{}**\nMust be one of ["commands", "handlers", "tags"]',
    'aboutallowusr':'see **{new_msg}accesshelp**',
    'aboutallowchat':'see **{new_msg}accesshelp**',
    'aboutbanusr':'see **{new_msg}accesshelp**',
    'aboutbanchat':'see **{new_msg}accesshelp**',
    'aboutallowedchat':'see **{new_msg}accesshelp**',
    'aboutallowedusr':'see **{new_msg}accesshelp**',
    'aboutignore':
    """
    Ignore a chat when processing commands from
    banned users. Reduces spam level

        by chatname or id all commands:
        
        `.ignore chatname`
        
        all chats:
        
        `.ignore *`
        
        the chat that you are writing this in:
        
        `.ignore`
""",
    'aboutverbose':
    """
    Enable chat when processing commands from
    banned users. Increases spam level, but
    also increases clarity

        by chatname or id all commands:
        
        `.unignore chatname`
        
        all chats:
        
        `.unignore *`
        
        the chat that you are writing this in:
        
        `.unignore`
""",
    'aboutsynhelp':
    """
    Get help about syntax rules
""",
    'synhelp':
    r"""
Hy, my name is [iahr](https://github.com/B1Z0N/iahr/). 

------------------------------------

All commands start with "`{new_msg}`",
arguments can be passed too: 

    `{new_msg}commands help` or `{new_msg}commands {left}help{right}`

------------------------------------

Pros of using brackets is that you can 
pass args with spaces, but don't forget 
to escape special symbols in brackets:

    `{new_msg}commands {left}very weird command \\{new_msg}\\{left}\\{right}{right}`

------------------------------------

Also there are `raw args`:

    `{new_msg}commands {raw}{left}very weird command {new_msg}{left}{right}{right}{raw}`

------------------------------------

You could use keyword args:
    allow me to run `commands` command

    `{new_msg}allowusr usr=me cmd=commands`

    allow ... to run all commands
    (not tagged with `admin`)

    `{new_msg}allowusr [usr=wery weird user with = sign]`

Or even like this:

    `{new_msg}do [what={new_msg}do1 other {new_msg}do2]`

------------------------------------

And the most important thing, 
you can chain commands, as long 
as they support each others return 
types:

    `{new_msg}do1 {left}{new_msg}do2 {left}arg1{right}{right} {left}{new_msg}do3{right}`

The brackets will add up automatically:

    `{new_msg}do1 {new_msg}do2 arg1 {new_msg}do3`
        means
    `{left}{new_msg}do1 {left}{new_msg}do2 {left}arg1{right} {left}{new_msg}do3{right}{right}{right}`
""",
    'aboutaccesshelp':
    """
    Get help about access rights actions
""",
    'accesshelp':
    r"""
You can customize access level 
to all your routines anytime.
------------------------------------

1. First you need to decide which 
command to use, start typing '{new_msg}'
2. Then select the access action 
write one of three: 'ban', 'allow' or
'allowed'(to find out the rights)
3. Then continue and select one 
of two: 'chat' or 'usr' entities

For example: `{new_msg}allowedusr`
Continue typing, tell what you need...
------------------------------------

Whatever command you've chosen in
the previous paragraph, the interface 
to it is all the same.

It depends on type of routine,
some examples:

`{new_msg}allowchat commands {left}chat1 chat2{right} {left}synhelp help{right}`

Or deduce entity from context,
by using `{current}` wildcard.
USR: usr you are replying to, or you
CHAT: current chat

`{new_msg}allowedusr handlers {current} onedit somehandler`

Apply to all commands, handlers, tags:

`{new_msg}banusr commands {current}`
`{new_msg}allowedchat handlers onedit {current}`
`{new_msg}banchat tags {current}`

Use tags to access whole categories
of commands/handlers:

`{new_msg}allowchat tags $ {raw}{left}default admin{right}{raw}`
"""
}

##################################################
# Russian
##################################################

localization['russian'] = {
    'nosuchcmd':
    """
    Нет такой команды,
    попробуйте посмотреть их список: `.commands`
""",
    'nosuchtag':
    '\n    Нет такого тэга: **{tag}**\n\n    попробуйте посмотреть их список: `.tags`\n',
    'abouthelp':
    """
    Общая информация о том с чего начать
""",
    'help':
    r"""
Привет, меня зовут [iahr](https://github.com/B1Z0N/iahr/). 

------------------------------------
    
Информация по синтаксису: **{new_msg}synhelp**.

**{new_msg}commands** - для получения
списка команд.

Передайте имя команды, чтобы получить
детальную информацию:

    `{new_msg}commands commands`

**{new_msg}tags** - для получения
списка тэгов

Передайте тэг, чтобы получить
список команд по нему:

    `{new_msg}tags default`

------------------------------------

Хей, **дружище**, используй меня нежно
и не забывай про свое **ВООБРАЖЕНИЕ**!
""",
    'aboutcommands':
    """
    Список всех команд или информация по команде

        Список команд:

        `.commands`

        Информация по команде:

        `.commands commands`
""",
    'abouthandlers':
    """
    Информация про хендлеры.
    Хендлер - команда, котороую нельзя
    комбинировать и использовать явно.

        Список хендлеров(разбит по типу события):

        `.handlers`

        Всё по конкретному типу события:

        `.handlers onedit`

        Информация по конкретным хендлерам
        (тип события - обязателен):

        `.handlers onedit [hndl1 hndl2]`
""",
    'handlers': {
        'wrongordering':
        'Нельзя передать **hndl**, не указав **etype** сначала\n',
        'nosuchtype':
        'Нет такого типа события **{etype}**\n\nСмотрите **.handlers**!',
        'nosuchhndl':
        'Нет такого хендлера **{hndl}**, смотрите весь список: **.handlers**'
    },
    'abouttags':
    """
    Список тэгов или команд с этим тэгом

        Список тэгов:

        `.tags`

        Список команд помеченых `default`:

        `.tags default`
""",
    'enabled':
    'разрешено',
    'disabled':
    'запрещено',
    'unknownactiontype':'Неизвестны тип: **{}**\nДолжен быть один из ["commands", "handlers", "tags"]',
    'aboutallowusr':'смотрите **accesshelp**',
    'aboutallowchat':'смотрите **accesshelp**',
    'aboutbanusr':'смотрите **accesshelp**',
    'aboutbanchat':'смотрите **accesshelp**',
    'aboutallowedchat':'смотрите **accesshelp**',
    'aboutallowedusr':'смотрите **accesshelp**',
    'aboutignore':
    """
    Игнорировать сообщения от пользователей 
    без доступа. Уменьшает уровень спама

        по логину или по id чата:
        
        `.ignore chatname`
        
        все чаты:
        
        `.ignore *`
        
        этот чат:
        
        `.ignore`
""",
    'aboutverbose':
    """
    Реагирвать на сообщения от пользователей 
    без доступа. Увеличивает уровень спама,
    повышает ясность

        по логину или по id чата:
        
        `.unignore chatname`
        
        все чаты:
        
        `.unignore *`
        
        этот чат:
        
        `.unignore`
""",
    'aboutsynhelp':
    """
    Получить информацию по правилам синтаксиса
""",
    'synhelp':
    r"""
Все команды начинаются с "`{new_msg}`",
вы можете передавать аргументы: 

    `{new_msg}commands help` или `{new_msg}commands {left}help{right}`

------------------------------------


Плюсы использования скобок - это то, 
что вы можете передавать аргументы с 
пробелами, но не забывайте эскейпить 
спец. символы внутри:

    `{new_msg}commands {left}очень_странная_команда \\{new_msg}\\{left}\\{right}{right}`

------------------------------------

Также можно использовать `raw args`(`чистые аргументы`):

    `{new_msg}commands {raw}{left}очень_странная_команда {new_msg}{left}{right}{right}{raw}`

------------------------------------

Вы можете использовать именованые аргументы:
    разрешить себе использовать команду `commands`

    `{new_msg}allowusr usr=me cmd=commands`

    разрешить ... использовать все команды(не тэгнутые admin)

    `{new_msg}allowusr [usr=ochen stranniy polsovatel s znAkom =]`

Или даже так:

    `{new_msg}do [what={new_msg}do1 other {new_msg}do2]`

------------------------------------

И самое важное, вы можете
обьединат команды в цепочку,
если она поддерживают друг друга:

    `{new_msg}do1 {left}{new_msg}do2 {left}arg1{right}{right} {left}{new_msg}do3{right}`

Скобки добавляются автоматически:

    `{new_msg}do1 {new_msg}do2 arg1 {new_msg}do3`
        то же самое что
    `{left}{new_msg}do1 {left}{new_msg}do2 {left}arg1{right} {left}{new_msg}do3{right}{right}{right}`
""",
    'aboutaccesshelp':
    """
    Получить информацию по командах прав доступа
""",
    'accesshelp':
    r"""
Вы можете изменять уровень доступа
к любым вашим командам/хендлерам.
------------------------------------

1. Для начала нужно решить какую команду
использовать, начните печатать '{new_msg}'
2. Потом выберите одно из действий: 
'ban', 'allow' или 'allowed'
(последнее чтобы посмотреть права)
3. Продолжайте, напечтайте одно из:
'chat' или 'usr' сущностей 

Например: `{new_msg}allowedusr`
Продолжайте печатать что вам нужно...
------------------------------------

Какую бы команду вы не выбрали
в предыдущем пункте, шаги далее
будут теми же для всех их

Всё зависит от типа команды, которую
вы выберете:

`{new_msg}allowchat commands {left}chat1 chat2{right} {left}synhelp help{right}`

Можно попросить Iahr вычислить
сущность из контекста, используя
знак `{current}`
USR: пользователь, которому вы отвечаете(reply),
или вы(если вы никому не reply'ете)
CHAT: чат, в которым вы это пишете

`{new_msg}allowedusr handlers {current} onedit somehandler`

Применить ко всем commands, handlers, tags:

`{new_msg}banusr commands {current}`
`{new_msg}allowedchat handlers onedit {current}`
`{new_msg}banchat tags {current}`

Используйте тэги чтобы применять
команду к целым категориям:

`{new_msg}allowchat tags $ {raw}{left}default admin{right}{raw}`
"""
}
