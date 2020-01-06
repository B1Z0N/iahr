MAX_LEN = 20

FRAME = {
    'single': {
        'H': '-',
        'V': '│',
        'TL': '╭',
        'TR': '╮',
        'BL': '╰',
        'BR': '╯'
    },
    'double': {
        'H': '=',
        'V': '║',
        'TL': '╔',
        'TR': '╗',
        'BL': '╚',
        'BR': '╝'
    }
}


def bordered(str: str, fr_type='single') -> str:
    def _div(str):
        words = str.split()
        _res = []
        while len(words) > 0:
            word = words.pop(0)
            if _res and len(' '.join(_res[-1])) + len(word) < MAX_LEN:
                _res[-1].append(word)
            else:
                _res.append([word])
        return _res

    def _norm(str, l):
        return str + ' ' * (l - len(str))

    msg = [' '.join(row) for row in _div(str)]
    lng = len(max(msg, key=len))

    # global FRAME
    fr = FRAME[fr_type]
    res = (
        fr['TL'] + fr['H'] * (lng + 2) + fr['TR'] + '\n' +
        '\n'.join(
            fr['V'] + ' ' + _norm(row, lng) + ' ' + fr['V']
            for row in msg
        ) +
        '\n' + fr['BL'] + fr['H'] * (lng + 2) + fr['BR']
    )

    return '<code>' + res + '</code>'
