from ..utils import AccessList, ActionData, Delimiter, CommandDelimiter
from ..utils import Tokenizer, parenthesize, ParseError
from ..config import IahrConfig

import re
from typing import Callable


class ExecutionError(RuntimeError):
    """
        Raise when next sender doesn't accept args from previous one
        or when wrong arguments were passed to the command
        or when a command function is buggy
    """
    pass


class CommandSyntaxError(ExecutionError):
    """ 
        Plug exception to tell that some input is faulty 
    """
    def __init__(self, e):
        super().__init__("wrong syntax, {}".format(str(e)))


class PermissionsError(ExecutionError):
    """
        Exception telling that this user or this chat can't use particular command
    """
    def __init__(self, command):
        super().__init__("you can't use **{}** command".format(command))


class NonExistantCommandError(ExecutionError):
    """
        Exception telling that this command is not registered yet
    """
    def __init__(self, command):
        super().__init__("**{}** command does not exist".format(command))


class Query:
    """ 
        Class-representation of our command string in python code
    """
    def __init__(self, command: str, args=None, kwargs=None):
        self.command = command
        # Could be: List[str | Query]
        self.args = list(args) if args is not None else [] 
        # Could be: Dict[str: [str | Query]]
        self.kwargs = dict(kwargs) if kwargs is not None else {}

    KWARGS_RE = re.compile(r'(?<!\\)=')

    @classmethod
    def unescape(cls, s):
        s = IahrConfig.LEFT.unescape(s)
        s = IahrConfig.RIGHT.unescape(s)
        s = IahrConfig.CMD.unescape(s)
        return s

    ##################################################
    # All about parsing
    ##################################################

    @classmethod
    def from_str(cls, qstr):
        qstr = f'{IahrConfig.LEFT.original}{qstr}{IahrConfig.RIGHT.original}'

        try:
            IahrConfig.LOGGER.info(f'raw query:{qstr}')
            qstr = IahrConfig.ADD_PARS(qstr)
            IahrConfig.LOGGER.info(f'parenthesized query:{qstr}')
            tree = Tokenizer.from_str(qstr, IahrConfig.LEFT, IahrConfig.RIGHT)
            IahrConfig.LOGGER.info(f'query tree:{tree}')
        except ParseError as e:
            raise CommandSyntaxError(str(e))

        self = cls.__to_q(tree)
        IahrConfig.LOGGER.info(f'query obj:{self}')
        return self

    @classmethod
    def __process_args(cls, rawargs):
        if not rawargs: return [], {}
        args, kwargs = [], {}

        def divide(arg):
            if type(arg) == cls:
                args.append(arg)
            elif len(arg) == 2:
                kwargs[arg[0]] = arg[1]
            else:
                args.append(arg[0])

        rawargs = map(cls.__to_q, rawargs)
        [divide(arg) for arg in rawargs]
        return args, kwargs

    @classmethod
    def __to_q(cls, tree):
        command, args = tree
        args, kwargs = cls.__process_args(args)

        if IahrConfig.CMD.is_command(command):
            return cls(command[1:], args, kwargs)
        else:
            return (*re.split(cls.KWARGS_RE, command, 1), )

    def __repr__(self):
        res = IahrConfig.CMD.full_command(self.command) + ' ['
        res += ', '.join(f'{arg}' for arg in self.args) + '] {'
        res += ', '.join(f'{key}:{val}'
                         for key, val in self.kwargs.items()) + ' }'
        return f'Query({res})'

    def __eq__(self, other):
        return self.command == other.command and \
               self.args == other.args and \
               self.kwargs == other.kwargs


class Routine:
    """
        Class that contains raw command handler and 
        manages permissions to use it in chats and by users
    """
    def __init__(self, handler: Callable, about: str):
        self.about = about
        self.handler = handler
        self.usraccess = AccessList(allow_others=False)
        self.chataccess = AccessList(allow_others=True)

    def help(self):
        return self.about

    ##################################################
    # Rights to run this handler
    ##################################################

    def allow_usr(self, usr: str):
        self.usraccess.allow(usr)

    def ban_usr(self, usr: str):
        self.usraccess.ban(usr)

    def is_allowed_usr(self, usr: str):
        return self.usraccess.is_allowed(usr)

    def allow_chat(self, chat: str):
        self.chataccess.allow(chat)

    def ban_chat(self, chat: str):
        self.chataccess.ban(chat)

    def is_allowed_chat(self, chat: str):
        return self.chataccess.is_allowed(chat)

    def get_handler(self, usr: str, chat: str):
        """
            Try to get handler if allowed
        """
        if usr is None or chat is None:
            return
        if not self.is_allowed_usr(usr) or not self.is_allowed_chat(chat):
            return

        return self.handler

    ##################################################
    # Session managing
    ##################################################

    def get_state(self):
        return {
            'usraccess': self.usraccess,
            'chataccess': self.chataccess,
        }

    def set_state(self, state):
        self.usraccess = state['usraccess']
        self.chataccess = state['chataccess']

    JSON_ENCODER = AccessList.ALEncoder
    JSON_DECODER = AccessList.ALDecoder

    def __repr__(self):
        return f'Routine(usraccess={self.usraccess}, chataccess={self.chataccess})'


class Executer:
    """ 
        Glues together
        1. Query(by getting command name and it's args)
        2. Routine(got by command name)

        And thus pipes all needed handlers directly 
        and checks if commands are compatible
    """
    def __init__(self, qstr, commands, action: ActionData):
        self.query = Query.from_str(qstr)
        self.dict = commands
        self.action = action

    async def run(self):
        return await Executer.__run(self.query, self.dict, self.action)

    async def __process_args(rawargs, rawkwargs, subprocess: Callable):
        if not rawargs and not rawkwargs: return [], {}
        args, kwargs = [], {}
        for arg in rawargs:
            if type(arg) == Query:
                call = await subprocess(arg)
                args.extend(call.res.args)
            else:
                args.append(arg)

        for key, val in rawkwargs.items():
            if type(val) == Query:
                call = await subprocess(val)
                kwargs[key] = call.res.args[0]
            else:
                kwargs[key] = val

        return args, kwargs

    @classmethod
    async def __run(cls, query, dct, action):
        async def proc(subquery):
            return await cls.__run(subquery, dct, action)

        qname = IahrConfig.CMD.full_command(query.command)
        id_msg = f'name={qname}:uid={action.uid}:cid={action.chatid}'

        try:
            IahrConfig.LOGGER.info(f'getting handler:{id_msg}')
            handler = dct[qname].get_handler(action.uid, action.chatid)
        except KeyError:
            IahrConfig.LOGGER.error(
                f'getting handler:no such command registered:{id_msg}')
            raise NonExistantCommandError(query.command)
        if handler is None:
            IahrConfig.LOGGER.warning(
                f'executer:getting handler:not permitted:{id_msg}')
            raise PermissionsError(query.command)

        try:
            args, kwargs = await cls.__process_args(query.args, query.kwargs,
                                                    proc)
            IahrConfig.LOGGER.info(f'arg={args}:kwargs={kwargs}:{id_msg}')
            return await handler(action.event, *args, **kwargs)
        except (AttributeError, ValueError, TypeError) as e:
            IahrConfig.LOGGER.error(f'userspace error:err={e}:{id_msg}')
            raise ExecutionError(*e.args)

    def __repr__(self):
        return f'Executer(query={self.query}, dict={self.dict}, action={self.action})'
