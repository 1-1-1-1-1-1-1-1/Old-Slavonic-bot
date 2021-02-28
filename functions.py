import json
import re
import os
import random

from datetime import datetime

from config import DATAFILE, LOG_FILENAME, LOGGING_ENABLED, CONSONANTS


def run_test(func=None, ifmain=True, print_=True, d=-1):
    """Example:
    >>> def func(name):
            print(name)
            answer = name is 'Name'
            return answer

    >>> run_test(ifmain=False)('name')
    'name'
    False
    """
    # Mind an index in the globals' dict.
    if ifmain:
        if __name__ != '__main__':
            def dummy_return(*args, **kwargs):
                return
            return dummy_return
    if func is None:
        func = list(globals().keys())[d]
        assert func != '__builtins__'
        func = eval(func)
    def call_with_args(*args, **kwargs):
        res = func(*args, **kwargs)
        if print_:
            print(res)
        return res
    return call_with_args


def log_info(info, *, filename=LOG_FILENAME):
    """Logger for the actions."""
    if not LOGGING_ENABLED:
        return
    
    # Ensuring the file exists:
    with open(filename, 'a') as f:
        del f

    info += '\n'

    def ctime():
        return datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    add_eol = False
    with open(filename, encoding='utf-8') as f:
        if (data := f.read()) and data[-1] != '\n':
            add_eol = True
        del data
    with open(filename, 'a', encoding='utf-8') as f:
        if add_eol:
            f.write('\n')
        f.write('[' + ctime() + '] ' + info)


def is_lower(s): return s.lower() == s


with open(DATAFILE, encoding='utf8') as f:
    data = json.load(f)


def word_replace(word):
    """Transliterate to the glagolic alphabeth."""
    if not word:
        return ""
    if re.fullmatch(r'[0-9]+', word):  # Case of a `number == 0...0` goes here.
        if word[0] == '0':
            return '0' + word_replace(word[1:])
        n = int(word)
        if n >= 3000:
            return word
        nums = list(word)
        d = data["glagolic"]["numbers"]
        def do_step(m):
            nonlocal nums
            if not int(nums[-m]): return
            if m < 4:
                nums[-m] = d[str(10**(m-1)*int(nums[-m]))]
            else:
                nums[:-3] = [d['1000']*(n // 1000)]
        for m in range(1, len(word) + 1):
            do_step(m)

        return '·'.join(filter(lambda t: t != '0', nums))

    word0 = word
    word = word.lower()
    assert re.fullmatch(r'(?i)[а-яё]+', word0)
    try:
        assert (res := word_translation(word))  #?
        return res
    except:
        d = data["glagolic"]["letters"]
        def func(i):
            orig_letter = word0[i]
            letter = word[i]
            res = d[letter]
            if is_lower(orig_letter):
                res = res.lower()
            return res
        return "".join(map(func, range(len(word))))


def exc_action(e, line):
    log_info(f"Line: {line}\nError: {e}")

data0 = data
_d = {}

path = os.listdir("data")
for fname in path:
    if fname in ['2.txt']:
        continue
    if re.fullmatch(r"\d+\.txt", fname):
        with open(os.path.join("data", fname), encoding='utf-8') as f:
            data = [line.rstrip('\n') for line in f.readlines()]
            n = data.index('===')
            code, data = data[:n], data[n+1:]
        d = {}
        exec("\n".join(code))
        _d[fname] = d
        del d

d = {
    1: _d["1.txt"],
    # 2: _d["2.txt"]
    '3': _d["3.txt"]  # tmp
}

del _d, data; data = data0

def is_in_2txt(phrase):
    pass


def parse_line_at2(word, line):
    line = line.replace(' ,', ',')  #?
    line = line.replace('\"', '"')  #?
    parts = line.split(';')
    parts = [line.strip(' ') for line in parts]
    for i in range(len(parts)):
        line = parts[i]
        if (p := re.match(r'[0-9]+(?:\.|\))', line)):
            parts[i] = line[p.end():].lstrip(' ')
    meanings = list(filter(lambda i: i, parts))

    raise NotImplementedError
    return word, meanings


def translate_phrase(phrase):
    """Translate the phrase to Old Slavonic.

    Try to search for `phrase` in a dictionary.
    Found —> return the random translation of it.
    Not found —> returns `None`.
    """
    plist = d[1].items()
    ress = []
    for a, q in plist:
        if phrase.lower() in map(lambda s: s.strip().lower(), q.split(";")):
            a = a.replace(')', '')
            a = a.replace('(', ',')
            a = a.split(',')
            a = map(lambda ph: ph.strip(), a)
            ress.extend(a)
    if not ress:
        plist = d['3'].items()
        ress = []
        for a, q in plist:
            if phrase.lower() == q.strip().lower():
                # Is perfect?
                ress.append(a)
        if not ress:
            return None
    res = random.choice(ress)
    if phrase == phrase.capitalize():
        res = res.capitalize()
    elif phrase == phrase.lower():
        res = res.lower()
    elif phrase == phrase.upper():
        res = res.upper()
    else:
        res = res.lower()
    
    return res


def dict_transliteration(word, dest=None):
    """Return the transliteration of `word` to alph. `dest`.
    Works only for those words, which are in the dictionary.
    """
    pass


def cyryllic_trans_of_number(number: str) -> "str or None":
    if not number:
        return number  # Case of `number == 0...0` goes here.
    if not re.fullmatch(r'[0-9]+', number):
        return
    zero = '0'
    if number[0] == zero:
        return zero + cyryllic_trans_of_number(number[1:])

    if int(number) > 999_999_999_999:
        return number

    digits_number = len(number)

    t = '\u0483'  # Титло в числах.
    _thou = "҂"
    mdot = '·' 

    number = list(number)  # ?

    _res = []

    d = data["cyryllic"]["numbers"]  # Mind name.
    def get_num(base_number: str) -> str:
        # Other — 6ther versions.
        return d[base_number].split('|')[0]

    def _number_under_1000(number: str):
        if not number:
            return ""
        res = []
        length = len(number)
        one = '1'
        req = list(range(length))
        if length > 1 and number[-2] == one:
            n1 = number[-1]
            ten = get_num('10')  # d['10']
            if n1 == zero:
                res.append(ten)
            else:
                res.append(ten + get_num(n1))
            del req[:2]
        for i, item in enumerate(reversed(number)):
            item = int(item)
            if item and i in req:
                transliterated = get_num(str(item*10**i))
                res.append(transliterated)
        return "".join(res)
    
    thou_s = 0
    is_fst_part = True
    while number:
        pre_a = _number_under_1000("".join(number[-3:]))
        if pre_a:
            if not is_fst_part:
                _res.append((mdot, ""))
            if is_fst_part:
                is_fst_part = False            
            _res.extend((_thou * thou_s, item) for item in pre_a)
        del number[-3:]
        thou_s += 1

    res = _res[::-1]
    _number = "|".join(d.values())
    
    if len(re.findall(_number, "".join("".join(item) for item in res))) > 1:
        pos = 2
    else:
        pos = 1

    counted = 0
    def do_local():
        nonlocal pos, counted
        ans = res[-pos:].count((mdot, ""))
        if ans > counted:
            counted += 1
            pos += 1
            return 1
        return 0
    while pos < len(res):
        if do_local() == 0:
            break
    omega = get_num('800')
    letter_i = get_num('10')
    with_no_titlo = (omega, letter_i)
    res[-pos] = (item := res[-pos])[0], item[1]+ t*(
        item[1] not in with_no_titlo)

    return mdot + "".join(''.join(item) for item in res) + mdot
'''
run_test()("12")
run_test()("10")
'''
run_test()("1871")
'''
run_test()("3")
run_test()("1")
run_test()("0")
run_test()("01")
run_test()("100")
run_test()("1000")
run_test()("200")
run_test()("202")
run_test()("301")
run_test()("321")
run_test()("221")
run_test()("1001")
run_test()(str(10_001))
run_test()(str(100_101))
run_test()(str(1_103_301))
run_test()(str(1_000_101))
'''

def _transliterate(word, *, dest="cyryllic"):
    """Transliterate the word to cyryllic."""
    try:  # To look.
        assert (res := cyryllic_trans_of_number(word))
        return res
    except:
        pass
    word = word.replace(chr(8211), chr(45))

    _d = data[dest]
    d = _d["letters"]

    if dest != "cyryllic":
        raise NotImplementedError("Transliterating to not-cyryllic \
is not implemented.")
    try:
        assert (res := dict_transliteration(word, dest=dest))
        return res
    except:
        if '-' in word:
            return '-'.join(_transliterate(word_, dest=dest)
                            for word_ in word.split('-'))

    # What is the best way to do with it?
    digit = r'[0-9]'
    digits = r'[0-9]+'
    if (_index := re.search(digit, word)):
        _index = re.search(digits, word)
        start = _index.start()
        end = _index.end()
        parts = word[:start], word[start:end], word[end:]
        res = (
            _transliterate(parts[0], dest=dest)
            + parts[1]
            + _transliterate(parts[2], dest=dest)
            )
        return res

    res = []
    i = 0
    n = len(word)
    skip = 0
    while i < n:
        c = word[i]
        c0 = c
        c = c.lower()
        var = d[c]
        _vars = var.split('|')
        dskip = 0
        if c == "о" and i < n - 1 and word[i+1].lower() == "т":
            # Does, which is from prev. line, really does so?
            res.append(d["от"])
            dskip = 1
            skip += 1
        elif c == "е":
            if i:
                res.append(_vars[2])
            else:
                res.append(_vars[0])
        elif c == "и":
            if i == n - 1 or word[i+1].lower() in CONSONANTS:
                res.append(_vars[0])
            else:
                res.append(_vars[1])
        elif c == "о":
            if not i:
                res.append(_vars[0])
            else:
                res.append(_vars[1])
        elif c == "у":
            if not i:
                res.append(_vars[0])
            else:
                res.append(_vars[1])
        elif c == "я":
            if i:
                res.append(_vars[0])
            else:
                res.append(_vars[1])
        else:
            res.append(var)
        if i == n-1 and c in CONSONANTS:
            res.append(d["ъ"])
            res[-1] = res[-1].split()[int(is_lower(c0) or n == 1)]
        i += dskip
        res[i-skip] = res[i-skip].split()[int(is_lower(c0))]

        i += 1

    return "".join(res)


def transliterate(text, dest="cyryllic"):
    pattern = r'(?i)[-–а-яё0-9]+'
    res = re.sub(pattern,  # Is it really so?
                 lambda match: _transliterate(match.group(),
                                              dest=dest),
                 text)
    return res

# ---

def do_translate(phrase):  # Check this function.
    r"""Translate part of text, which *should* be translated."""
    if (_n1 := re.search('\w', phrase)) is None:
        return phrase
    
    if re.fullmatch(r'\w*', phrase):
        try:
            assert (res := translate_phrase(phrase))
            return res
        except:
            return phrase
    s1 = chr(45)  # '-'
    s2 = chr(8211)  # '–'
    phrase = phrase.replace(s2, s1)
    del s1, s2
    if re.fullmatch(r'[-\w]*', phrase):
        try:
            assert (res := translate_phrase(phrase))
            return res
        except:
            phrases = re.split('-', phrase)
            return '-'.join(do_translate(phrase) for
                            phrase in phrases)
    n1 = _n1.start(); del _n1
    n2 = len(phrase) - re.search(r'\w', phrase[::-1]).start()
    parts = (phrase[:n1],
             phrase[n1:n2],
             phrase[n2:])
    phrase = parts[1]
    
    inds = [match.start() for match in re.finditer(r'^\w|(?<!\w)\w', phrase)]
    w = r'[\w-]+'
    n = len(inds)  # number of words at `phrase`.
    nmax = n
    i = 0  # index of the 1-st pattern in string.
    while n - 1:
        while i + n <= nmax:
            try:
                tmp = phrase[inds[i]:]
                tmp = re.match(w + r'(?:\W+' + w + '){' + str(n-1) + '}',
                    tmp).group()
                assert (res := translate_phrase(tmp))
                return (parts[0]
                        + do_translate(phrase[:inds[i]])
                        + res
                        + do_translate(phrase[inds[i] + len(tmp):])
                        + parts[2])
            except:
                i += 1
        i = 0
        n -= 1
    
    return (parts[0]
            + re.sub(r'[-\w]+',
                     lambda match: do_translate(match.group()),
                     phrase)
            + parts[2])

def _translation(text):  # Nice?
    """Translate from Russian to Old Slavonic, maybe with no transliteration."""
    flags = r'(?i)'
    wlet = r"[а-яё]"
    pattern = (flags
        + r"(?:^|(?<!" + wlet
        + r"))[-–а-яА-ЯёЁ\s,]+(?:$|(?!"
        + wlet + "))"
        )
    res = re.sub(pattern, lambda match: do_translate(match.group()),
                 text)

    return res


def glagolic_transliterate(text):
    """Return the tranliteration from Russian to glagolic."""
    pattern = "([А-ЯЁа-яё]+)|([0-9]+)"
    return re.sub(pattern, lambda match: word_replace(match.group()), text)

def translation(text, dest=None, transliterate_=True, *, from_="russian"):
    """Text translation from `from_` to `dest`."""
    if from_ != "russian":
        raise NotImplementedError
    if dest == "glagolic":
        text = _translation(text)
        if transliterate_:
            pattern = r"([А-ЯЁа-яё]+)|([0-9]+)"
            text = re.sub(pattern, lambda match: word_replace(match.group()),
                          text)
        return text
    elif dest == "cyryllic":
        res = _translation(text)
        if transliterate_:
            res = transliterate(res, dest=dest)
        return res
    else:
        pass
