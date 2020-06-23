import pytest

from iahr.commands import default


@pytest.mark.parametrize('input, is_cmds, result', [
    ('first', True, ['.first']),
    ('first second', True, ['.first', '.second']),
    ('first .second', True, ['.first', '.second']),
    (None, False, ['None']),
    ('first', False, ['first']),
    ('first second', False, ['first', 'second']),
    ('first .second', False, ['first', '.second']),
])
def test_process_list(input, is_cmds, result):
    assert default.process_list(input, is_cmds) == result
