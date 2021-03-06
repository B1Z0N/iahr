from telethon import events

from dataclasses import dataclass
import re, json, inspect


class Delimiter:
    RE_ESCAPINGS = r'.^$*+-?()[]{}\|'

    def __init__(self, delim: str):
        self.re_sensitive = delim in self.RE_ESCAPINGS
        self.original = delim
        self.escaped = '\\' + delim

    def in_re(self):
        return self.escaped if self.re_sensitive else self.original

    def unescape(self, s):
        return self.escaped_replace(s, self.original)

    def escape(self, s):
        return self.unescaped_replace(s, self.escaped)

    def escaped_replace(self, string, to):
        return string.replace(self.escaped, to)

    def unescaped_re(self):
        return r'(?<!\\){}'.format(self.in_re())

    def unescaped_replace(self, string, to):
        return re.sub(self.unescaped_re(), to, string)

    def __repr__(self):
        return f'Delimtier({self.original})'


class CommandDelimiter(Delimiter):
    def full_command(self, cmd):
        return self.original + cmd

    def is_command(self, s):
        return s.startswith(self.original)


class Delayed:
    def __init__(self):
        self.operation = None
        self.delayed = []

    def do(self, *args, **kwargs):
        if self.operation is None:
            self.delayed.append((args, kwargs))
        else:
            self.operation(*args, **kwargs)

    def undelay(self):
        if self.operation is None:
            return
        for el in self.delayed:
            args, kwargs = el
            self.operation(*args, **kwargs)
        self.delayed = []

    def init(self, operation):
        self.operation = operation
        self.undelay()

    def __repr__(self):
        return f'Delayed(delayed={self.delayed})'


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instance = None

    def __call__(self):
        if self._instance is None:
            self._instance = super().__call__()
        return self._instance


class ParseError(Exception):
    def __init__(self, s):
        super().__init__(IahrConfig.LOCAL['ParseError'].format(s))


def errstr(s, ebegin, eend):
    """
        errstr('.do r[err]', 4, 6)

        .do **r[**err]
              ^^
    """
    before, err, after = s[:ebegin], s[ebegin:eend], s[eend:]
    res = f'{before}`{err}`{after}'
    return res


def parenthesize(ldel, rdel, cmd_del, raw_del):
    left, right = ldel.original, rdel.original
    cmdd, raw = cmd_del.original, raw_del.original

    def next_delim(s, start):
        space_i = s.find(' ', start)
        rmatch = re.search(rdel.unescaped_re(), s[start:])
        right_i = -1 if rmatch is None else rmatch.start() + start

        if space_i == -1:
            return right_i
        elif space_i < right_i:
            return space_i
        else:
            return right_i

    def surround(s):
        return s if s.startswith(left) else left + s + right

    def is_left_raw(s, i):
        return s[i] == raw and i + 1 < len(s) and s[i + 1] == left

    def is_right_raw(s, i):
        return s[i] == right and i + 1 < len(s) and s[i + 1] == raw

    def is_unescaped(c):
        def _(s, i):
            return i < len(s) and s[i] == c and i > 0 and s[i - 1] != '\\'

        return _

    is_command, is_left, is_right = is_unescaped(cmdd), \
        is_unescaped(left), is_unescaped(right)

    def full_escape(s):
        return cmd_del.escape(rdel.escape(ldel.escape(s)))

    def do_raw(s, i):
        errstart = i
        start = i + 2
        while i < len(s) and not is_right_raw(s, i):
            i += 1
        if i == len(s):
            msg = errstr(s, errstart, errstart + 2)
            raise ParseError(IahrConfig.LOCAL['Unbalanced raw'].format(
                f'"{raw}{left} {right}{raw}":\n\n{msg}'))
        return surround(full_escape(s[start:i])), i + 2

    def do(s, i):
        errstart = i
        open_cnt, res = 0, ''
        cmd_arg = False
        while not is_right(s, i):
            if len(s) == i:
                msg = errstr(s, errstart - 1, errstart)
                raise ParseError(IahrConfig.LOCAL['Unbalanced'].format(
                    f'{left} {right}"\n\n{msg}'))

            if is_left_raw(s, i):
                subres, i = do_raw(s, i)
                res += subres
            elif is_left(s, i):
                subres, i = do(s, i + 1)
                res += surround(subres)
                i += 1
            elif is_command(s, i):
                start, i = i, next_delim(s, i)
                res += left + s[start:i]
                open_cnt += 1
                cmd_arg = True
            elif s[i] == ' ' or not cmd_arg:
                res += s[i]
                i += 1
            else:
                start, i = i, next_delim(s, i)
                res += left + s[start:i] + right

        return res + right * open_cnt, i

    return lambda s: do(surround(s), 1)[0]


class Tokenizer:
    """
        Class to tokenize to command text
    """

    # match
    # 1) spaces
    # 2) any characters (including `\)` and `\(`) without `(` and `)`
    # 3) `(` and `)`
    TOKS = re.compile(r' +|((\\\()|(\\\))|([^\(\)]))+|[()]')

    def __init__(self, s):
        self.s = s

    def tokenize(self):
        """
            Tokenize a string.
            Tokens yielded are of the form (type, string)
            Possible values for 'type' are '(', ')' and 'WORD'
        """
        s = self.s
        for match in self.TOKS.finditer(s):
            s = match.group(0)
            if s[0] == ' ':
                continue
            if s[0] in '()':
                yield s, s
            else:
                yield 'WORD', self.unescape(s[1:-1])

    @classmethod
    def parse_inner(cls, toks):
        """
            Parse once we're inside an opening bracket.
        """
        ty, name = next(toks)
        children = []
        if ty != 'WORD':
            raise ParseError(IahrConfig.LOCAL['Brackets should start'])

        while True:
            ty, s = next(toks)
            if ty == '(':
                children.append(cls.parse_inner(toks))
            elif ty == ')':
                return name, children

    @classmethod
    def parse_root(cls, toks):
        """
            Parse this grammar:
            ROOT ::= '(' INNER
            INNER ::= WORD ROOT* ')'
            WORD ::= [A-Za-z]+
        """
        ty, _ = next(toks)
        if ty != '(':
            raise ParseError(IahrConfig.LOCAL['Surround tokens'])
        return cls.parse_inner(toks)

    def perform(self):
        """
            Commodity function that glues it alltogether 
        """
        toks = self.tokenize()
        return self.parse_root(toks)

    @classmethod
    def from_str(cls, s, leftdel: Delimiter, rightdel: Delimiter):
        """
            Recursive lists from string
        """
        s = cls.escape(s)
        # surround it with double delimiters for correct space handling
        s = leftdel.unescaped_replace(s, "('")
        s = rightdel.unescaped_replace(s, "')")
        obj = cls(s)
        return obj.perform()

    @staticmethod
    def escape(s):
        return s.replace('(', r'\(').replace(')', r'\)')

    @staticmethod
    def unescape(s):
        return s.replace(r'\(', '(').replace(r'\)', ')')

    @classmethod
    def show_children(cls, tree):
        """
            Pretty print commands and it's args
        """
        name, children = tree
        if not children: return
        print('{} -> {}'.format(name,
                                ' '.join(child[0] for child in children)))
        for child in children:
            cls.show_children(child)


# import here, due to the circular import
from iahr.config import IahrConfig


class AccessList:
    """
        Users and groups access manager
    """
    # Current user is enabled by default and can't be disabled

    @classmethod
    def is_special(cls, ent):
        return ent in (IahrConfig.OTHERS, IahrConfig.ME)

    def __init__(self, allow_others=False, allow_selfact=False):

        self.whitelist = set()
        self.blacklist = set()
        self.allow_others = allow_others
        self.selfact = {'allow': allow_selfact, 'selfban': False}

    def allow(self, entity: str):
        if entity == IahrConfig.ME:
            if self.selfact['allow']:
                self.selfact['selfban'] = True
            return

        if entity == IahrConfig.OTHERS:
            self.whitelist = set()
            self.blacklist = set()
            self.allow_others = True
        elif self.allow_others is False:
            self.whitelist.add(entity)
        elif entity in self.blacklist:
            self.blacklist.remove(entity)

    def ban(self, entity: str):
        if entity == IahrConfig.ME:
            if self.selfact['allow']:
                self.selfact['selfban'] = True
            return

        if entity == IahrConfig.OTHERS:
            self.whitelist = self.blacklist = set()
            self.allow_others = False
        elif self.allow_others is True:
            self.blacklist.add(entity)
        elif entity in self.whitelist:
            self.whitelist.remove(entity)

    def is_allowed(self, entity: str):
        if entity == IahrConfig.ME:
            return not self.selfact['selfban']

        return (self.allow_others and entity not in self.blacklist)\
                or (not self.allow_others and entity in self.whitelist)

    def is_self(self, entity: str):
        return entity == IahrConfig.ME and not self.selfact['selfban']

    def __repr__(self):
        return 'AccessList(whitelist: {}, blacklist: {}, allow_others: {}, selfact: {})'\
                .format(self.whitelist, self.blacklist, self.allow_others, self.selfact)

    @classmethod
    async def check_me(cls, client):
        me = await client.get_me()
        myid = me.id

        def check(eid):
            return IahrConfig.ME if eid == myid else eid

        return check

    class ALEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, AccessList):
                return {
                    'AccessList': {
                        'others': obj.allow_others,
                        'selfact': obj.selfact,
                        'whitelist': list(obj.whitelist),
                        'blacklist': list(obj.blacklist),
                    }
                }

            return json.JSONEncoder.default(self, obj)

    class ALDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self,
                                      object_hook=self.object_hook,
                                      *args,
                                      **kwargs)

        def object_hook(self, dct):
            if 'AccessList' in dct:
                alst, dct = AccessList(), dct['AccessList']
                alst.allow_others = dct['others']
                alst.selfact = dct['selfact']
                alst.whitelist = set(dct['whitelist'])
                alst.blacklist = set(dct['blacklist'])
                return alst
            return dct


@dataclass
class ActionData:
    """
        Contains event and shortcut info about it's author
    """
    event: events.common.EventCommon
    uid: int
    chatid: int

    MESSAGE_T = {
        etype.Event
        for etype in [
            events.NewMessage, events.MessageDeleted, events.MessageEdited,
            events.MessageRead
        ]
    }

    OTHER_T = {}

    @classmethod
    async def from_event(cls, event):
        me = await AccessList.check_me(event.client)
        cid = me((await event.get_chat()).id)
        etype = type(event)

        if etype in cls.MESSAGE_T:
            print(event)
            uid = me(event.message.from_id)
        elif etype in cls.OTHER_T:
            # no definition of user, just pass `me`
            uid = IahrConfig.ME
        else:
            raise RuntimeError('Event type `{etype}` is currently unsupported')

        return cls(event, uid, cid)


def argstr(fun, remove_event=True):
    spec = inspect.getfullargspec(fun)
    args = spec.args
    if remove_event:
        args = spec.args[1:]

    if spec.defaults is not None:
        division = len(spec.defaults)
        args, kwargs = args[:-division], args[-division:]
        kwargs = zip(kwargs, spec.defaults)
    else:
        kwargs = []

    res = ' '.join(args) + ' '
    res += ' '.join('{}={}'.format(arg, val) for arg, val in kwargs)

    if spec.varargs is not None:
        res += '*' + spec.varargs + ' '
    if spec.kwonlydefaults is not None:
        res += ' '.join(arg + '=' + val
                        for arg, val in spec.kwonlydefaults.items())
    if spec.varkw is not None:
        res += ' **' + spec.varkw

    return res


def ev_to_type(event):
    """
        Return type of this event. 
        event - type or instance of an event
    """
    if not isinstance(event, type):
        return type(event)
    return event


def ev_prefix(etype):
    """
        Get prefix to different types of events
    """
    etype = ev_to_type(etype)
    pr = IahrConfig.PREFIXES.get(etype)
    return '' if pr is None else pr
