from telethon import events

from dataclasses import dataclass
import re


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

    def unescaped_replace(self, string, to):
        return re.sub(r'(?<!\\){}'.format(self.in_re()), to, string)


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


class AccessList:
    """
        Users and groups access manager
    """
    # Current user is enabled by default and can't be disabled

    OTHERS = '*'    
    ME = 'me'

    
    @classmethod    
    def is_special(cls, ent):
        return ent in (cls.OTHERS, cls.ME)
    
    def __init__(self, allow_others=False):
        self.whitelist = set()
        self.blacklist = set()
        self.allow_others = allow_others

    def __access_modifier(self, entity: str, lst: set, desirable: bool):
        if entity == self.ME:
            return

        if entity == self.OTHERS:
            self.whitelist = set()
            self.blacklist = set()
            self.allow_others = not desirable
        elif self.allow_others is desirable:
            lst.add(entity)

    def allow(self, entity: str):
        self.__access_modifier(entity, self.whitelist, desirable=False)
               
    def ban(self, entity: str):
        self.__access_modifier(entity, self.blacklist, desirable=True)

    def is_allowed(self, entity: str):
        me = entity == self.ME
        return me or (self.allow_others and entity not in self.blacklist)\
                or (not self.allow_others and entity in self.whitelist)

    def __repr__(self):
        return 'whitelist: {}, blacklist: {}, allow_others: {},'\
                .format(self.whitelist, self.blacklist, self.allow_others)

    @classmethod
    async def check_me(cls, client):
        me = await client.get_me()
        myid = me.id
        def check(eid):
            return cls.ME if eid == myid else eid
        return check


@dataclass
class ActionData:
    """
        Contains event and shortcut info about it's author
    """
    event: events.common.EventCommon
    uid: int
    chatid: int

    @classmethod
    async def from_event(cls, event: events.NewMessage):
        me = await AccessList.check_me(event.client)
        uid = event.message.from_id
        c = await event.message.get_chat()
        return cls(
            event,
            me(uid),
            me(c.id)
        )


##################################################
# All about parsing
##################################################


class ParseError(Exception):
    def __init__(self, e):
        super().__init__('Error parsing the query: ({})'.format(e))


def parenthesify(left, right, command_delimiter): 
    def next_delim(s, start):
        space_i = s.find(' ', start)
        right_i = s.find(right, start)
 
        if space_i == -1:
            return right_i
        elif space_i < right_i:
            return space_i
        else:
            return right_i

    def surround(s):
        return s if s.startswith(left) else left + s + right

    def do(s, i):
        par_cnt, res = 0, ''
        cmd_args = False
        while s[i] != right:
            if s[i] == left:
                subres, i = do(s, i + 1)
                res += surround(subres)
                i += 1
            elif s[i] == command_delimiter:
                cmd_args = True
                start, i = i, next_delim(s, i)
                res += left + s[start:i]
                par_cnt += 1
            elif s[i] == ' ' or cmd_args is False:
                res += s[i]
                i += 1
            else:
                start, i = i, next_delim(s, i)
                res += left + s[start:i] + right

            
        return res + right * par_cnt, i

    def wrapper(s):
        s = surround(s)
        
        try:
            res = do(s, 1)
        except IndexError as e:
            raise ParseError(str(e))              
        else:
            return res[0]    
 
    return wrapper 

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
                yield 'WORD', self.unescape(s.strip())
    
    @classmethod
    def parse_inner(cls, toks):
        """
            Parse once we're inside an opening bracket.
        """
        ty, name = next(toks)
        children = []
        if ty != 'WORD': 
            raise ParseError('Bracket should be starting with word')
        
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
        if ty != '(': raise cls.ParseError
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
        s = leftdel.unescaped_replace(s, ' ( ')
        s = rightdel.unescaped_replace(s, ' ) ')
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
        print('{} -> {}'.format(name, ' '.join(child[0] for child in children)))
        for child in children:
            cls.show_children(child)
    

