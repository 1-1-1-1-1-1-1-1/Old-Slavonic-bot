"""Main functions file to translate / tranliterate the text to
Old Slavonic. 

Supported actions
-----------------

### Main ###

 * translate from Russian to Old Slavonic at Cyryllic script
 * translate from Russian to Old Slavonic at Glagolitic script
 * tranliterate from Russian to Old Slavonic at Glagolitic script

### Other / Functions ###

 * `run_test`: run test, see docs of it
 * `dict_transliteration`
 * `word_translation`
 * `translate_phrase`
 * `do_translate`
 * `_translation`
 * Directly transliterating to Glagolic
     - `glagolitic_translate_number`
     - `_glagolitic_transliterate`: transliterate a part of the text from
        Russian to Old Slavonic, Glagolitic script
     - `glagolitic_transliterate`
 * Directly transliterating to Cyryllic
     - `cyryllic_translate_number`
     - `_cyryllic_transliterate`
     - `cyryllic_transliterate`
 * `translation`

### Internal functions ###

 * `log_info`: log information
 * `is_lower`: is_lower(s: str) -> s.lower() == s
 * `exc_action`: action on occured exception
 * `is_in_2txt`
 * `parse_line_at2`

"""


import json
import re
import os
import random
from datetime import datetime

from config import DATAFILE, LOG_FILENAME, LOGGING_ENABLED, CONSONANTS


def run_test(func=None, ifmain=True, print_=True, d=-1):
    """Example:
    >>> def function(name):
            print(name)
            answer = name == 'Name'
            return answer

    >>> run_test(ifmain=False, print_=False)('name')
    name
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
        if func == 'func':
            # Rename not to cause the name collapse
            _func = eval(func)
            func = _func
        else:
            func = eval(func)
        
    def call_with_args(*args, **kwargs):
        res = func(*args, **kwargs)
        if print_:
            print(res)
        return res

    return call_with_args


def log_info(info, *, filename=LOG_FILENAME):
    """Log anything."""
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


def exc_action(e, line):
    return log_info(f"Line: {line}\nError: {e}")


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
    line = line.replace(r'\"', '"')  #?
    parts = line.split(';')
    parts = [line.strip(' ') for line in parts]
    for i in range(len(parts)):
        line = parts[i]
        if (p := re.match(r'[0-9]+(?:\.|\))', line)):
            parts[i] = line[p.end():].lstrip(' ')
    meanings = list(filter(lambda i: i, parts))

    raise NotImplementedError
    return word, meanings


# === Section: transliteration and translation preliminary stuff ==============


def dict_transliteration(word: str, dest=None) -> 'Optional[str]':
    """Return the transliteration of `word` to `dest`.
    Works only for those words, which are in the dictionary.
    """
    pass


def word_translation(word: str) -> 'Optional[str]':
    """Return the translation or `word` to Glagolitic.
    If not found, return `None`.
    """
    result = dict_transliteration(word, dest="glagolitic")
    return result


def translate_phrase(phrase: str) -> 'Optional[str]':
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
            return
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


def do_translate(phrase):
    """Translate part of text, which *should* be translated."""
    if not (_n1 := re.search(r'\w', phrase)):
        return phrase
    
    if re.fullmatch(r'\w*', phrase):
        try:
            # Here the *also transliterated* text may appear.
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
    n = len(inds)  # Number of words at `phrase`.
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
    
    result = (parts[0]
              + re.sub(r'[-\w]+',
                       lambda match: do_translate(match.group()),
                       phrase)
              + parts[2])
    return result


def _translation(text):  # Nice?
    """Translate from Russian to Old Slavonic, maybe with no transliteration."""
    flags = r'(?i)'
    wlet = r"[а-яё]"
    pattern = (flags
        + r"(?:^|(?<!" + wlet
        + r"))[-–а-яА-ЯёЁ\s,]+(?:$|(?!"
        + wlet + "))"
        )
    res = re.sub(pattern,
                 lambda match: do_translate(match.group()),
                 text)

    return res


# === Section: Glagolitic transliteration =====================================


def glagolitic_translate_number(string: str, allow_not_arabic=False) \
    -> str:
    if not allow_not_arabic:
        try:
            assert re.fullmatch(r'[0-9]+', string)
        except AssertionError:
            raise SyntaxError("Not arabic number passed")
    else:
        raise NotImplementedError("Using not arabic numbers at Glagolitic"
            " transliterate number function should be avoided")

    # Now the string is considered to represent the arabic number.

    if not string:
        # If `string` == "0...0", this happens
        return ""
    if string[0] == '0':
        return '0' + glagolitic_translate_number(word[1:])
    n = int(string)
    if n >= 3000:
        return string

    nums = list(string)
    d = data["glagolitic"]["numbers"]
    dobreak = False
    def do_step(m):
        nonlocal nums
        if not int(nums[-m]): return
        if m < 4:
            nums[-m] = d[str(10**(m-1)*int(nums[-m]))]
        else:
            nums[:-3] = [d['1000']*(n // 1000)]
            nonlocal dobreak
            dobreak = True
    for m in range(1, len(string) + 1):
        if dobreak:
            break
        do_step(m)

    if len(nums) > 1:
        nums = nums[:-2] + [nums[-1], nums[-2]]

    return '·'.join(filter(lambda t: t != '0', nums))


def _glagolitic_transliterate(word: str, transliterate_number=True) -> str:
    """Preliminary transliterate to the Glagolitic script."""
    if not word:
        return ""
    if re.fullmatch(r'[0-9]+', word):
        if transliterate_number:
            result = glagolitic_translate_number(word)
            return result
        # Otherwise `word` represents number,
        # no transliteration is required for it.
        return word

    word0 = word
    word = word.lower()
    assert re.fullmatch(r'(?i)[а-яё]+', word0)
    
    try:
        # Try to transliterate, using dictionary or another source.
        # It may be implemented and states as a sample.
        result = word_translation(word)
        assert result
        return result
    except:
        d = data["glagolitic"]["letters"]
        def func(i):
            orig_letter = word0[i]
            letter = word[i]
            res = d[letter]
            if is_lower(orig_letter):
                res = res.lower()
            return res
        return "".join(map(func, range(len(word))))


def glagolitic_transliterate(text: str, transliterate_numbers=True) -> str:
    """Write the Russian text at the Glagolitic script."""
    pattern = r"([А-ЯЁа-яё]+)|([0-9]+)"
    repl = lambda match: \
    _glagolitic_transliterate(
        match.group(),
        transliterate_number=transliterate_numbers
    )
    return re.sub(pattern,
                  repl,
                  text)


# === Section: Cyryllic transliteration =======================================


def cyryllic_translate_number(number: str) -> str:
    """Transliterate the number (given as :obj:`str`) to Cyryllic."""
    if not number:
        # Case of `number == "0...0"` goes here.
        return number

    assert re.fullmatch(r'[0-9]+', number)
    
    zero = '0'
    if number[0] == zero:
        return zero + cyryllic_translate_number(number[1:])

    if int(number) > 999_999_999_999:
        return number

    digits_number = len(number)

    t = '\u0483'  # Титло в числах.
    _thou = "҂"
    mdot = '·' 

    number = list(number)

    _res = []

    d = data["cyryllic"]["numbers"]  # Mind name `d`.

    def get_num(base_number: str) -> str:
        # Get Cyryllic basic number from the arabic "number",
        # where "number" is in ``d.keys()''.
        return d[base_number].split('|')[0]

    def _number_under_1000(number: str) -> str:
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
    res[-pos] = (item := res[-pos])[0], item[1] + t*(
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


def _cyryllic_transliterate(word: str, transliterate_number=True) -> str:
    """Preliminary transliterate the word to Cyryllic."""
    if re.fullmatch(r'[0-9]+', word):
        if transliterate_number:
            result = cyryllic_translate_number(word)
            return result
        return word
    
    word = word.replace(chr(8211), chr(45))

    _d = data["cyryllic"]
    d = _d["letters"]

    try:
        result = dict_transliteration(word, dest="cyryllic")
        assert result
        return result
    except:
        if '-' in word:
            gen_item: callable[[str], str] = lambda word_: \
            _cyryllic_transliterate(word_,
                transliterate_number=transliterate_number)
            result = '-'.join(gen_item(word_)
                              for word_ in word.split('-'))
            return result

    # What is the best way to do with it?
    digit = r'[0-9]'
    digits = r'[0-9]+'
    if (_index := re.search(digit, word)):
        _index = re.search(digits, word)
        start = _index.start()
        end = _index.end()
        parts = word[:start], word[start:end], word[end:]

        def transliterate_func(word_: str) -> str:
            return transliterate_to_cyryllic(
                word_,
                transliterate_number=transliterate_number
            )

        res = (
            _transliterate_func(parts[0])
            + parts[1]
            + _transliterate_func(parts[2])
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


def cyryllic_transliterate(text, transliterate_numbers=True):
    """Implement the transliteration from Russian to Cyryllic."""
    pattern = r'(?i)[-–а-яё0-9]+'
    repl = lambda match: \
    _cyryllic_transliterate(
        match.group(),
        transliterate_number=transliterate_numbers
    )
    res = re.sub(pattern,  # Is it really so?
                 repl,
                 text)
    return res


# === Section: Main ===========================================================


def translation(text: str, dest=None,
                transliterate_=True,
                transliterate_numbers=True,
                *, from_="russian") -> str:
    """Return the translation of text to the Old Slavonic at script `dest`."""
    if from_ != "russian":
        raise NotImplementedError(
            "Translation or transliterating from not "
            "Russian if not implemented"
            )
    if dest == "glagolitic":
        text = _translation(text)
        if transliterate_:
            text = glagolitic_transliterate(text,
                transliterate_numbers=transliterate_numbers
            )
        return text
    elif dest == "cyryllic":
        res = _translation(text)
        if transliterate_:
            res = cyryllic_transliterate(res,
                transliterate_numbers=transliterate_numbers
            )
        return res
    else:
        pass
