from iahr.utils import Delimiter, CommandDelimiter, \
Delayed, SingletonMeta, parenthesify, Tokenizer, AccessList,\
ActionData

from iahr.config import IahrConfig

import pytest

##################################################
# Delimiter tests
##################################################


class TestDelimiter:
    DELIMITERS = {
        **{ d : '\\' + d for d in Delimiter.RE_ESCAPINGS },
        **{ d : d for d in ['a', 's', 'd', 'f', '/', '&']},
    }


    @pytest.mark.parametrize('orig, in_re', [
        *DELIMITERS.items()
    ])
    def test_re(self, orig, in_re):
        d = Delimiter(orig)
        assert d.in_re() == in_re
        assert d.unescaped_re() == r'(?<!\\){}'.format(in_re)   
    
    @pytest.mark.parametrize('delimiter, escaped, unescaped', [
        ('.', r'once in \.a .while', 'once in .a .while'),
        ('?', r'once in \?a ?while', 'once in ?a ?while'),
        ('\\', r'once in \\a \while', r'once in \a \while'),
    ])
    def test_escaping(self, delimiter, escaped, unescaped):
        delimiter = Delimiter(delimiter)
        assert delimiter.unescape(escaped) == unescaped
        assert delimiter.escaped_replace(escaped, delimiter.original) == unescaped

        escaped = delimiter.escape(unescaped)
        assert delimiter.unescape(escaped) == unescaped
        assert delimiter.escape(unescaped) == escaped
        assert delimiter.unescaped_replace(unescaped, delimiter.escaped)

    
class TestCommandDelimiter:
    @pytest.mark.parametrize('delimiter, cmd', [
        ('.', 'help'),
        ('.', '.help'),
        ('!', 'help'),
        ('!', '!help') 
    ])
    def test_command(self, delimiter, cmd):
        d = CommandDelimiter(delimiter)
        fcmd = d.full_command(cmd)
        assert fcmd == delimiter + cmd
        assert d.is_command(fcmd)
        assert d.is_command(cmd) == cmd.startswith(delimiter)
       

class TestDelayed:
    def operation(self, *args, **kwargs):
        self.cnt += 1


    @pytest.mark.parametrize('cnt', [ 1, 5, 20, 50 ])
    def test_calls_cnt(self, cnt):
        d = Delayed()        
        args, kwargs = [1, 2, 3], {'a' : 4, 'b' : 5 }
        for i in range(cnt):
            d.do(*args, **kwargs)
        for el in d.delayed:
            assert list(el[0]) == args
            assert dict(el[1]) == kwargs        

        self.cnt = 0
        assert len(d.delayed) == cnt
        d.init(self.operation)
        assert self.cnt == cnt
        assert len(d.delayed) == 0


class TestSingletonMeta:
    def test_singleness(self):
        class Singleton(metaclass=SingletonMeta):
            INSTANCE_COUNT = 0
            def __init__(self):
                self.id = self.INSTANCE_COUNT 
                self.INSTANCE_COUNT += 1
        
        s = Singleton()
        assert s.INSTANCE_COUNT == 1
        assert s.id == 0
        
        ss = [Singleton() for i in range(50)]
        for el in ss:
            assert el.id == s.id == 0
            assert id(el) == id(s)


class TestAccessList:
    ENT = 'some id'

    @pytest.mark.parametrize('operation, should_be', [
        ('allow', True),
        ('ban', False)
    ])
    def test_simple_operation(self, operation, should_be):
        for allow_others in (True, False):
            al = AccessList(allow_others)
            getattr(al, operation)(self.ENT)
            assert al.is_allowed(self.ENT) == should_be

    @pytest.mark.parametrize('allow_others', [True, False])
    def test_operation_when_already_done_for_all(self, allow_others):
        operation = 'allow' if allow_others else 'ban'
        al = AccessList(allow_others)
        lst = al.whitelist if allow_others else al.blacklist

        getattr(al, operation)(self.ENT)
        assert (len(lst) == 0)
        
    def test_me(self):
        al = AccessList()
        me = IahrConfig.ME
        assert al.is_allowed(me)
        al.ban(me)
        assert al.is_allowed(me)
        al = AccessList(allow_others=True)
        assert al.is_allowed(me)

    @pytest.mark.parametrize('operation', ['allow', 'ban'])
    def test_others(self, operation):
        should_be = operation == 'allow'
        opposite = 'allow' if operation == 'ban' else 'ban'
        al = AccessList()
        others = IahrConfig.OTHERS

        assert not al.is_allowed(self.ENT)
        getattr(al, operation)(others)
        assert al.is_allowed(self.ENT) == should_be

        getattr(al, opposite)(self.ENT)
        assert not (al.is_allowed(self.ENT) == should_be)
        getattr(al, operation)(others)
        assert al.is_allowed(self.ENT) == should_be

    @pytest.mark.asyncio
    async def test_check_me(self, client1, client2):
        check_me1 = await AccessList.check_me(client1)
        check_me2 = await AccessList.check_me(client2)
        me1 = await client1.get_me()
        me2 = await client2.get_me()
        
        assert check_me1(me1.id) == IahrConfig.ME
        assert check_me1(me2.id) == me2.id
        
        assert check_me2(me2.id) == IahrConfig.ME
        assert check_me2(me1.id) == me1.id


