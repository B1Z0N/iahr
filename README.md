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



# Commands

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

# Built-in commands



# Framework configuration

