# Iahr

Telegram command execution framework based on telethon library

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
    on_event=newmsg) # what event it should be called on, default - events.NewMessage
async def macro():
    return 'polo'
```

**Note**: don't forget`multiret=True` when you want to return list of values instead of one value: list. 

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

    .help help or .help [help]

------------------------------------

Pros of using brackets is that you can pass args with spaces, but don't forget to escape special symbols in brackets:

    .help [very weird command \.\[\]]

------------------------------------

Also there are raw args:

    .help r[very weird command .[]]r

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

  1. get list of commands: `.help`
  2. get info about a command: `.help help` 

* `allowusr`

  1. allow user to run a command: `.allowusr B1ZON help` or `.allowusr usr=B1ZON cmd=help`

  2. allow user to run all non-admin commands: `.allowusr B1ZON`

  3. allow user that you are replying to (or you if you are replying to nobody): `.allowusr cmd=help`

     **NB**: the user could be gotten by replying to his message(the easiest way)

  4. like previous one, but all non-admin commands: `.allowusr`

* `allowchat`

  1. allow chat to run a command: `.allowchat strawberry_fields_forever help` or `.allowchat chat=starwbery_fields_forever cmd=help`

  2. allow chat to run all non-admin commands: `.allowchat strawberry_fields_forever`

  3. allow chat that you are writing this in `.allowchat cmd=help`

     **NB**: the chat could be detected automatically if you write in it(the easiest way)

  4. like previous one, but all non-admin commands: `.allowchat`

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

* `synhelp` - help about syntax

## HOW TO extend

 ### Configuration



 ###  Creating senders



  ### Creating managers



 ### Creating registers



# HOW TO contribute

### Guidelines



### Syntax error refactoring



### New commands



### Ideas

* Modules support
* Dynamic command creation
* Spam level reduce
