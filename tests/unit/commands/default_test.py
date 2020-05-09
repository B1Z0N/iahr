import pytest

from iahr.commands import default


@pytest.mark.parametrize('input, is_cmds, result', [
    ('first', True, ['.first']),
    ('first second', True, ['.first', '.second']),
    ('first .second', True, ['.first', '.second']),
    (None, True, [None]),
    ('first', False, ['first']),
    ('first second', False, ['first', 'second']),
    ('first .second', False, ['first', '.second']),
])
def test___process_list(input, is_cmds, result):
    assert default.__process_list(input, is_cmds) == result

    