# placing this file exaclty as a separate may be somehow strange, so it's just
# (partially) developed here, may be with not the latest version
# NOTE: may different for difirent methods of working at Telegram
# NOTE: this file states only as an example and a part of developing, which
# than was continued at other files/places.
# -------

# --- For the test
def get_info_by_rule(pattern: str, kid, mentioned=[], add_d=None):
    """get word and meaning from the given dict

    :return: tuple (..) if found; None when not found
    when d is not given, pass::

        add_d=object of type dict

    type(d) is dict
    """
    if add_d:
        d = add_d
    if kid == 1:
        # meta: `*a*nswer`,  # *d*efinition  #
        #        `*q*uestion`
        possible = []
        for a, q in d.items():
            a = a.replace(')', '')
            a = a.replace('(', ',')
            a = a.lower().split(',')
            a = map(lambda ph: ph.strip(), a)
            filter_ = lambda k: k.lower() not in \
                (item.lower() for item in mentioned) and \
                    re.fullmatch(r'[-\w]+', k)
            a = list(filter(
                filter_,
                a
            ))

            if any(re.fullmatch(pattern.lower(), a_part) for a_part in a):
                possible.extend(a)
        word = random.choice(possible)
        return word, q
    elif kid == '3':
        searched = []
        for k in d:
            if re.fullmatch(pattern.lower(), k.lower()):
                meaning = d[k]
                searched += (k, meaning)
        k, meaning = random.choice(searched)
        return k, meaning        
# ^ for the test
# ---


import re
from urllib.parse import urlsplit
import warnings  # only for inform
import random
import requests  # really required

from aiogram import types
# ^ only for informing the user via bot/about errors

try:
    from form_word import iter_possible
    # ^ for tests
except ImportError:
    from .form_word import iter_possible

# other possibly required: bot_inform


# May be remaden to the class, such structure should be great
# template:
# class FindWordAndMeaning:
#     # define methods: get_from_dict, get_from_site(url) (static/class), etc.
#     # define constants:  __word_pattern etc.
#     # define help-methods: `one_iteration` at url-search etc.
async def get_word_and_meaning(pattern: 'str or dict',
                               message: types.Message,
                               mentioned=[]):
    r"""Get a word, which matches pattern, and meaning of a word.

    :param str pattern: a pattern, matches `(?i)[-а-яё\*\?]+`
    """
    # -----------------------------------------------------------------
    # *dev note*: this code may be partially strange, see version 1.0.4
    #             (maybe 1.0.5) or earlier to view the previous
    # considered to be UNDONE, both at all other similar code-parts
    # ----
    # compatibility:
    _word_pattern = pattern  # should be gone
    _pattern = pattern  # register word/name/some another
    # :param increase_allowed: REMOVED
    # :param search_mode: REMOVED (also see: _search_mode)
    # :key `normal` at `_word_pattern` (further): changed to `dictionary`
    #     *note*: ^ not essen.

    assert re.fullmatch(r'(?i)[-\w\*\?]+', pattern)
    keys = set(_word_pattern.keys())
    if type(_word_pattern) is dict and 'normal' in _word_pattern:
        _word_pattern['dictionary'] = _word_pattern['normal']
        del _word_pattern['normal']
    supported_search_types = {'dictionary', 'site'}
    if not keys.issubset(supported_search_types):
        warnings.warn("Unsupported search type passed")
    word_pattern = _word_pattern
    if type(_word_pattern) is str:
        # if not word_pattern:  # TODO great | TODO: check all this
            # raise BotException("Incorrect type of input: length is 0")
        # letter = word_pattern  # (TODO)
        func = lambda n: _word_pattern + '*'*(n - max(0,
                                                      len(word_pattern)))
        word_pattern = {
            # versions (required):
            'dictionary': _word_pattern + r'.*',
            'site': func
        }
    else:
        assert {'dictionary', 'site'}.issubset(set(keys))
        word_pattern = _word_pattern

    order = [
        ('dictionary', (None, 1,)),
        ('dictionary', (None, '3',)),
        ('site', ("https://loopy.ru/?word={0}&def=",
                  {
                      "word": 'word_pattern["site"]',
                      "def": None
                   })
        )
    ]

    def _allowed(s='-а-яё', *, add_s=''):
        return eval(f"r'(?i)[{s + add_s}]'")
    allowed = _allowed()  # *note* here are all symbols at word (not more/less)
    assert re.fullmatch(_allowed(add_s='*?'), word)
    del _allowed
    
    def search_at_dictionary(k, *, _d=_d):
        word_pattern_ = word_pattern['dictionary']
        word, meaning = None, None
        d = _d[k]
        result = get_info_by_rule(word_pattern_, k, mentioned)
        return result  # either None, or a tuple `(word, meaning)`

    def search_on_loopy(url, args: dict = None):
        # search on loopy.ru
        # :return: a tuple (exit_code, result),
        # either a (0, word, meaning), or (2, dict_)
        pattern = eval(args['word'])
        def_ = args['def']
        if def_ is not None:
            def_ = eval(def_)

        def _is_strict_word(word):
            return re.fullmatch(f'{allowed}+', word)
        is_strict_word = _is_strict_word(pattern)

        increase_allowed = not is_strict_word  # to look then, is meta
        if increase_allowed:
            maxn = 4  # best?
            possible = list(range(1, maxn))
        else:
            maxn = len(word_pattern)
            possible = [maxn - 1]
        searched = None

        # :part: define function
        def one_iteration(url):
            # :return: either tuple (1,), or a tuple: (exit_code, result),
            # where `result` is either a dict, or unpacked (word, meaning)
            # exit_code possible values: 0, 1, 2 (int)
            # 0 means success, 1 means `not found', 2 means `a message/exc'
            # is returned

            r = requests.get(url)
            nonlocal searched

            if increase_allowed:
                if r.status_code != 200:
                    return 2, {"msg": "Unexpected error"}

                text = r.text

                base = re.findall(r'<div class="wd">(?:.|\n)+?</div>', text)

                def word(item):
                    _pattern = r'<h3>.+?значение слова ([-\w]+).+?</h3>'
                    return re.search(_pattern, item).group(1)

                def meanings(item):
                    return re.findall(r'<p>(.+?)</p>', item)

                while base:
                    i = random.choice(range(len(base)))
                    item = base.pop(i).group()
                    word_ = word(item)
                    if word_ not in mentioned:
                        searched = word_
                        if not (m := meanings(item)):  # can it actually be?
                            pass
                        meaning = random.choice(meanings(item))
                        # *dev note*: mind adding `searched` to the mentioned
                        return 0, searched, meaning
                return 1,

            else:  # i. e. is_strict_word == True
                word = pattern
                if (sc := r.status_code) == 404:
                    msg = f"Слово {word!r} не найдено в словаре."
                    return 2, {"msg": msg}
                elif sc != 200:
                    msg = f"Непонятная ошибка. Код ошибки: {sc}."
                    return 2, {"msg": msg}
                rtext = r.text
                _rtext_part = rtext[rtext.find('Значения'):]

                try:  # version 1
                    rtext_part = _rtext_part
                    rtext_part = rtext_part[:rtext_part.index('</div>')]
                    finds = re.findall(r'<p>(.*?)</p>', rtext_part)[1:]
                    # :request question: is 1-st item here: ^ — a header?
                    assert finds
                except AssertionError:  # version 2
                    rtext_part = _rtext_part
                    rtext_part = rtext_part[:rtext_part.index('</ul>')]
                    finds = re.findall(r'<li>(.*?)</li>', rtext_part)
                    if not finds:  # can it actually be?
                        return 2, {"msg": 'Unexpected error'}
                res = random.choice(finds)
                meanings = res  # compatibility
                return 0, pattern, meanings

        # :part: search for word and meaning
        iterations_made = 0  # optional, iterations counter
        max_allowed_iterations = 100
        if not is_strict_word:
            while maxn <= 20 and \
            iterations_made < max_allowed_iterations:
                possible.append(maxn)
                n = possible.pop(random.choice(range(len(possible))))
                format_ = pattern(n)  # can be done, actually, for any pattern.
                # but it's not a goal of this work. See form_word for some help
                url = _url.format(format_)
                code, *result = one_iteration(url)
                iterations_made +=1
                maxn += 1

                if code == 1:  # not found
                    continue
                else:  # either found, or an exception occured
                    break
        else:
            word = pattern
            url = _url.format(word)
            code, *result = one_iteration(url)
        
        # :part: get results, if weren't received earlier
        if code == 0:
            word, meaning = result
        elif code == 1:  # shouldn't come here ...unless `searched is None`
                         # occures at `not is_strict_word` case, see code
            pass  # result wasn't received
        elif code == 2:
            return 2, result  # result is message/exception data
        else:  # not implemented, is a sample code
            pass

        if searched is None and not is_strict_word:
            if iterations_made >= max_allowed_iterations - 1:
                # do_something_really_causing()  # unexpected, see
                return 2, {"msg": "Unexpected error"}
            # commented:
            """'''
            msg = (
            "Wow!😮 How can it happen? I had found no words for this pattern."
            "❌Game is stopped. Realise move's skip to continue"  #!
            )  # *question*: continuing game -- ?
            '''"""
            # return 2, {"iterations_made": iterations_made}  # Or so

        return 0, word, meaning

    async def search_at(source_type: str = 'dictionary',
                        parameters=None,
                        *,
                        return_on_fail: 'callable or object to return' = 1):
        # return:
        # rtype: int or tuple
        try:
            if source_type == 'dictionary':
                dict_, *params = parameters
                return 0, *search_at_dictionary(*params, _d=dict_)
            elif source_type == 'site':
                _url, *args = parameters
                netloc = urlsplit(_url).netloc
                if netloc == "loopy.ru":
                    code, *result = search_on_loopy(_url, args)
                    if code == 2:
                        if "msg" in result:
                            await message.reply(result['msg'])
                        elif 'bot_inform' in result:
                            await bot_inform(result['bot_inform'], 
                                             **result['kwargs'])
                        else:
                            pass
                        return 1,  # word/meaning not found
                    # otherwise code is 0, do the action: return
                    return 0, *result
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        except NotImplementedError as e:
            raise e
        except Exception as e:
            if callable(return_on_fail):
                return return_on_fail(e)    
            return return_on_fail,
        
    async def whole_search():
        # perform search throw the all requested sources; see `order`
        # :return: either 1 (int), or a tuple (word, meaning)
        while order:
            item = order.pop(0)
            source_type, parameters = item
            try:
                search_result = await search_at(source_type, parameters)
            except NotImplementedError:
                continue
            if search_result != 1 and search_result != (1,):
                _, result = search_result
                return result
        return 1  # not found
    result = await whole_search()
    if result == 1:
        return  # All (?) is done
    
    word, meaning = result
    word = word.capitalize()

    return 0, word, meaning


# test
if __name__ == '__main__':
    pass
