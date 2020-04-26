from .register import CommandRegisterError, \
    WrongEventTypeError, UninitializedRegisterError
from .register import reg, init

from .senders import MultiArgs, create_sender, any_send
from .senders import TextSender, MediaSender, VoidSender

