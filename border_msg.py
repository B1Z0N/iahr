def bordered(str):
    res = ''
    MAX_LEN = 20

    def rep(char, cnt):
        res = ''
        while cnt > 0:
            res += char
            cnt -= 1
        return res

    def _div(str):
        words = str.split(' ')
        _res = ['']
        while (len(words) > 0):
            if len(words[0]) > MAX_LEN:
                _res.append(words[0])
            elif len(_res[-1]) + len(words[0]) < MAX_LEN:
                _res[-1] = _res[-1] + ' ' + words[0]
            else:
                _res.append(words[0])
            words = words[1:]
        _res[0] = _res[0][1:]
        return _res

    def _norm(str, l):
        return str + rep(' ', l - len(str))

    msg = _div(str)
    lng = len(max(msg, key=len))

    res += '╭' + rep('-', lng + 2) + '╮\n'
    for row in msg:
        res += '│ ' + _norm(row, lng) + ' │\n'
    res += '╰' + rep('-', lng + 2) + '╯'

    return '<code>' + res + '</code>'
