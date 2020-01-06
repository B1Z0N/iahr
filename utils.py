MAX_LEN = 20


def bordered(str: str) -> str:
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

    res = (
        '╭' + '-' * (lng + 2) + '╮\n' +
        '\n'.join('│ ' + _norm(row, lng) + ' │' for row in msg) +
        '\n╰' + '-' * (lng + 2) + '╯'
    )

    return '<code>' + res + '</code>'
