from utils import SingletonMeta
from enum import Enum, auto
from manager import app, COMMAND_DELIMITER
from telethon import events


class CommandRegisterError(Exception):
    pass

class WrongEventTypeError(CommandRegisterError):
    def __init__(self):
        msg = 'Wrong event type of a command, look at Registrar.EventType enum'
        super().__init__(self, msg) 

class UninitializedRegistrarError(CommandRegisterError):
    def __init__(self):
        super().__init-_(self, "Call `init_client` first")


class Registrar(metaclass=SingletonMeta):
    NON_NEW_MSG_COMMAND = '!'
    NEW_MSG_COMMAND = COMMAND_DELIMITER    
    
    PREFIXES = { 
        events.MessageEdited : 'edit', 
        events.MessageDeleted : 'del', 
        events.MessageRead : 'read', 
        events.ChatAction : 'chataction' , 
        events.UserUpdate : 'usrupdate', 
        events.Album : 'album',
    }    

    @classmethod
    def prefix(cls, event):
        pr = PREFIXES.get(type(event))
        if pr is None:
            return NEW_MSG_COMMAND
    @classmethod
    def reg_new_msg(cls, name, handler, about):
        app.add(name, handler, about, delimiter=cls.NEW_MSG_COMMAND)
        
    def reg_others(self, name, handler, about, event):
        if self.client is None:
            raise UninitializedRegistrarError    

        app.add(self.prefix(event) + name,
                handler, about, delimiter=self.NON_NEW_MSG_COMMAND)
        client.add_event_handler(handler, event)

    def __init__(self):
        self.client = None

    def init_client(self, client):
        self.client = client

    def reg(self, name, handler, about, etype=None):
        if etype == None or type(etype) == events.NewMessage:
            reg_new_msg(name, handler, about)
        else:
            reg_others(name, handler, about, etype)

    
reg = Registrar()


