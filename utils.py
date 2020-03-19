from os import path
import re
from telethon import tl
import json
from PIL import ImageFont, Image, ImageDraw
from typing import Tuple


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

LATIN = 'abcdefghijklmnopqrstuvwxyz'
VOWELS = 'аеєиіїоуыюя'
ST_SL_REPLACES = {
    'е': 'ѣ',
    'эту': 'сию',
    'этого': 'сего',
    'этот': 'сей',
    'эта': 'сия',
    'это': 'сие'
}


def bordered(str: str, fr_type='single') -> str:
    def _div(str):
        _words = str.split()
        _res = []
        while len(_words) > 0:
            _word = _words.pop(0)
            _rowlen = len(' '.join(_res[-1])) + len(_word) if _res else 0
            if _res and _rowlen < MAX_LEN:
                _res[-1].append(_word)
            else:
                _res.append([_word])
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

    return f'<code>{res}</code>'


def is_cyrrillic(str: str) -> bool:
    return all((l not in str) for l in LATIN)


def to_staro_slav(_str: str) -> str:
    _src = _str.lower()

    def repl(match: re.Match):
        w = match.group(0).lower()
        if (w not in VOWELS) and (w not in ('ь', 'ъ', 'й')):
            return w + 'ъ'
        else:
            return w

    _src = re.sub(r'(\w)\b', repl, _src)
    for w, rep in ST_SL_REPLACES.items():
        _src = _src.replace(w, rep)
    _src = _src.replace('и', 'і')
    _src = [[c for c in w] for w in _src.split()]
    for i, w in enumerate(_str.split()):
        if w[0].istitle():
            _src[i][0] = w[0]
    return ' '.join(''.join(w) for w in _src)


def jsonclass(path):
    def wrapper(cls):
        class WrapperClass(cls):
            def __init__(self, *args, **kwargs):
                super(WrapperClass, self).__init__(*args, **kwargs)

            def save(self):
                with open(path, 'w') as f:
                    json.dump(vars(self), f)

            def load():
                with open(path, 'r') as f:
                    d = json.load(f)
                    return WrapperClass(**d)
        return WrapperClass

    return wrapper


def mention(user: tl.types.User):
    if user.username:
        return f'@{user.username}'
    name = user.first_name
    if user.last_name:
        name += ' ' + user.last_name
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def wrap(text: str, font: ImageFont, maxwidth: int) -> Tuple[str, int]:
    res = []
    for w in text.split():
        if not res or font.getsize(res[-1] + ' ' + text)[0] > maxwidth:
            res.append(w)
        else:
            res[-1] += ' ' + w
    return '\n'.join(res), max(font.getsize(r)[0] for r in res)


def draw_text(image: Image, text: str):
    pass

RES_DIR = 'resources/'

def with_such_jokes(text) -> Image:
    BOX_SIZE = (94, 80)
    BOX_POS = (260, 140)

    img = Image.open(path.join(RES_DIR, 'with_such_jokes.jpg'))
    box = Image.new('RGBA', BOX_SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    font = ImageFont.truetype(path.join(RES_DIR, 'arial.ttf'), size=24)

    text, maxwidth = wrap(text, font, BOX_SIZE[0])
    d.text(
        ((BOX_SIZE[0] - maxwidth) / 2, 0),
        text,
        font=font,
        fill='#ffffff',
        stroke_width=2,
        stroke_fill='#000000',
        align='center'
    )
    img.paste(box, BOX_POS, box)
    return img


# tests
if __name__ == '__main__':
    print(bordered('Hello, world!', fr_type='single'))
    print(to_staro_slav('Привет. Как дела?'))
