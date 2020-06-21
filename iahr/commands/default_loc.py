# localization for default routines
from ..config import IahrConfig

localization = {}


##################################################
# English
##################################################


localization['english'] = {
'nosuchcmd' : """
    No such command(try checking full list: `.commands`)
""",
'nosuchtag' : """
    No such tag(try checking full list: `.tagsf`)
""",
'abouthelp' : """
    Get general info about how to start
""",
'help' : r"""
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
'aboutcommands' : """
    Get the list of all commands or info about command

        Commands list:

        `.commands`

        Info about command:

        `.commands commands`
""",
'abouthandlers' : """
    Get the info about handlers.
    Handler is non new message routine.

        Handlers list(divided by event types):

        `.handlers`

        Handlers on specific event type:

        `.handlers onedit_`

        Info about handlers(specify event type):

        `.handlers onedit_ [hndl1 hndl2]`
""",
'handlers' : {
    'wrongordering' : 'You can\'t pass **hndl**, not specifying **etype** first\n',
    'nosuchtype' : 'No such event type **{etype}**\n\nCheck **.handlers**!',
    'nosuchhndl' : 'No such handler, try checking full list: **.handlers**'
},
'abouttags' : """
    Get the list of all tags or list of commands tagged,

        Tags list:

        `.tags`

        Commands tagged with `default`:

        `.tags default`
""",
'enabled' : 'enabled',
'disabled' : 'disabled',
'aboutallowusr' : """
    Allow usr to run a command

        by nick, id or phone number all comands:

        `.allowusr uname`
        
        all users some commands
        (not tagged with `admin`):
        
        `.allowusr * [cmd1 cmd2 cmd3]`
        
        message author or the user 
        that you are replying to:
        
        `.allowusr cmd=command`

    **You can't allow admin commands to all users**
""",
'aboutallowchat' : """
    Allow a command to be runned in a chat

        by chatname or id all commands:
        
        `.allowchat chatname`
        
        all chats some commands
        (not tagged with `admin`):
        
        `.allowchat * [cmd1 cmd2 cmd3]`
        
        the chat that you are writing this in:
        
        `.allowchat cmd=command`

    **You can't allow admin commands in all chats**
""",
'aboutbanusr' : """
    Ban usr from running a command

        by nick, id or phone number all comands:
        
        `.banusr uname`
        
        all users some commands:
        
        `.banusr * [cmd1 cmd2 cmd3]`
        
        message author or the user 
        that you are replying to:
        
        `.banusr cmd=command`
""",
'aboutbanchat' : """
    Ban command from running in a chat

        by chatname or id all commands:
        
        `.banchat chatname`
        
        all chats some commands:
        
        `.banchat * [cmd1 cmd2 cmd3]`
        
        the chat that you are writing this in:
        
        `.banchat cmd=command`
""",
'aboutallowedchat' : """
    Get the commands allowed in a chat

        by chatname or id:
        
        `.allowedchat chatname command`
        
        in current chat:
        
        `.allowedchat cmd=command`
        
        list of chats, list of commands:
        
        `.allowedchat [chat1 chat2] [cmd1 cmd2 cmd3]`
""",
'aboutallowedusr' : """
    Get the commands allowed to a usr

        by username, id or phone number:
        
        `.allowedusr usrname command`
        
        current user or the user 
        that you are replying to:
        
        `.allowedusr cmd=command`
        
        list of users, list of commands:
        
        `.allowedusr [usr1 usr2] [cmd1 cmd2 cmd3]`
""",
'aboutignore' : """
    Ignore a chat when processing commands from
    banned users. Reduces spam level

        by chatname or id all commands:
        
        `.ignore chatname`
        
        all chats:
        
        `.ignore *`
        
        the chat that you are writing this in:
        
        `.ignore`
""",
'aboutverbose' : """
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
'aboutsynhelp' : """
    Get help about syntax rules
""",
'synhelp' : r"""
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
"""
}


##################################################
# Russian
##################################################


localization['russian'] = {
'nosuchcmd' : """
    Нет такой команды,
    попробуйте посмотреть их список: `.commands`
""",
'nosuchtag' : """
    Нет такого тэга,
    попробуйте посмотреть их список: `.tags`
""",
'abouthelp' : """
    Общая информация о том с чего начать
""",
'help' : r"""
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
'aboutcommands' : """
    Список всех команд или информация по команде

        Список команд:

        `.commands`

        Информация по команде:

        `.commands commands`
""",
'abouthandlers' : """
    Информация про хендлеры.
    Хендлер - команда, котороую нельзя
    комбинировать и использовать явно.

        Список хендлеров(разбит по типу события):

        `.handlers`

        Всё по конкретному типу события:

        `.handlers onedit_`

        Информация по конкретным хендлерам
        (тип события - обязателен):

        `.handlers onedit_ [hndl1 hndl2]`
""",
'handlers' : {
    'wrongordering' : 'Нельзя передать **hndl**, не указав **etype** сначала\n',
    'nosuchtype' : 'Нет такого типа события **{etype}**\n\nСмотрите **.handlers**!',
    'nosuchhndl' : 'Нет такого хендлера, смотрите весь список: **.handlers**'
},
'abouttags' : """
    Список тэгов или команд с этим тэгом

        Список тэгов:

        `.tags`

        Список команд помеченых `default`:

        `.tags default`
""",
'enabled' : 'разрешено',
'disabled' : 'запрещено',
'aboutallowusr' : """
    Разрешить пользователю исполнять команду


        по нику, id или по номеру телефона(все команды): 

        `.allowusr uname`
        
        всем пользователям, список команд
        (не тэгнутые `admin`):
        
        `.allowusr * [cmd1 cmd2 cmd3]`
        
        автору сообщения или человеку,
        которому вы отвечаете(reply):
        
        `.allowusr cmd=command`

    **Запрещено разрешать админ команду всем**
""",
'aboutallowchat' : """
    Разрешить исполнение команды в чате

        по логину или по id чата, все команды:
        
        `.allowchat chatname`
        
        все чаты, нектороые команды
        (не тэгнутые `admin`)
        
        `.allowchat * [cmd1 cmd2 cmd3]`
        
        этот чат:
        
        `.allowchat cmd=command`

    **Запрещено разрешать админ команду всем**
""",
'aboutbanusr' : """
    Запретить пользователю исполнять команду

        по нику или номеру телефона, все команды:
        
        `.banusr uname`

        все пользователи, некоторые команды:

        `.banusr * [cmd1 cmd2 cmd3]`
        
        автору сообщения или человеку, которому
        вы отвечаете(reply):
        
        `.banusr cmd=command`
""",
'aboutbanchat' : """
    Запретить исполнение команды в чате

        по логину или по id чата, все команды:
        
        `.banchat chatname`
        
        все чаты, некоторые команды:
        
        `.banchat * [cmd1 cmd2 cmd3]`
        
        этот чат:
        
        `.banchat cmd=command`
""",
'aboutallowedchat' : """
    Получить список команд, разрешенных в этом чате

        по логину или по id чата:
        
        `.allowedchat chatname command`
        
        этот чат:
        
        `.allowedchat cmd=command`
        
        список чатов, список команд:
        
        `.allowedchat [chat1 chat2] [cmd1 cmd2 cmd3]`
""",
'aboutallowedusr' : """
    Получить список команд разрешенных пользователю

        по нику, или номеру телефона:
        
        `.allowedusr usrname command`
        
        автора сообщения или человека, которому
        вы отвечаете(reply):
        
        `.allowedusr cmd=command`
        
        список пользователей, список команд
        
        `.allowedusr [usr1 usr2] [cmd1 cmd2 cmd3]`
""",
'aboutignore' : """
    Игнорировать сообщения от пользователей 
    без доступа. Уменьшает уровень спама

        по логину или по id чата:
        
        `.ignore chatname`
        
        все чаты:
        
        `.ignore *`
        
        этот чат:
        
        `.ignore`
""",
'aboutverbose' : """
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
'aboutsynhelp' : """
    Получить информацию по правилам синтаксиса
""",
'synhelp' : r"""
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
"""
}
