# Iahr

Telegram chats command execution framework based on telethon library

# Contents

- [Iahr](#iahr)
- [Contents](#contents)
- [Warning](#warning)
- [Setup](#setup)
- [Example](#example)
- [HOW TO commands](#how-to-commands)
    - [How it works](#how-it-works)
    - [Adding new commands](#adding-new-commands)
    - [Non new message event command](#non-new-message-event-command)
    - [Senders](#senders)
    - [Syntax](#syntax)
    - [Built-in commands](#built-in-commands)
- [HOW TO extend](#how-to-extend)
    - [Configuration](#configuration)
    - [Session filename and permissions](#session-filename-and-permissions)
    - [Creating senders](#creating-senders)
    - [Other ways](#other-ways)
- [HOW TO contribute(and TODOs)](#how-to-contributeand-todos)
    - [Guidelines](#guidelines)
      - [Coding style](#coding-style)
      - [Templates](#templates)
    - [Syntax error refactoring](#syntax-error-refactoring)
    - [New commands](#new-commands)
    - [Tests](#tests)
    - [Docker](#docker)
    - [Ideas](#ideas)
    - [Problems](#problems)
- [Naming](#naming)
- [Thanks](#thanks)

# Warning

Be careful to not violate Telegram's [Terms of service](https://core.telegram.org/api/terms).
> If you use the Telegram API for flooding, spamming, faking subscriber and view counters of channels, you will be banned forever.
> Due to excessive abuse of the Telegram API, all accounts that sign up or log in using unofficial Telegram API clients are automatically put under observation to avoid violations of the Terms of Service.

# Setup

There are two ways of installation:
       1. Run `pip3 install iahr` and create some kind of `exmpl` folder
       2. Clone this project and see `exmpl` folder for further instructions

Personally I prefer second option, since it's half-ready setup.

# Example

Example in `exmpl` folder has all you need to get started. 


1. Go to `exmpl` folder ~> `cd exmpl`
1. Create venv ~> `python3 -m venv venv`
1. Go into venv ~> `source venv/bin/activate` 
1. Install requirements ~> `pip3 install -r ../requirements.txt`
1. Exit venv ~> `exit`
1. Provide your [telegram API credentials](https://core.telegram.org/api/obtaining_api_id) to template in `.env_exmpl`
1. Rename it ~> `mv .env_exmpl .env`
1. Start example ~> `./start.sh venv`
1. Go to your telegram account and send `.help` or `.synhelp` to any chat

Now you could add new commands and change configuration of the framework by altering `main.py` and `commands.py`. More on that you can read below.



# HOW TO commands

> They created a program to tell them one thing, the most important one. After a few months
>
> it stopped and printed: "function". 

Well, actually it printed **segmentation fault, core dump**, but the quote ain't cooler in this case.

### How it works

You could easily add new commands, `iahr` was designed for it. And moreover you could easily compose them(like plain old functions in any modern PL), as long as one commands return type corresponds to other argument's type.

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

Just add new function, like you would do in python. 

```python
def marco():
    return 'polo'
```

And that's wrong!. Stop, not so fast. It lacks three more things:

1. `iahr` doesn't know anything about your code. So it should be registered.
2. Use `async def` because it's faster
3. You need more info to reply to a message, just an additional parameter: `event`

So now:

```python
@VoidSender()
async def marco(event):
	await event.message.reply('polo')
```

That's it. It automatically adds your command to the list of commands on `.help`. But there is more than one way to do it right: 

```python
from telethon.events import NewMessage as newmsg

@TextSender(
	name='marco', # how you will call it in chat
    about='An ancient game in modern messenger', # description on `.help marco`
    take_event=False, # whether it takes event, default - True
    multiret=False, # whether it returns one value, or multiple, default - False
    on_event=newmsg, # what event it should be called on, default - events.NewMessage
    tags={'audio'}) # tags facility to quickly search for commands
async def marco():
    return 'polo'
```

**NB**: don't forget`multiret=True` when you want to return list of values instead of one value: list. 

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

### Non new message event command

There [are](https://docs.telethon.dev/en/latest/quick-references/events-reference.html) other types of events. So here is an example of how you could use it:

```python
from telthon import events
@TextSender(take_event=False, about="""
	Reply, when someone edits the message
""", on_event=events.MessageEdited)
async def isaw():
    return 'I saw what you did here! You bastard!'
```

It was added for sake of uniform interface. So that you could add different types of commands and get help about them by means of ordinary senders. 

### Senders

Currently there are three senders:

* `VoidSender` - your functions returns nothing
* `TextSender` - it returns `str`
* `MediaSender` - return file-like object

You can import it from `iahr.reg`. And easily create new senders(more on it later, below).

### Syntax

Syntax details could be easily changed(see **Configuration** below). So we would use default configuration to show syntax example. Also, you can call `.synhelp` for the same purpose.

------------------------------------

All commands start with ".", arguments can be passed too: 

    .cmds help or .cmds [help]

------------------------------------

Pros of using brackets is that you can pass args with spaces, but don't forget to escape special symbols in brackets:

    .cmds [very weird command \.\[\]]

------------------------------------

Also there are raw args:

    .cmds r[very weird command .[]]r

------------------------------------

You could use keyword args:

* allow me to run help command:

  ```
  .allowusr usr=me cmd=help
  ```

* allow ... to run all commands

  ```
  .allowusr [usr=wery weird user with = sign]
  ```

* Or even like this:

  ```
  .do [what=.do1 other .do2]
  .do [what=[.do1 [other] [.do2]]]
  ```

------------------------------------

And the most important thing, you can chain commands, as long as they support each others return types:

    .do1 [.do2 [arg1]] [.do3]

The brackets will add up automatically:

```
.do1 .do2 arg1 .do3
```

means

```
[.do1 [.do2 [arg1] [.do3]]]
```

### Built-in commands

To run a command both user and chat need to be allowed to run this command(except if it's you(admin) who is running the command).

* `help`

  Where to start
  
* `cmds`

  1. get list of commands: `.cmds`
  2. get info about a command: `.cmds cmds` 

* `tags`

  1. get list of tags: `.tags`
  2. get list of commands with this tag: `.tags sometag` 

* `synhelp` - help about syntax

* `allowusr`

  1. allow user to run a command: `.allowusr B1ZON help` or `.allowusr usr=B1ZON cmd=help`

  2. allow user to run all non-admin commands: `.allowusr B1ZON`

  3. allow user that you are replying to (or you if you are replying to nobody): `.allowusr cmd=help`

     **NB**: the user could be gotten by replying to his message(the easiest way)

  4. like previous one, but all non-admin commands: `.allowusr`

  5. allow all users to run a command: `.allowusr * help`

* `allowchat`

  1. allow chat to run a command: `.allowchat strawberry_fields_forever help` or `.allowchat chat=starwbery_fields_forever cmd=help`

  2. allow chat to run all non-admin commands: `.allowchat strawberry_fields_forever`

  3. allow chat that you are writing this in `.allowchat cmd=help`

     **NB**: the chat could be detected automatically if you write in it(the easiest way)

  4. like previous one, but all non-admin commands: `.allowchat`

  5. allow all chats to run a command `.allowchat * help`

* `banusr` - just a mirrored function to `allowusr`

* `banchat` - twin function of `allowchat`

* `allowedusr`

  1. list all allowed commands to particular user: `.allowedusr B1ZON`

  2. see permissions of multiple users to run this command: `.allowedusr [B1ZON huligan2007] help`

  3. check permissions on multiple commands of user you are replying(or your permissions, if you are replying to nobody) : `.allowedusr [cmd=help synhelp]`

     **NB**: the user could be gotten by replying to his message(the easiest way)

  4. like previous one, but all commands: `.allowedusr`

* `allowedchat`

  1. list all allowed commands to particular chat: `.allowedchat loose_couple`

  2. check permissions of multiple chats to run this command: `.allowedchat [loose couple] help`

  3. check permissions on multiple commands of chat you are writing it in : `.allowedchat [cmd=help synhelp]`

     **NB**: the chat could be detected automatically if you write in it(the easiest way)

  4. like previous one, but all commands: `.allowedchat`

* `ignore`

  1. ignore printing output to users without permissions in a chat(decrease spam level): `.ignore chat`
  2. the same but chat is the one we are writing in: `.ignore`

* `unignore`

  1. print all output to users in a chat(increases spam, and clarity): `.unignore chat`
  2. the same but chat is the one we are writing in: `.unignore`

# HOW TO extend

 ### Configuration

To configure use function with this signature:

```python
from iahr.config import config

config(
    left=None, # left delimtier, default - '['
    right=None, # right delimiter, default - ']'
    raw=None, # raw arg delimiter, default - 'r'
    new_msg=None, # delimiter for ordinary command, default - '.'
    non_new_msg=None, # delimiter for non-newmsg command, default - '!'
    prefix=None, # prefix for non-newmsg command, default - '_'
    prefixes=None, # dict of prefixes depending on event type
    me=None, # user identifier meaning you, default - 'me'
    others=None, # user identifier meaning others, default - '*'
    log_format=None, # see 
    log_datetime_format=None,
    log_out=None, # log output may be sys.stdout, sys.stderr or filename
    session_fname=None # session file name, default - 'iahr.session'
)
```

### Session filename and permissions

By default your newly registered command would be allowed to use only you and in all chats.

Most probably you want all your bans, ignores for noisy users and chats to be saved when you exit the program. And, thank God, there are state. State stored in a JSON file. Here is an example content for few commands:

```json
{
    "commands": {
        ".help": {
            "usraccess": {
                "AccessList": {
                    "others": false,
                    "whitelist": [],
                    "blacklist": []
                }
            },
            "chataccess": {
                "AccessList": {
                    "others": false,
                    "whitelist": [],
                    "blacklist": []
                }
            }
        }
	...
    },
    "chatlist": {
        "AccessList": {
            "others": false,
            "whitelist": [],
            "blacklist": []
        }
    }
}

```

And most of it you could easily change, for example `others`. To change `whitelist` or `blacklist` you need to get user id of user, because it is much more reliable, it won't change over time. 

### Creating senders

No words, just action. For example, here are how `MediaSender` defined.

```python
from iahr.reg import create_sender, any_send, MultiArgs

# self.res - result of function: MultiArgs object
# self.event - original event object
async def __media_send(self):
    # MultiArgs contains only `args` - list of args 
    res = self.res.args[0]
    await any_send(self.event, file=res)
    
MediaSender = create_sender('MediaSender', __media_send)
```

And that's it. You could register new functions with `@MediaSender`.

**Note**: args and kwargs you pass to `any_send` after event are all that you pass to [event.message.reply](https://docs.telethon.dev/en/latest/modules/events.html?highlight=reply#telethon.events.chataction.ChatAction.Event.reply). 

 ### Other ways

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

# HOW TO contribute(and TODOs)

### Guidelines

#### Coding style

Use [yapf](https://github.com/google/yapf) with default settings([pep8](https://www.python.org/dev/peps/pep-0008/)). Be sure to run `yapf -ri *` before pushing. Or use an [online demo](https://yapf.now.sh/).

**Note**: there are errors regarding new [walrus operator](https://medium.com/better-programming/what-is-the-walrus-operator-in-python-5846eaeb9d95) and [f-strings](https://realpython.com/python-f-strings/), just remove them manually and then add it back after formatting.

#### Templates

There are templates for issues and pull requests in here. Use them.

### Syntax error refactoring

There are much more to learn in the wisdom of python's success. It is much easier to write code(commands in chat) when you have a lot of useful errors appearing when you do something wrong. So it's a major issue to work on. Some ideas on what errors we'd like to provide:

* Incompatible commands error

  When there are more or less args than command can take, we'll print 
  ```
  {command} takes more/less args, please check your query
  ```

### New commands

There is such a small directory as [commands](iahr/commands). And you can fulfill it with whole bunch of other files containing commands for different topics, like text, photos audiofiles, jokes and pranks, videos and many others, just use your imagination. That's the point!

### Tests

Now there are lots of unit tests. Endpoint is a full test coverage. We need to add tests to check if all is working as expected at telegram level. So here how integration testing could be done:

1. [Mock](https://docs.python.org/3/library/unittest.mock.html)
2. Create two clients and/or use [test servers](https://docs.telethon.dev/en/latest/developing/test-servers.html)

### Docker

Create docker container within `exmpl` folder.

### Ideas

* Tags support

  ​	enable structuring of commands by tags, like `.crop` and `.revert` is tagged with `audio`.

* Dynamic command creation

  ​	something like `.alias [oneword x: .concat .split $1]`

### Problems 
	
*  Fix `pip` deps and `start.sh` scripts
	
	1. Sort out `requirements.txt` to easier install necessary files.
	2. Make `start.sh` use only `python3.8` or higher
	3. Maybe create script to install all needed deps(docker will fit perfectly)

# Naming

`Iah` is [egyptian god](https://en.wikipedia.org/wiki/Iah) of the new moon. And in russian language "echo" and "moon" are homophones. The words that pronounce the same, but have different meaning. So "echo" is a prefect synonym to functionality of this framework. It replies to you with your request results. 

But I thought it'll sound more epic with "r" at the end. So here is why ^^

# Thanks

* To [Vsevolod Ambros](https://github.com/kraftwerk28), the man the idea of `iahr` was [stolen](https://github.com/kraftwerk28/tgai28) from.

* To my university, that will drop me out for doing this and not studying
