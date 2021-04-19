# About

Telegram chat command execution framework based on telethon library

## Warning

Be careful, do not violate Telegram's [Terms of service](https://core.telegram.org/api/terms).
> If you use the Telegram API for flooding, spamming, faking subscriber and view counters of channels, you will be banned forever.
> Due to excessive abuse of the Telegram API, all accounts that sign up or log in using unofficial Telegram API clients are automatically put under observation to avoid violations of the Terms of Service.

# Contents

- [About](#about)
  * [Warning](#warning)
- [Contents](#contents)
- [How to start](#how-to-start)
  * [Docker](#docker)
  * [Basic concepts](#basic-concepts)
    + [Routines](#routines)
    + [Senders](#senders)
    + [Events](#events)
  * [How it works](#how-it-works)
    + [Adding new commands](#adding-new-commands)
    + [Adding new handlers](#adding-new-handlers)
    + [Built-in commands](#built-in-commands)
- [How to customize](#how-to-customize)
  * [Env](#env)
  * [Config](#config)
  * [Session file](#session-file)
- [How to extend](#how-to-extend)
  * [Creating senders](#creating-senders)
  * [Other ways](#other-ways)
- [How to contribute](#how-to-contribute)
  * [Guidelines](#guidelines)
    + [Coding style](#coding-style)
    + [Templates](#templates)
  * [Error refactoring](#error-refactoring)
  * [New commands](#new-commands)
  * [Localization](#localization)
  * [Tests](#tests)
  * [Ideas](#ideas)
- [Naming](#naming)
- [Thanks](#thanks)

# How to start

## Docker

```
cp .env_exmpl .env

# fulfill .env with your data
# ...
# build container

docker build . --tag iahr

# run exmpl(as a daemon)

docker run -v "$(pwd)"/exmpl:/opt/app/exmpl -it iahr exmpl

# run tests(optional)

docker run -v "$(pwd)"/tests:/opt/app/tests -it iahr tests
```

P. S. try adding sudo if something is faulty

## Basic concepts

### Routines

Routine is your python function with some metadata 
that can be accessed from telegram

There are two type of routines:

* **Commands** - text-based routines, call it by typing it's name in message.
* **Handlers** - reactions to some events(e.g. `onedit`)

### Senders

Senders decorators are used to register your routine.
Currently there are three senders:

* `VoidSender` - your function returns nothing
* `TextSender` - it returns `str`
* `MediaSender` - return file-like object

You can import it from `iahr.reg`. 
And easily create new senders(more on it later, below).

### Events

Every function, if not specified otherwise, takes event object
from telethon as first parameter. This helps to  provide custom
behavior and enables more freedom in terms of an API.

## How it works

You could easily add new commands, `Iahr` was designed for it. And moreover you could easily compose them(like plain old functions in any modern PL), as long as one commands return type corresponds to other parameter's type.

For example:

`.upper word` ~> `WORD`

`.lower wORd` ~> `word`

and the most epic one(attention!):

`.lower .upper word` ~> `word`

>  \- WOW, isn't it?
>
> \- It is!

And this is just text examples, you can use any data format to pass in/out of  commands.

### Adding new commands

I'm feeling lonely and bored, so i want to be able to play my favorite game marcopolo with myself in any chat.

Just add new function, like you would do it in python. 

```python
def marco():
    return 'polo'
```

And that's wrong!. Stop, not so fast. It lacks three more things:

1. `Iahr` doesn't know anything about your code. So it should be registered.
2. Use `async def` because it's faster
3. You need more info to reply to a message, just an additional parameter: `event`

So now:

```python
@VoidSender()
async def marco(event):
	await event.message.reply('polo')
```

That's it. It automatically adds your command to the list of commands on `.commands`. 
But there is more than one way to do it right: 

```python
from telethon.events import NewMessage as newmsg

@TextSender(
	name='marco', # how you will call it in chat
    about='An ancient game in modern messenger', # description on `.help marco`
    take_event=False, # whether it takes event, default - True
    multiret=False, # whether it returns one value, or multiple, default - False
    on_event=newmsg, # what event it should be called on, default - events.NewMessage
    tags={'games'}) # tags facility to quickly search for commands
async def marco():
    return 'polo'
```

**NB**: don't forget `multiret=True` when you want to return list of values instead of one value: list. 

-------------------------

Well that's now a lot more, it's just an overview of an API and you don't need to use it whole. Personally I would stop on something like this:

```python
@TextSender(take_event=False, about="""
	An ancient game in modern messenger
""")
async def marco():
    return 'polo'

# or

@TextSender(about='An ancient game in modern messenger')
async def marco(_):
    return 'polo'
```

### Adding new handlers

I want to trigger if someone edits a message. Let's do this.

By the way, there [are](https://docs.telethon.dev/en/latest/quick-references/events-reference.html) other types of events. So here is an example of how you could use it, currently only `onedit` is supported. But it is implemented with extension in future.

```python
from telthon import events

@TextSender(take_event=False, about="""
	Reply, when someone edits the message
""", on_event=events.MessageEdited)
async def isaw():
    return 'I saw what you did here! You bastard!'
```

### Built-in commands

To run a command both user and chat need to be allowed to run this command(except if it's you(admin) who is running the command).

* `help`
```
    Info to start with
```
* `synhelp`
```
    Info about syntax rules and some usage examples
```
* `commands`
```
    Get the list of all commands or info about command

        Commands list:

        `.commands`

        Info about command:

        `.commands commands`
```

* `handlers`
```
    Get the info about handlers.
    Handler is a reaction to some event:

        Handlers list(divided by event types):

        `.handlers`

        Handlers on specific event type:

        `.handlers onedit`

        Info about handlers(specify event type):

        `.handlers onedit [hndl1 hndl2]`
```
* `tags`
```
    Get the list of all tags or list of commands tagged,

        Tags list:

        `.tags`

        Commands tagged with `default`:

        `.tags default`
```
* `{allow|ban|allowed}{usr|chat}`
```
    You can customize access level 
    to all your routines anytime.
    ------------------------------------

    1. First you need to decide which 
    command to use, start typing '.'
    2. Then select the access action 
    write one of three: 'ban', 'allow' or
    'allowed'(to find out the rights)
    3. Then continue and select one 
    of two: 'chat' or 'usr' entities

    For example: .allowedusr
    Continue typing, tell what you need...
    ------------------------------------

    Whatever command you've chosen in
    the previous paragraph, the interface 
    to it is all the same.

    It depends on type of routine,
    some examples:

    .allowchat commands [chat1 chat2] [synhelp help]

    Or deduce entity from context,
    by using $ wildcard.
    USR: usr you are replying to, or you
    CHAT: current chat

    .allowedusr handlers $ onedit somehandler

    Apply to all commands, handlers, tags:

    .banusr commands $
    .allowedchat handlers onedit $
    .banchat tags $

    Use tags to access whole categories
    of commands/handlers:

    .allowchat tags $ r[default admin]r
```
* `accesshelp`
```
    Get help about access rights commands
```
* `ignore`
```
    Ignore a chat when processing commands from
    banned users. Reduces spam level

        by chatname or id all commands:
        
        `.errignore chatname`
        
        all chats:
        
        `.errignore *`
        
        the chat that you are writing this in:
        
        `.errignore`
```
* `errverbose`
```
    Enable chat when processing commands from
    banned users. Increases spam level, but
    also increases clarity

        by chatname or id all commands:
        
        `.errverbose chatname`
        
        all chats:
        
        `.errverbose *`
        
        the chat that you are writing this in:
        
        `.errverbose`
```

# How to customize

## Env

Change `.env` file to fit your needs.

**NB**: `TG_SESSION_PATH` and `IAHR_DATA_FOLDER` are relative to the working directory(`exmpl` or `tests`).

## Config

To configure use `config.json` file relative to `IAHR_DATA_FOLDER` env var.
(see example [here](exmpl/etc/config.json))
Or a function `config` from `iahr.config`. The first variant is preferable,
because it initializes program before it's execution.

## Session file

Go to the session file and modify it's json manually to get what you want.
It's path is `${IAHR_DATA_FOLDER}/iahr.session`.

# How to extend

## Creating senders

No words, just action. For example, here are how `MediaSender` defined.

```python
from iahr.reg import create_sender, any_send, MultiArgs

# self.res - result of a function: MultiArgs object
# self.event - original event object
async def __media_send(self):
    # MultiArgs contains only `args` - list of args 
    res = self.res.args[0]
    await any_send(self.event, file=res)
    
MediaSender = create_sender('MediaSender', __media_send)
```

And that's it. You could register new functions with `@MediaSender`.

**Note**: args and kwargs you pass to `any_send` after event are all that you pass to [event.message.reply](https://docs.telethon.dev/en/latest/modules/events.html?highlight=reply#telethon.events.chataction.ChatAction.Event.reply). 

## Other ways

If you have more demanding wishes. We are glad to satisfy them. Here is how to initialize it all manually:

```python
from iahr import init
from iahr.run import Manager
from iahr.reg import Register
from iahr.config import IahrConfig

# ...
# init telethons `client` variable
# ...

app = Manager()
register = Register(client, app)
IahrConfig.init(app, register)
```

That's how `iahr.init` works. But what if you want to create custom Manager and custom Register? We have something for you just overload `ABCManager` and `ABCRegister`. But i'll leave you on your own here. Go check how it works by example in [Manager](iahr/run/manager.py) and [Register](iahr/reg/register.py). 

# How to contribute

## Guidelines

### Coding style

Use [yapf](https://github.com/google/yapf) with default settings([pep8](https://www.python.org/dev/peps/pep-0008/)). Be sure to run `yapf -ri *` before pushing. Or use an [online demo](https://yapf.now.sh/).

**Note**: there are errors regarding new [walrus operator](https://medium.com/better-programming/what-is-the-walrus-operator-in-python-5846eaeb9d95) and [f-strings](https://realpython.com/python-f-strings/), just remove them manually and then add it back after formatting.

### Templates

There are templates for issues and pull requests in here. Use them.

## Error refactoring

There are much more to learn in the wisdom of python's success. It is much easier to write code(commands in chat) when you have a lot of useful errors appearing when you do something wrong. So it's a major issue to work on. Some ideas on what errors we'd like to provide:

* Incompatible commands error

  When there are more or less args than command can take, we'll print 
  ```
  {command} takes more/less args, please check your query
  ```

## New commands

There is such a small directory as [commands](iahr/commands). And you can fulfill it with whole bunch of other modules containing commands for different topics, like text, photos audiofiles, jokes and pranks, videos and many others, just use your imagination. That's the point!

## Localization

Right now `Iahr` supports english and russian languages.
You can provide localization to your own language.
For this you need to alter:

* `Iahr` internal messages:
    create file {yourlang}.py in [iahr/localization](iahr/localization).
* default commands messages:
    create according dictionary in [iahr/commands/default/localization.py](iahr/commands/default/localization.py).

## Tests

Right now there are lots of unit tests. Endpoint is a full test coverage. We need to add tests to check if all is working as expected at telegram level. So here how integration testing could be done:

1. [Mock](https://docs.python.org/3/library/unittest.mock.html)
2. Create two clients and/or use [test servers](https://docs.telethon.dev/en/latest/developing/test-servers.html)

## Ideas

* Dynamic command creation(see branch [alias](https://github.com/B1Z0N/iahr/tree/alias))

  ​	something like `.alias r[oneword x: .concat .split $1]r`

  ​	and then `.oneword [nice nice day] => niceniceday`

* Script to generate `README.md` from code

* Script to surround bare docker run with

# Naming

`Iah` is [egyptian god](https://en.wikipedia.org/wiki/Iah) of the new moon. And in russian language "echo" and "moon" are homophones. The words that pronounce the same, but have different meaning. So "echo" is a prefect synonym to functionality of this framework. It replies to you with your request results. 

But I thought it'll sound more epic with "r" at the end. So here is why ^^

# Thanks

* To [Vsevolod Ambros](https://github.com/kraftwerk28), the man the idea of `Iahr` was [stolen](https://github.com/kraftwerk28/tgai28) from.

* To my university/employer, that will drop me out for doing this and not studying/working
