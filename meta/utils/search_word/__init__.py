import re
from urllib import urlsplit
import warnings  # only for inform
import random
import requests  # really required

from aiogram import types
# ^ only for informing the user via bot/about errors

from .form_word import iter_possible


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

    def _is_strict_word(word):  # required
        return re.fullmatch(f'{allowed}+', word)
    # is_strict_word = _is_strict_word(word_pattern)

    order = [
        ('dictionary', (None, 1,)),
        ('dictionary', (None, '3',)),
        ('site', ("https://loopy.ru/?word={0}&def=",
                  'word_pattern["site"]')
        )
    ]
    def _allowed(s='-а-яё', *, add_s=''):
        return eval(f"r'(?i)[{s + add_s}]'")
    allowed = _allowed()  # *note* here are all symbols at word (not more/less)
    assert re.fullmatch(_allowed(add_s='*?'), word)
    del _allowed
    
    def search_at_dictionary(k, *, _d=_d):
        word_pattern_ = word_pattern['normal']
        word, meaning = None, None
        d = _d[k]
        result = get_info_by_rule(word_pattern_, k, mentioned)
        if not result:
            return
            # continue
        word, meaning = result
        return word, meaning

    def search_on_loopy(url, pattern=word_pattern['site']):
        # search on loopy.ru
        pattern_ = pattern = word_pattern['site']
        if _is_strict_word(pattern_):
            _search_mode = 0
        else:
            _search_mode = 1  # see code

        increase_allowed = _search_mode == 1  # to look then, is meta
        if increase_allowed:
            maxn = 4  # best?
            possible = list(range(1, maxn))
        else:
            maxn = len(word_pattern)
            possible = [maxn - 1]
        searched = None

        # :dev note: search mode -- either 'as strict', or 'as float'
        if not increase_allowed:
            search_mode = 'as strict'  #! *note*: <- `search_mode`
        else:
            search_mode = 'as float'

        def one_iteration(url):
            r = requests.get(url)
            nonlocal searched

            if search_mode == 'as float':  # `search_mode`
                text = r.text

                base = re.findall(r'<div class="wd">(?:.|\n)+?</div>', text)
                base = list(base)

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
                        meaning = random.choice(meanings(item))
                        # *dev note*: mind adding `searched` to the mentioned
                        return 0, searched, meaning

            elif search_mode == 'as strict':
                # here is considired: `is_strict == true`
                if (sc := r.status_code) == 404:
                    pattern = word_pattern['site']
                    msg = f"Слово {pattern!r} не найдено в словаре."
                    return {"msg": msg}
                elif sc != 200:
                    msg = f"Непонятная ошибка. Код ошибки: {sc}."
                    return {"msg": msg}
                rtext = r.text
                _rtext_part = rtext[rtext.find('Значения'):]

                # *dev question*: is this try-except structure great?
                try:  # version 1
                    rtext_part = _rtext_part
                    rtext_part = rtext_part[:rtext_part.index('</div>')]
                    finds = re.findall(r'<p>(.*?)</p>', rtext_part)[1:]
                    # ^ *request question*: 1-st item here — a header?
                    assert finds
                except AssertionError:  # version 2
                    rtext_part = _rtext_part
                    rtext_part = rtext_part[:rtext_part.index('</ul>')]
                    finds = re.findall(r'<li>(.*?)</li>', rtext_part)
                    if not finds:
                        text = \
                        f"A <b>great</b> error occured: haven't found a meaning"
                        " for {word!r}."
                        answer_d = {
                            "bot_inform": text,
                            'kwargs': dict(parse_mode='HTML')
                        }
                        return answer_d
                res = random.choice(finds)
                meanings = res  # compatibility
                return 0, pattern, meanings
            return (1,)

        if increase_allowed:
            while not searched and maxn <= 20:
                possible.append(maxn)
                n = possible.pop(random.choice(range(len(possible))))
                format_ = pattern(n)
                url = "https://loopy.ru/?word={}&def=".format(format_)
                result = one_iteration()
                maxn += 1
            if result is None:
                continue
            code, result = result
            elif code == 2:
                return  # *dev note* as all is done
            else:
                break
        else:
            word = pattern
            url = f'https://loopy.ru/?word={word}&def='
            result = one_iteration(url)
        # -*- part -*- #
        if code == 0:
            word, meaning = result

        if code == 0:
            _, word, meaning = result
        elif code[0] == 1:  # *question/meta-temporary*
            # ^ required? see code  # TODO (not here): change tokens and/or
            # other params, were at .env-todo (commit 181e106)
            code, msg = code
            return msg

        if searched is None and _search_mode == 1:  # /`... increase_allowed`:
            msg = (
            "Wow!😮 How can it happen? I had found no words for this pattern."
            "❌Game is stopped. Realise move's skip to continue"  #!
            )  # *question*: continuing game -- ?
            return {"msg": msg}
            # OR: `return {"exc": iterations_made}`  # <- undone
        word = searched
        return word, meaning
    async def search_at(source_type: str = 'dictionary',
                        parameters=None,
                        *,
                        return_on_fail: 'callable or object to return' = 1):
        # really this? see code
        try:
            if source_type == 'dictionary':
                dict_, *params = parameters
                return search_at_dictionary(*params, _d=dict_)
            elif source_type == 'site':
                _url, *params = parameters
                netloc = urlsplit(_url).netloc
                if netloc == "loopy.ru":
                    result = search_on_loopy(_url.format(*map(eval, params)))
                    if type(result) is dict:
                        if "msg" in result:
                            await message.reply(result['msg'])
                        elif 'bot_inform' in result:
                            await bot_inform(result['bot_inform'], 
                                             **result['kwargs'])
                        else:
                            pass
                        return (2,)
                    return result
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        except NotImplementedError as e:
            raise e
        except Exception as e:
            if callable(return_on_fail):
                return return_on_fail(e)    
            return return_on_fail
        
    async def whole_search():
        while order:
            item = order.pop(0)
            source_type, parameters = item
            try:
                result = await search_at(source_type, parameters)
            except NotImplementedError:
                continue
            if result is not None and result != 1:
                return result
        return 2  # not found
    result = await whole_search()
    if result == 1:
        pass
    if result == 2:
        return
    word, meaning = result
    word = word.capitalize()

    return 0, word, meaning
    ### here the process ends # see code
    # was: try-except (not more)
