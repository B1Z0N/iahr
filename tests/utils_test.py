from iahr.utils import Delimiter, CommandDelimiter, \
Delayed, SingletonMeta, parenthesify, Tokenizer, AccessList,\
ActionData

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

    
class CommandDelimiter:
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
       
