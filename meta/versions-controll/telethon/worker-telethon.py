# -*- coding: utf-8 -*-
# version: telethon:v1.0.6-editing

# THIS CODE AND APP ARE FREE FOR USAGE AND MAINTAINED & DISTRIBUTED UNDER THE
# TERMS OF *MIT License*. See LICENSE for more info.
# =============================================================================
# Main file, written preferably with PEP8, required modules/libraries
# are in requirements.txt.
# 
# **PLEASE NOTE:** The `version: lib:v_name` is important at the beginning of
# this file. It is parsed while writing this file to the root in order to get
# the most recent information about what version of app is used and write it 
# to the "current-version.txt" immediately.
#
# -----------------------------------------------------------------------------
# See also:
# - README for some info
# - meta/metalog for some instant/following/current changes
# - config.py to view or change the configurations; also, .env or its analogues
# - launcher and similar to have a help (maybe) with launching the bot app
# Requires Python >=3.8 to allow the use of `:=`
# set the required version at runtime.txt (see also: runtime info at [1])
# 
# [1]: https://devcenter.heroku.com/articles/python-runtimes#supported-runtime-versions
# 
# -----------------------------------------------------------------------------
# 
# Developer notes
# ---------------
# 
# - this can help to ignore further triggers for an exact update:
#   `raise events.StopPropagation`
# - see *questions*/*question*
# - see *mark* (maybe), and also: file metalog
# - see the `aiogram` version worker[.py] for info
# - comments at this and other files use the syntax of:
#    * Markdown (plain/GitHub, mainly *word* and so on);
#    * ReST (or related meta-syntax, styled as ReST)
#      *note*: ReST is ReStructuredText
#    * Several Markdown-styled, but not really existed, e. g. `word_or_text'
# - **important**: to solve:
#    + `TODO`, `test` (just less more important),
#    + *question*/*questions* (or simply question with no symbols behind)
# - noting versions at some places (e. g. functions/classes) to show, which of
#   version they are ('at which version'/when they were written/added)
#   + marking versions: either 'version-name', or 'v:<comment>', e. g. when
#     comment is "undefined"
#     * 'to-check' means "nearly final version, to check still, and merge"
# - may use 'one case'/another to mark (with "'"), which words are included.
# - TODO: merge versions (1.0.6-editing stage, before 1.0.6 full)
#
# Meta
# ----
# 
# versions stages:
# '-editing' (means editing in process)
# rcN means realise candidate; if no issues are mentioned -- considired to
# be ready
# 
# See also: PEP440.
# 
# Notes syntax
# -------------
# 
# - Mixed Markdown and Sphinx, also using some Sphinx-styled maybe-not-existed
#   commands.
# - `re` expressions
# - Such as:
#   + [...] -- optional part
#   + <var>, meaning an exact command, inserted at a place of the "<var>".


import random
import re
import asyncio
import typing
import logging
import json
from html import escape as html_escape

import requests
import telethon
from telethon import sync  # Maybe not required, but let it be

from telethon.tl.types import InputWebDocument
from telethon import errors
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.custom.button import Button
from telethon.tl.types import (
    MessageEntityUnknown,  # *question*: what is it?
    MessageEntityMention,
    MessageEntityMentionName,
    InputMessageEntityMentionName
)
from telethon import events
from telethon.events.inlinequery import InlineQuery

from config import (
    # Pictures/media:
    A_CYRYLLIC, A_GLAGOLIC, A_LATER_GLAGOLIC,
    # configparser:
    configparser, NoSectionError,
    # Chats & channels:
    CHANNEL, TEST_CHAT, SPEAK_CHAT, HEAD_CHAT,
    # Connected with bot:
    bot, TOKEN, BOT_ID, BOT_USERNAME, TOKEN_INIT,
    # Game words:
    WORDS_GAME_PATTERN, GAME_WORDS_DATA, ANY_LETTER,
    # Inline:
    INLINE_EXAMPLES, NAMES_REPLACE, CACHE_TIME, COMMON_THUMB_CONFIG,
    # Greeting
    FILE_GREETING, DEFAULT_GREETING_EVAL_SOURCE,
    # Other:
    ADMINS, LOGGING_CHAT, CHAT_LOGS_MODE_ALL, HELP_URL,
    PROD, PASSWORD_ENABLED, ON_HEROKU, UIDS_BASE,
    LOCAL_LOGS
)
from functions import translation, glagolic_transliterate
from functions import d as _d
from meta.edit_date import short_cright, full_cright  # <- meta


# Set logging
logformat = '[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s'
logging.basicConfig(format=logformat,
                    level=logging.WARNING)


edit_note = r"edited at July, the 12th"
# ^ dummy, to check for updates while running.

# checked
async def bot_inform(text, chat_id=LOGGING_CHAT, type_=None, **kwargs):
    if type_ is not None and type_ not in CHAT_LOGS_MODE_ALL:
        return
    await bot.send_message(chat_id, text, **kwargs)

# TODO Do this (great). Appears to be more a template then a complete func.
class BotException(Exception):
    def __init__(self, *args, extra={}, kwargs={}):
        super(BotException, self).__init__(*args, **kwargs)
        self.extra = extra
        chat_id = extra.get('chat_id')
        sender = extra.get('sender')
        sender.id = sender.id if 'id' in dir(sender) else sender.user_id
        # sender = telethon.utils.get_peer(peer)  # *question*: helpful?
        if args:
            exception = self.args[0]
        else:
            exception = "no info given"

        text = f"""\
**An exception occured**
 - `chat_id`: __{chat_id}__
 - `sender.id`: __{sender.id}__
 - `exception`: __{exception}__
"""

        future = bot_inform(text, type_='bot-exception', parse_mode='md')
        asyncio.get_event_loop().run_until_complete(future)

# d = dict(chat_id='chat_id', sender=telethon.tl.types.PeerUser(0))
# raise BotException('test', extra=d)  # test


loop = asyncio.get_event_loop()
prod_word = "" if PROD else 'not '
on_heroku = 'yes' if ON_HEROKU else 'no'
text = f"""\
Launched the bot.
Is <u>{prod_word}the production</u> version.
Is whether on Heroku: <u>{on_heroku}</u>.
"""
future = bot_inform(text, type_="launch", parse_mode='html')
loop.run_until_complete(future)

del text, ON_HEROKU, on_heroku, future, loop

# v1.0.6
# checked
def _cmd_pattern(cmd: str, *, flags='i') -> str:  # Internal
    if flags:
        _flags_add = r'(?' + flags + r')'
    else:
        _flags_add = ""
    cmd_pattern = _flags_add + r'/' + cmd + r'(?:@' + BOT_USERNAME + r')?'
    return cmd_pattern

# v1.0.6
# checked
def commands(*cmds, flags=None) -> str:  # Internal
    if flags is not None:
        kwargs = {'flags': flags}
    else:
        kwargs = {}
    if len(cmds) == 1:
        cmd_styled = cmds[0]
    else:
        cmd_styled = r'(?:' + '|'.join(cmds) + r')'
    return _cmd_pattern(cmd_styled, **kwargs)

# v1.0.6
# checked
def feature_exists(fid):  # Internal
    d = {
        'teach_word': False
    }
    if fid in d:
        return d[fid]
    return False


# v1.0.6
# checked
async def is_participant(user_id, of=HEAD_CHAT):
    """User is participant of chat `of`, returns bool."""
    try:
        return not (await bot.get_permissions(of, user_id)).has_left
    except (ValueError, errors.UserNotParticipantError):
        return False


# v:1.0.6rc1
# Check, test, merge.
# TODO Test
def enabled(case=True, *, is_coro=False):  # Internal
    """Help-function to enable/disable the required trigger.

    Internal function. See code. Works both with functions and coroutines.
    Pass is_coro=True to work with coroutines. Defaults to False.

    .. example::

        # Example 1
        @enabled(case=True)
        def func():
            ...

        # is same as `def func(): ...`. While:

        # Example 2
        @enabled(False, is_coro=True)
        async def func():
            pass

        # is equal to

        async def func():
            return  # Pay attention to this! Just `return`.
    """
    # This appears to be more a template, then a wrapper function to any such
    # func. The task may be undone for functions, which have default
    # arguments/kw, and for functions names; here there is no sense.
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            def _enabled(case_):
                if type(case_) is bool:
                    return bool(case_)
                elif callable(case_):
                    # Does it really work so?
                    args_defaults = func.__defaults__
                    kwargs_defaults = func.__kwdefaults__
                    code = func.__code__
                    kwonlyargcount = code.co_kwonlyargcount
                    argcount = code.co_argcount
                    if not kwargs_defaults:
                        kwargs_defaults = {}
                    if not args_defaults:
                        args_defaults = ()

                    kwargs_ = kwargs  # kwargs to call with
                    args_ = args  # args to call with

                    args_with_no_value_count = len(args) + \
                        len(kwargs) - \
                        len(args_defaults)
                    for k in kwargs_defaults:
                        kwargs_.setdefault(k, kwargs_defaults[k])

                    args_names = code.co_varnames
                    args_names = args_names[:argcount + kwonlyargcount]
                    used_args_names = set(kwargs_defaults.keys()) - set(kwargs)
                    used_args_count = len(used_args_names)

                    lack = argcount - used_args_count
                    args_ += args_defaults[lack:]

                    return case_(*args_, **kwargs_)
                elif type(case_) is str:
                    case_ = eval(case_)
                    return _enabled(case_)
                else:
                    raise TypeError(
                        "Internal error: "
                        "case_ must be one of"
                        " bool, callable, str"
                        )
            if not _enabled(case):
                if is_coro:
                    async def dummy():
                        # `await dummy()` -> `None`
                        """Dymmy function. dummy() is a coroutine object."""
                    return dummy()
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator


# v1.0.6
async def _add_user(user_id):
    """Add ID to the base. Comments are allowed."""
    filename = UIDS_BASE
    with open(filename, 'a') as f:
        pass
    with open(filename, 'r', encoding='utf8') as f:
        data = f.read()  # only to read
    data_ = ""  # to write
    if data and data[-1] != '\n':
        data_ += '\n'  # add newline if absent
    if (suid := str(user_id)) not in data:
        text = 'New user: \
<a href="tg://user?id={0}">{1}</a>\nuser_id: {0}'.format(
            user_id, "User")
        await bot_inform(text, type_='new user', parse_mode='html')
        data_ += suid + '\n'
    with open(filename, 'a', encoding='utf8') as f:
        f.write(data_)

# v1.0.6
def full_name(user):
    """Full name of a user."""
    return f'{user.first_name}{" " + u if (u := user.last_name) else ""}'

# v1.0.6
def user_text_mention(user, fill=None) -> str:
    """Text mention of a user, i. e. a hyperlink."""
    # :param fill: Text to insert at mention.
    # Link: https://core.telegram.org/bots/api#formatting-options.
    if fill is None:
        filling = full_name(user)
    else:
        filling = fill
    return f'<a href="tg://user?id={user.id}">{filling}</a>'

# v1.0.6
def load_users():
    # **Note**: Return is a generator object!
    with open(UIDS_BASE, encoding='utf-8') as f:
        users = map(eval, f.read().strip().split('\n'))
    return users


# To test, assumed to be ready
def get_info_by_rule(pattern: str, kid, mentioned=[], add_d=None):
    """Get word and meaning from the given dict

    :return: tuple `(word, meaning)` if found; `None` when not found
    when `d` (see code) is not given, pass::

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
                possible.append((a, q))  # to check
        word, q = random.choice(possible)
        return word, q
    elif kid == '3':
        searched = []
        for k in d:
            if re.fullmatch(pattern.lower(), k.lower()):
                meaning = d[k]
                searched.append((k, meaning))
        k, meaning = random.choice(searched)
        return k, meaning


# - Was copied from the version with aiogram;
# - And is currently developed (2021-07-10: morning and later) at this file;
# - Same to previously stated function (`get_info_by_rule`)
# 
# from there:
# ---
# May be remaden to the class, such structure should be great.
# 
# template for it:
# class FindWordAndMeaning:
#     # define methods: get_from_dict, get_from_site(url) (static/class), etc.
#     # define constants:  __word_pattern etc.
#     # define help-methods: `one_iteration` at url-search etc.
async def get_word_and_meaning(pattern: 'str or dict',
                               message: events.NewMessage,
                               mentioned=[]):
    r"""Get a word, which matches pattern, and meaning of a word.

    # :param str pattern: a pattern, matches `(?i)[-а-яё\*\?]+`  # not so
    :return: either `None`, or `(word, meaning)`
    """
    # VERSIONS:
    # - **important**: see `most-recent.txt'
    # - worker (this) -- current, telethon, most recent
    # - worker-a -- not so recent, maybe just a few
    # - worker-telethon and worker-aiogram are old
    # -----------------------------------------------------------------
    # *dev note*: this code may be partially strange, see version 1.0.4
    #             (maybe 1.0.5) or earlier to view the previous
    # considered to be **UNDONE**, both at all other similar code-parts
    # :pattern's keys:
    # - is either 'normal' (='dictionary', changed to this), or 'site'
    # - changing to `dictionary`; it is not essential.
    # *dev note*: this code may be strange at least because of it's
    # aim only for satisfying 2 cases: (letter)**..* and `whole_word`
    # (i. e. search by patterns :re_pattern:`f"{letter}.*"` and exact
    # word pattern). However, writing a comple
    # ----
    _pattern = pattern  # register word/name/'place to work at'

    if type(_pattern) is dict and 'normal' in _pattern:
        _pattern['dictionary'] = _pattern['normal']
        del _pattern['normal']
    
    if type(_pattern) is str:
        if '?' in _pattern:
            raise NotImplementedError
        # _pattern = re.sub(r'[^\w?]', '*', _pattern)
        # case of `{letter}**.*`, just named `_pattern=letter`
        assert re.fullmatch(r'(?i)[-\w\*\?]+', _pattern)
        # *question*: should `assert _pattern` be?
        func = lambda n: _pattern + '*'*(n - max(0,
                                                 len(_pattern)))
        word_pattern = {
            # versions (required):
            'dictionary': _pattern + r'.*',
            'site': func
        }
    else:
        assert type(_pattern) is dict
        supported_search_types = {'dictionary', 'site'}
        keys = set(_pattern.keys())
        if not keys.issubset(supported_search_types):
            warnings.warn("Unsupported search type passed")
        assert {'dictionary', 'site'}.issubset(set(keys))
        word_pattern = _pattern

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
    assert re.fullmatch(_allowed(add_s='*?') + r'+', word_pattern["site"])
    del _allowed
    
    # :define function: search at dictionary
    def search_at_dictionary(k, *, _d=_d):
        pattern = word_pattern['dictionary']
        d = _d[k]
        result = get_info_by_rule(pattern, k, mentioned)
        return result  # either None, or a tuple `(word, meaning)`

    # :define function: search on site `loopy.ru`
    def search_on_loopy(url, args: dict = {}):
        # search on loopy.ru
        # :return: a tuple (exit_code, *result),
        # either a (0, word, meaning), or (2, dict_)
        if not 'word' in args:
            raise Exception  # nothing should be done
        pattern = eval(args['word'])
        def_ = args['def']
        if def_ is not None:
            def_ = eval(def_)

        def _is_strict_word(word):
            return re.fullmatch(f'{allowed}+', word)
        is_strict_word = bool(_is_strict_word(pattern))
        print(is_strict_word)

        increase_allowed = not is_strict_word  # to look then, is meta
        if increase_allowed:
            maxn = 4  # best?
            possible = list(range(1, maxn))
        else:
            maxn = len(pattern)
            possible = [maxn - 1]
        searched = None

        # :part: define function
        def one_iteration(url):
            # :return: a tuple `(exit_code, result)`
            # .. exit_code-info::
            #     
            #     - 0 means success,
            #     - 1 means `not found',
            #     - 2 means `a message/exc' is returned.
            # 
            # .. result-info::
            # 
            #     code == 1 (not found) --> `None`
            #     code == 2 --> a dict, is data of 'a message'/exc
            #     code == 0 (success) --> a tuple `(word, meaning)`
            # where code is exit_code
            
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
                        return 0, (searched, meaning)
                return 1, None

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
                return 0, (pattern, meanings)

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
                code, result = one_iteration(url)
                iterations_made +=1
                maxn += 1

                if code == 1:  # not found
                    continue
                else:  # either found, or an exception occured
                    break
        else:
            word = pattern
            url = _url.format(word)
            code, result = one_iteration(url)
        
        # :part: get results, if weren't received earlier
        if code == 0:
            word, meaning = result
        elif code == 1:  # shouldn't come here, unless `searched is None`
                         # occures when `not is_strict_word` is true
            pass  # result wasn't received
        elif code == 2:
            return 2, result  # result is message/exception data
        else:  # not implemented; is a sample
            pass

        if searched is None and not is_strict_word:
            if iterations_made >= max_allowed_iterations - 1:
                return 2, {"msg": "Unexpected error"}
            # commented:
            """'''
            msg = (
            "Wow!😮 How can it happen? I had found no words for this pattern."
            "❌Game is stopped. Realise move's skip to continue"  #!
            )  # *question*: continuing game -- ?
            '''"""
            # return 2, {"iterations_made": iterations_made}  # Or so

        return 0, (word, meaning)

    # :define function: search at given source
    async def search_at(source_type: str = 'dictionary',
                        parameters=None,
                        *,
                        return_on_fail: 'callable or object to return' = 1):
        # :exit_code info: 0 means found, 1 means fail
        # :return: (exit_code, result)
        # exit_code == 0 --> result is `(word, meaning)`
        try:
            if source_type == 'dictionary':
                dict_, *params = parameters
                return 0, search_at_dictionary(*params, _d=dict_)
            elif source_type == 'site':
                _url, *args = parameters
                netloc = urlsplit(_url).netloc
                if netloc == "loopy.ru":
                    code, result = search_on_loopy(_url, args)
                    if code == 2:
                        if "msg" in result:
                            await message.reply(result['msg'])
                        elif 'bot_inform' in result:
                            await bot_inform(result['bot_inform'], 
                                             **result['kwargs'])
                        else:
                            pass
                        return 1, None  # word/meaning not found
                    # otherwise code is 0, do the action: return
                    return 0, result
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        except NotImplementedError as e:
            raise e
        except Exception as e:
            if callable(return_on_fail):
                return return_on_fail(e),
            return return_on_fail,
    
    # :define: whole search    
    async def whole_search():
        # perform search through the all requested sources; see `order`
        # :return: either `1`, or a tuple `(word, meaning)`
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

    return word, meaning

# tests
pattern_1 = {
    "normal": "слов.+",
    "site": "слов*"
}
print(asyncio.run(get_word_and_meaning(pattern_1, None)))
pattern_2 = {
    "normal": "сила",
    "site": "сила"
}
print(asyncio.run(get_word_and_meaning(pattern_2, None)))
raise SystemExit(0)


# checked
async def make_move(message, letter, mentioned):
    """Make move at a game, checking for a word, whether exists."""
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, 'typing')
    result = await \
        get_word_and_meaning(letter, message, mentioned=mentioned)
    if result:
        word, meaning = result
        msg = word + ' (' + meaning + ')'
        return word, msg
    else:  # *question*: what?
        raise Exception


# Stage:
# - [ ] Look throught for the usage of make_move etc., solve to be great;
# - [ ] Check; commit.
# - [ ] (NOTE) Also: see *question*/*questions*.
async def play_words(event):
    # """Да, тут считают, что е и ё -- одна буква."""
    # :param current: is it required?  # *question*

    c = configparser.ConfigParser()
    chat_id = str(event.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Ошибка: не найдено игру."
        await event.reply(msg)
        raise NoSectionError
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    cur_letter = section["letter"]
    mentioned = eval(section["mentioned"])

    dot = '.' * (random.choice([0, 1, 2]) < 1)
    if (n := event.sender.id) in order and \
        (match := re.fullmatch(WORDS_GAME_PATTERN, event.text)):
        if event.is_private and not (
            #               Considered to be meaning of a word, is ignored
            # Matches '![ ]word[...]'.          vvvvvvvvv
            re.fullmatch(r"(?s)!\s?(?:[-\w]+)(?:\s*\(.+\))?", event.text)
            or  #                     ^^^^^^ Is word
            # Message is a reply to the appropriate sender's message
            ((reply := get_reply_message(event)) and  #(?)
             reply.from_user.id == order[current - 1])
        ):
            # Message is neither a reply, nor a message with expacted pattern.
            return
        if n != order[current]:
            answer_msg = (
                f"Не твой сейчас ход{dot}"
                # " Ход игрока" + user_text_mention(user) + '!'
            )
            await event.reply(answer_msg)
            return  #~
        word = match.group(1)
        print(word)  # test
        if cur_letter != ANY_LETTER and \
        word[0].lower().replace('ё', 'е') != cur_letter:
            answer_msg = f"На букву {cur_letter!r}{dot}"
            await event.reply(answer_msg)
            return
        if requests.get(f"https://loopy.ru/?word={word}&def=").status_code \
            == 404:
            answer_msg = "Вау. Кажется, я не знаю этого слова. Хотя, \
возможно, оно лежит где-то на полке в папке data, но я не смотрел." \
 + f" Переходи, пожалуйста{dot}" + " Что \
это слово значит? (Ход не засчитан. Потом либо напиши ответом на это \
сообщение толкование слова, я его в словарь запишу, либо назови другое \
слово. И вообще, это not implemented ещё{dot})"*feature_exists('teach_word')
            await event.reply(answer_msg)
            return
        if word.casefold() in map(lambda s: s.casefold(), mentioned):
            answer_msg = f"Слово {word!r} уже было в этой игре{dot}"
            await event.reply(answer_msg)
            return
        mentioned.append(word)
        res = word.lower().rstrip('ь')
        assert re.fullmatch(r"(?i)[-а-яё]+", res)  # (*question*) required?
        letter = res[-1]
        section["letter"] = letter
        current = (current + 1) % len(order)
        if int(order[current]) == BOT_ID:
            print("Bot's move at game 'words'")  # test

            try:
                answer, msg = await make_move(event, letter, mentioned)
            except Exception as e:
                print(e)
                return

            current = (current + 1) % len(order)

            mentioned.append(answer)

            next_let = answer.lower().rstrip('ьъ')[-1]
            if next_let == 'ё': next_let = 'е'
            section["letter"] = next_let

            await event.reply(msg)

        section["current"] = str(current)
        section["mentioned"] = str(mentioned)

        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
    elif not n in order:
        # msg = ...
        # await event.reply(msg)
        pass

    raise events.StopPropagation


# v1.0.6rc1
# add all users from either `NewMessage` or `InlineQuery`
@bot.on(InlineQuery)
@bot.on(events.NewMessage)
async def add_user(event):
    await _add_user(event.sender.id)


# v1.0.6rc1
# here is a test-start, may be used for tests
# see the `start` command
@enabled(is_coro=True)
async def test_start_message(event):
    if event.sender.id not in ADMINS:
        return

    msg = "Some msg.\n\n\
Ввод в режиме inline (перевод):"
    choices = INLINE_EXAMPLES
    url = "https://telegra.ph/Test-02-20-154"  # test
    example = random.choice(choices)
    switch_cur_chat_button = Button.switch_inline(
        "Да", example, same_peer=True
    )
    go_to_help_message = Button.url(
        "Open help (test)", url=url
    )
    buttons = [
        [switch_cur_chat_button],
        [go_to_help_message]
    ]
    await event.respond(msg, buttons=buttons)

    return "Success"  # required?


# v1.0.6rc1
# examples for it:
# /do -password=pw -action=eval code
# /do -password=pw -time=mm:ss -action=exec code
# exact example:
# /do -password={some_password} 1+2 (it gives 3)
@bot.on(events.NewMessage(pattern=commands('do')))
async def do_action(event):
    # **NOTE**:
    # Some imports were made exactly here,
    # as this function's call is uncommon
    sid = event.sender.id
    if sid not in ADMINS:
        return

    # Assume an appropriate folder exists
    filename = LOCAL_LOGS
    mid = "{},{}".format(event.chat.id, event.id)

    try:  # to let the polls tracker go further
        with open(filename, 'rt', encoding='utf-8') as f:
            _data = f.read().split('\n')
        if mid in _data:
            return  # Was already answered
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)
    finally:
        with open(filename, 'at', encoding='utf-8') as f:
            f.write(mid)
            f.write('\n')

    pattern = (
        _cmd_pattern('do', flags='is')  # command's pattern
        + r"(?: {1,2}-password=(" + r'\S+' + r"))?"  # password
        + r"(?:\s+-time=(\d{,2}:\d{,2}))?"  # time
        + r"(?:\s+-action=(exec|eval))?"  # action (type)
        + r"\s+(.+)"  # the code
    )
    string = event.text
    if not (match := re.fullmatch(pattern, string)):
        print(pattern, string)
        return
    pw, time, *other = match.groups()
    if PASSWORD_ENABLED:
        from config import password as _password
        if time is not None:
            time = time.split(':')
        password = _password(sid, time=time)
        print('pw:', password)  #!
        if pw != password:
            return
    action, code = other
    if action is None:
        action = 'eval'
    action0 = action
    action = eval(action)
    try:
        if action is eval:
            res = eval(code)
            await event.reply(str(res))
        elif action is exec:
            exec(code)
    except Exception as e:
        msg = f"Ошибка. __{e}__"  # to test
        await event.reply(msg, parse_mode='md')

    raise events.StopPropagation


# TODO:
# - [ ] Test
# - [ ] See: test_start
@bot.on(events.NewMessage(pattern=commands('start')))
async def start(event):
    """Answer the start message.

    Start message is a text message, starts with '/start'.
    See also: https://core.telegram.org/bots#commands.
    """
    p = commands('start') + r'\s+[-=]?test'
    if 'test_start_message' in globals() and re.fullmatch(p, event.text):
        result = await test_start_message(event)
        if result:  # If result appears `None`, consider message
                    # as unanswered and go to answer as to normal
                    # message `/start`
            return
    sid = event.sender.id
    cid = event.chat.id
    test = False

    header = r"\[test]"*test
    # Notes on happened:
    # ~0:01 at 2021-02-08: once said "can't parse ent.",
    # after reload — with some extra ent. ...
    # Then — without (one '"'' was rem.), but wrong, not working.
    # Then — again once "can't ..." (byte offset ?552)
    msg = f"""\
{header}
Основные команды:
/start — это сообщение
/words — игра в слова. Глянь /words help.
/help — помощь по боту
/meaning — значение слова. Глянь /meaning для справки.

`Перевод текста`
См. /help.
"""
    allow_to_all = False
    if allow_to_all or await is_participant(sid):
        async def invite_link(chat_id_):
            try:
                _link = await bot(ExportChatInviteRequest(chat_id_))
                link = _link.link
            except:
                link = "не найдено"
            return link

        channel = await invite_link(CHANNEL)
        chat = await invite_link(HEAD_CHAT)

        msg += f"""
Ссылки на материалы по курсу:
🔸 канал: {channel}
🔸 чат курса: {chat}
"""
    msg += """ 
Тест перевода:
"""
    choices = INLINE_EXAMPLES
    example = random.choice(choices)
    switch_button = Button.switch_inline("Да", example, same_peer=True)
    await event.respond(msg, parse_mode='md',
        buttons=switch_button,
        link_preview=False)

# v1.0.6rc1
@bot.on(events.NewMessage(pattern=commands("add_user", "add_users")))
async def add_user_via_message(event):
    sids = []
    if (m := get_reply_message(event)):
        sid = m.sender.id
        await _add_user(sid)
        await event.respond("Пользователь добавлен.")
    else:
        pass
    raise events.StopPropagation


# v1.0.6-editing
# TODO:
# - [ ] See `TODO` etc., solve it all.
# - [ ] Check.
#     + In particular: the default invite message.
# - [ ] Test.
@bot.on(events.NewMessage(pattern=commands('help')))
async def send_help_msg(event):
    """Answer the help message.

    Help message is '/help' or the same with parameters.
    See also: https://core.telegram.org/bots#commands.
    """
    # TODO: to test: `🔸text` or `🔸 text` -- which looks better?
    # Same to all, where this/such a thing appears
    pattern = commands('help') + r'\s+[-+]?full'
    is_full = re.fullmatch(pattern, event.text)
    is_not_full = not is_full
    msg = f"""\
Переводчик на старославянский язык. Правило перевода: ввести в чате\
 слово "@{BOT_USERNAME}\
\" и, после пробела, — текст для перевода.
Для отправки текста из списка нажать на тот текст.{'''
 `-` Очень много символов за раз бот не может отправить, только около 220.
 `-` Возможные ошибки: недописывание символов.'''*is_full}

Ещё:
🔸 игра в слова (см. `/words help`);
🔸 значение слова: \
см. /meaning help.
{'''
`-` Полное сообщение — `/help full`.
'''*is_not_full}
{short_cright if is_not_full else full_cright}
"""
    h_text = "Руководство"
    h_url = HELP_URL
    help_message = Button.url(h_text, url=h_url)
    await event.respond(msg, parse_mode='md', buttons=help_message)
    raise events.StopPropagation

# v:undefined
# 1
async def words_skip_move(event):
    c = configparser.ConfigParser()
    chat_id = str(event.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Игра не найдена"
        await event.reply(msg)
        return
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    current += 1
    current %= len(order)
    section["current"] = str(current)

    if int(order[current]) == BOT_ID:
        mentioned = eval(section["mentioned"])
        cur_letter = section["letter"]
        letter = cur_letter

        print("Bot's move")  # test

        # Here normally the answer exists, so make_move(...) is a pair
        # `(word: str, message: str)`
        answer, msg = await make_move(event, letter, mentioned)

        current = (current + 1) % len(order)

        section["current"] = str(current)
        next_let = answer.lower().rstrip('ьъ')[-1]
        mentioned.append(answer)
        if next_let == 'ё': next_let = 'е'
        section["letter"] = next_let
        section["mentioned"] = str(mentioned)

        await event.reply(msg)
    else:
        msg = "Ход пропущен."
        await event.reply(msg)
    with open(filename, 'w', encoding='utf-8') as f:
        c.write(f)

    print('Performed skip of move.')  # test

# v:undefined
# 3 | TODO
@bot.on(events.NewMessage(pattern=commands('meaning')))
async def send_meaning(event):
    """Send meaning of a word.  See help for syntax.

    Syntax: either `/meaning word`, or `/meaning` in reply to the message with
    the word the meaning searched for.  Priority to search at the reply.
    """
    # **Note**: Priority to search for a word:
    # dict. 1 -> dict. '3' -> in the exact place at the I-net.

    chat_id = event.chat.id
    bot.action(chat_id, 'typing')

    try:
        cmd_pattern = _cmd_pattern('meaning')
        text = event.text
        word = re.fullmatch(cmd_pattern + r'\s*([-а-яё]+)', text).group(1)
    except:
        try:
            text = get_reply_message(event).text
            word = re.fullmatch(WORDS_GAME_PATTERN, text).group(1)
        except:
            msg = "Не распознано слово. Напиши либо в ответ на сообщение, \
где искомое слово, либо `/meaning слово`."
            await event.reply(msg, parse_mode='markdown')
            return
    from functions import d as d0
    order = [1, '3']
    async def by_rule(kid):
        if kid == 1:
            for a, q in d.items():
                a = a.replace(')', '')
                a = a.replace('(', ',')
                a = a.lower().split(',')
                a = map(lambda ph: ph.strip(), a)

                if word.lower() in a:
                    await event.reply(q)
                    return 0
        elif kid == '3':
            for k in d:
                if k.lower() == word.lower():
                    meaning = d[k]
                    await event.reply(meaning)
                    return 0
    for k in order:
        try:
            d = d0[k]
            if await by_rule(k) != 0:
                continue
            return
        except:
            continue
        del d
    del d0, order, by_rule

    url = f'https://loopy.ru/?word={word}&def='

    if (sc := (r := requests.get(url)).status_code) == 404:
        msg = f"Слово {word!r} не найдено в словаре."
        await event.respond(msg)
    elif sc != 200:
        msg = f"Непонятная ошибка. Код ошибки: {sc}."
        await event.respond(msg)
    else:
        rtext = r.text
        _rtext_part = rtext[rtext.find('Значения'):]
        try:  # great?
            rtext_part = _rtext_part
            rtext_part = rtext_part[:rtext_part.index('</div>')]
            finds = re.findall(r'<p>(.*?)</p>', rtext_part)[1:]
            # ^ 1-st item here — a header?
            assert finds
        except AssertionError:
            rtext_part = _rtext_part
            rtext_part = rtext_part[:rtext_part.index('</ul>')]
            finds = re.findall(r'<li>(.*?)</li>', rtext_part)
            if not finds:
                text = \
                f"A <b>great</b> error occured: haven't found a meaning"
                " for {word!r}."
                await bot_inform(text, parse_mode='html')
        res = random.choice(finds)

        await event.reply(res)

    raise events.StopPropagation

# v:undefined
# 5
async def _react_game_words(event):
    # Developer note:
    # Meta-syntax:
    # ------------
    # + `bot_username` -- username of a bot, i. e. BOT_USERNAME
    chat = event.chat
    text = event.text
    scid = str(chat.id)

    # Be careful: telethon does not recognize str object as a
    # chat id if passed as an entity,
    # e.g. while sending message via `send_message`.

    chat_id = scid

    # Processing further actions may take a significant amount of time.
    # Notify the user about it.
    bot.action(chat.id, 'typing')

    cmd_pattern = _cmd_pattern('words')
    help_pattern = cmd_pattern \
        + r'\s(?:[-—\s:]*)(?:правила|инструкция|команды|help)\s*\??'

    if re.fullmatch(cmd_pattern + r'.*?\s+[-!]?skip', text):
        await words_skip_move(event)
        return
    if re.fullmatch(cmd_pattern + r'\s+(?:приостановить|pause)', text):
        bot.action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
           msg = "Игра не найдена."
           await event.reply(msg)
           return
        c[chat_id]['status'] = 'paused'
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Игра приостановлена. Продолжение: /words continue{dot}"
        await event.reply(msg)

        return
    if re.fullmatch(cmd_pattern + r'\s+(?:хватит|удалить игру|stop)', text):
        bot.action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
           c.remove_section(chat_id)
        else:
            msg = "Игра не найдена."
            await event.reply(msg)
            return
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Текущая игра убрана{dot}"
        await event.reply(msg)
        return
    if re.fullmatch(cmd_pattern + r'\s+(?:очередь|порядок|order)', text):
        bot.action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            await event.respond("Игра в этом чате не найдена.")
            return
        section = c[chat_id]
        order = eval(section["order"])
        current = int(section["current"])
        uid = order[current]

        async def get_user(uid_: int):
            async for user in bot.iter_participants(chat.id):
                if user.id == uid_:
                    return user
            raise BotException('not found')
        u = await get_user(uid)
        order_ = ', '.join(map(
            full_name,
            [(await get_user(uid_)) for uid_ in order]
            ))
        text_mention = user_text_mention(u, fill=None)
        msg = f"""Последовательность: {order_}
Сейчас ходит: {text_mention}"""
        await event.respond(msg, parse_mode='html')
        return
    if re.fullmatch(help_pattern, text):
        bot.action(chat.id, 'typing')
        mark_item_point = ' `-` '  # '◽️'
        msg = f"""\
Начало игры
`-----------`
В личной переписке: /words `[начать|start]` `[single]` (`single` — игра самому)
В группе: `/words пользователь\_1 ...`
{mark_item_point}Имена пользователей — упоминанием;
{mark_item_point}Если своё имя не указывать, оно первое в очереди

Хода
`----`
В личной переписке: `!слово` либо `слово`
В группе: либо `!слово`, либо `слово` в ответ на сообщение того, кто ходил прошлым.

Другие:
`-------`
`/words pause``|``приостановить` — остановка игры
`/words stop``|``хватит|удалить игру` — прекратить игру и удалить
`/words skip` — пропуск хода
`/words order``|``очередь|порядок` — порядок ходов, текущий игрок
`/words help``|``правила|инструкция|команды` — это сообщение
`/words continue``|``продолжить` — продолжение (после `pause`)
"""
        await event.respond(msg, parse_mode='markdown')
        return

    if re.fullmatch(cmd_pattern + r'\s+(?:продолжить|continue)', text):
        bot.action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if (c.has_option(chat_id, 'status') and
            c[chat_id]['status'] == 'paused'):
            c.set(chat_id, 'status', 'active')
            with open(filename, 'w', encoding='utf-8') as f:
                c.write(f)
            dot = '.' * (random.random() > 1/2)
            msg = f"Игра продолжена{dot}"
            await event.reply(msg)

            return

    if event.is_private:
        # 'Requeted' the start of game via `/words[...]` at private chat.
        # Case of just `/words` goes also here.
        if 'single' in text:
            order = [event.sender.id]
        else:
            order = [event.sender.id, BOT_ID]
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
            if not re.search('(?:начать|start)', text):
                # Prevent the case of just `/words[@bot_username]` of being
                # the game's registering applied.
                msg = "Игра уже есть. Новая игра: /words `начать`|`start`. " \
                      "Также см.: /words `help`."
                await event.reply(msg, parse_mode='markdown')
                return
        else:
            c.add_section(chat_id)

        section = c[chat_id]
        section["order"] = str(order)
        section["current"] = str(current)
        section["letter"] = ANY_LETTER
        section["mentioned"] = str(mentioned)
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

        print("Registered. chat_id: " + chat_id)  # test
        await event.respond("Done. Registered.")
    elif event.is_group:
        # Message `/words[@bot_username]` was sent via a group or megagroup.

        # group = chat.id
        # can be helpful here: `bot.get_participants(group)`

        async def user_id_(e: 'Entity') -> 'int or `None`':  # TODO: do it
            # Returns either an `user_id: int`, or `None` if not found.
            # `None` appears either when the entity's type is unexpectable,
            # then the message via bot is send, if enabled, or when entity
            # is surely not a mention of user.
            # Expectable entity types to receive:
            # - MessageEntityUnknown,  # what?
            # - MessageEntityMention,
            # - MessageEntityMentionName,
            # - InputMessageEntityMentionName
            # Other types surely can't be a mention of a user.

            other = (
                MessageEntityUnknown,
                InputMessageEntityMentionName
            )
            if isinstance(e, MessageEntityMention):
                index = e.offset  # Start index of an entity at
                # the entity's text (this text defines as follows).
                text = event.text
                # text[index:] should be smth. like `'@username[...]'`.
                # +1: Skips `@`
                uname = text[index + 1 : index + e.length]
                return (await bot.get_entity(uname)).id
            elif isinstance(e, MessageEntityMentionName):
                return e.user_id
            elif isinstance(e, other):
                text = f'Unexpected! Type of entity (reg. game):'
                bot_inform(text + ' ' + str(e))
                print(text, e)
            else:
                # If another entity appears, ignore it.
                pass

        order = []
        for e in event.entities[1:]:
            maybe_user_id = await user_id_(e)
            if maybe_user_id:
                order.append(maybe_user_id)
            else:
                # Some entity wasn't recognized.
                # Let the user put the entity at a text and
                # just ignore it here. E. g., the user can
                # put links to anything at that message. (*)
                pass
        if not order:
            # (*) Still, when no users were registered, this case happens.
            # If the user really wants to play the game at his own at a group
            # chat (and even without the bot's moves), he maybe can do it by
            # registering the game with his own mention.
            # "Maybe" means "if his client gives him an appropriate chance".

            # So, do not register the game if only command was passed.
            # It prevents the case of unwanted click to command of being the
            # game reset.
            return

        # Otherwise, the message `event` is considered to be a request to
        # register the game at that chat.

        if (n := event.sender.id) not in order:
            order = [n] + order

        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            c.add_section(chat_id)
        else:
            # If section exists, game is considired to be still started:
            # the user wrote an exact text
            # '/words[@bot_username](\s<user_mention>)+', so this message
            # is considered to be not odd, but intentional.
            pass
        section = c[chat_id]
        section["order"] = str(order)
        section["current"] = str(current)
        section["letter"] = ANY_LETTER
        section["mentioned"] = str(mentioned)
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

        print("Game registered. chat_id: " + chat_id)  # test
        await event.respond("Done. Game registered.")


# v1.0.6rc1
# checked
# 4
@bot.on(events.NewMessage(pattern=commands('words')))
async def react_game_words(event):
    """React commands and triggers at game 'words'."""
    await _react_game_words(event)
    raise events.StopPropagation


# v1.0.6-to-check
# checked
# 2-(was set later).
# TODO:
# - [ ] test,
# - [ ] (ONLY AFTER TEST) Add hint at the bot, that this exists.
@bot.on(events.NewMessage(pattern=commands('greeting', 'new_greeting')))  # new
async def manage_greeting(event):
    """Set new greeting via bot/manage existed."""
    # Mind the Markdown/HTML escape or set.
    #
    # Possible: add Markdown/HTML. Also, doing a perfect function
    # of invite is a goal of not this bot.
    _pattern = event.pattern_match.re.pattern  # _pattern is a str object

    def pattern(command_part, cont=r'(?!\w).*'):
        part = r'\s*[-\s]?' + command_part + cont
        return _pattern + part

    help_pattern = pattern(r'help')
    del_pattern = pattern(r'(?:del(?:ete)?|remove)')
    show_pattern = pattern(r'show')

    def match(pattern_):
        text = event.text
        return re.fullmatch(pattern_, text)

    if match(help_pattern):
        sep = '🔸'
        dash = '-'
        reply_msg = r"""Добавить текст приветствия: /new_greeting текст.\
Доступная разметка: `...{user.method}...`, {mention(user)}, (1), всё в HTML.\
\
\n\nПример: <i>\"Привет, {mention(user)}! Твое имя: {user.first_name}.\"</i>.
""" + f"""
{sep}Это сообщение: /greeting help или /new_greeting help
{sep}Показать приветствие: /greeting show
{sep}Удалить приветствие: одно из /greeting del|delete|remove
Перед параметрами можно добавить тире, например, /greeting {dash}del.
(1): mentions: mentions — упоминания <i>добавленных пользователей</i> через \
запятую, bt_uname — @имя_бота, scright и fcright — длинный и короткий, \
соответственно, тексты копирайта.
"""
        await event.reply(reply_msg, parse_mode='html')
        return
    else:
        try:
            with open(FILE_GREETING, encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

    section = str(event.chat.id)
    is_new_greeting = bool(match(commands('new_greeting')))
    should_set_new = True

    if not is_new_greeting:
        if match(del_pattern):
            case = 'delete'
            del data[section]
            should_set_new = False
        elif match(show_pattern):
            case = 'show'
            msg = data[section]
            await event.reply(msg)
            should_set_new = False
            return
    elif should_set_new:
        case = 'add'
        msg = re.fullmatch(_pattern + r'\s*([.\n]+)').match(1)
        data[section] = msg

    with open(FILE_GREETING, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    if case == 'delete':
        await event.reply("Приветствие удалено.")
    elif case == 'add':
        await event.reply("Приветствие добавлено.") 

# v1.0.6-editing
# checked; to test
@bot.on(events.ChatAction(func=lambda event: \
                          event.user_joined or event.user_added))
async def greet_new_chat_members(event):
    """Welcome every new user.

    Strategy: if user joined a chat with chat_id==SPEAK_CHAT and is not a
    member of the head chat (with chat_id==HEAD_CHAT), ban him; otherwise he
    is considered to be a normal user to greet him at that chat. It is made in
    order to add some safety to the chat of speaking. If user/users joined an
    *another* chat, just greet him/them. If this chat is not with chat_id in
    [SPEAK_CHAT, HEAD_CHAT, TEST_CHAT], try to greet him using the greeting,
    set by using the command /add_greeting or similar to this text. If it
    doesn't goes still, try to greet with a default greeting. In this order,
    every new user (which is pointed as a user to greet; if not banned in case
    of upper-mentioned coinsedences) is welcomed with exactly one greeting.
    """
    # print(event)  # test
    should_greet_all = False
    # ^ Only for chat with `chat_id == SPEAK_CHAT`

    if event.user_joined:
        user_id = event.action_message.from_id  # peer
        user = await bot.get_entity(user_id)
        users = [user]
    elif event.user_added:
        user = event.action_message.from_id
        permissions = await bot.get_permissions(event.chat, user)
        if permissions.is_admin:
            should_greet_all = True
        uids = event.action_message.action.users
        users = [await bot.get_entity(uid) for uid in uids]
    else:
        # Event is not "user joined/added". Actually, is not required if an
        # appropriate `func=...` is set at the trigger's settings.
        return

    chat_id = event.chat.id

    uids = [u.id for u in users]
    for uid in uids:
        await _add_user(uid)

    def _mentions(_users, *, escape=True, escape_with='html'):
        # Return mentions of _users, separated by ', '.
        # HTML symbols are escaped (or not) in order to make an appropriate
        # message to send it then.  TODO: Test such mentions + unescape.
        # e. g. this as a name: `<a href="google.com">Hello</a>`.
        # Some link(s) about es-pes at Telegram bots/(?)operations:
        # - https://core.telegram.org/bots/api#formatting-options
        # 
        # This action appears to be so common here, that this is a great to
        # make at as a call of a separate function. I. e., this function.

        escape = escape_with if escape else None
        def _escape(s, style=None):
            # Escape the string s symbols with an appropriate symbols seq-s.
            # When style is None -- do not escape.
            # 
            # This function states more as a template, then a complete escape.
            # For supported styles see `supported_styles` at following.

            style = style.lower()
            supported_styles = {
                None,
                'html', 'markdown', 'markdownv2'
            }
            assert style in supported_styles
            if style is None:
                return s
            elif style == 'html':
                # See https://core.telegram.org/bots/api#markdown-style.
                return html_escape(s, quote=False)
            else:
                msg = "At this case using markdown(v2) can be bad."
                warnings.warn(msg)

                from escape_markdown import escape as __escape
                return __escape(s, version=style.lstrip('markdown'))
        
        _answer = [
            _escape(
                user_text_mention(user), style=escape
            )
            for user in _users
        ]
        answer = ", ".join(_answer)
        return answer
    if chat_id == SPEAK_CHAT:
        if TOKEN != TOKEN_INIT:
            # Prevent the case two bots were put at that chat together.
            # More precisely, greet than only if the working bot is a bot
            # with TOKEN==TOKEN_INIT.
            return
        should_ban = []
        if not should_greet_all:
            for user in users:
                if not await is_participant(user.id):
                    should_ban.append(user)

        if should_ban:
            await event.reply("Сюда можно онли участникам чата курса. Сóри.")
            for u in should_ban:
                await bot.edit_permissions(chat_id, u.id,
                    view_messages=False  # i. e. banning
                )
                # reference: (1) *QUESTION*: where? what?

        should_greet = [user for user in users if user not in should_ban]
        if not should_greet:
            # No one found to greet him.
            return

        is_test_msg = False

        mentions = _mentions(should_greet)
        msg = f"""{"[Это тест.]"*is_test_msg}
Привет, {mentions}!
Этот чат — флудилка. Ссылка на основной чат находится в \
закрепе. Бот может быть полезен аля-переводом текста на старославянский \
язык. Инструкция: см. /help@{BOT_USERNAME}.

{short_cright}
"""
        await event.respond(msg, parse_mode='html')
    elif chat_id == HEAD_CHAT:
        word = "Здравствуй" if len(users) == 1 else "Здравствуйте"
        
        mentions = _mentions(users)
        msg = f"""\
{word}, {mentions}!
Это основной чат курса, ссылка на флудилку есть в закрепе.
Бот может быть полезен аля-переводом текста на старославянский \
язык, транслитерацией в старославянские алфавиты. Инструкция: \
см. /help@{BOT_USERNAME}.
"""
        await event.respond(msg, parse_mode='html')
    elif chat_id == TEST_CHAT:
        msg = f"""\
{user_text_mention(user)}
Этот чат — тестовый чат. 
/start
/help@{BOT_USERNAME}.
"""
        await event.respond(msg, parse_mode='html')
    else:
        mentions = _mentions(users)
        with open(FILE_GREETING, 'w', encoding='utf-8') as f:
            data = json.load(f)

        if (k := str(chat_id)) in data:
            # *question*: best?
            for user in users:
                source = eval(DEFAULT_GREETING_EVAL_SOURCE)
                # Replace `"` with `\"`.
                _msg = data[k].replace('"', r'\"')
                msg = eval('f"' + _msg + '"', source)
                await event.respond(msg)

        else:
            bot_uname = BOT_USERNAME  # shorthand
            default_greeting = f"""Hello, {mentions}!

🔸Set the greeting via /add_greeting, see /add_greeting@{bot_uname} \
<pre>help</pre>.
🔸Bot is usible for like-a-translation to Old Slavonic, see \
/help@{bot_uname}.
"""
            await event.respond(msg, parse_mode='html')


# v:undefined
# TODO Check, test
@bot.on(InlineQuery(func=lambda event: 0 < len(event.text) <= 255))
async def answer_query(event):
    """Answer a non-empty inline query, but not big.
    
    See https://core.telegram.org/bots/api#inlinequery.
    See also: https://core.telegram.org/bots/#inline-mode.
    """
    try:
        answers = []  # Storage for the results of inline query.
        text = event.text
        print('query:', text)  # test

        builder = event.builder

        if any(text.startswith(k) for k in NAMES_REPLACE):
            show_text = text
            # ... Or do the further with `html.escape(text, quote=False)`,
            # html is a module of Python stdlib.
            pairs = {
                '<': "&lt;",
                '>': "&gt;",
                '&': "&amp;"
            }
            def _repl(s_part):
                return pairs[s_part]
            pattern = '|'.join(pairs.keys())
            repl = lambda match: _repl(match.group())
            def html_readable(s):
                return re.sub(pattern, repl, s)
            text = html_readable(text)

            for k in NAMES_REPLACE:
                i1, i2 = NAMES_REPLACE[k]
                show_text = show_text.replace(k, i1)
                i1 = html_readable(i1)
                text = text.replace(k,
                    '<a href="tg://user?id={1}">{0}</a>'.format(i1, i2))

            zero_title = bytes("Смена слов", encoding='utf-8')
            zero_description = show_text
            zero_text = text
            parse_mode = 'html'  #?

            r_1 = builder.article(zero_title, zero_description,
                text=zero_text, parse_mode=parse_mode)
            answers.append(r_1)

        text = event.text

        # parse_mode *question*  # TODO Solve this question.
        # Parse mode here — ?
        # And sending the text in HTML/Markdown.

        thumb_config = COMMON_THUMB_CONFIG
        size = thumb_config['size']
        mime_type = thumb_config['mime_type']
        attributes = [thumb_config['attributes']]

        # thumb configs:
        c_url = A_CYRYLLIC
        g_url = A_GLAGOLIC
        trg_url = A_LATER_GLAGOLIC
        c_thumb = InputWebDocument(c_url, size, mime_type, attributes)
        g_thumb = InputWebDocument(g_url, size, mime_type, attributes)
        trg_thumb = InputWebDocument(trg_url, size, mime_type, attributes)
        # *note*: Shortages for `^` (upper):
        #  - c, g -- cyryllic, glagolic
        #  - trg -- transliterated (to) glagolic
        # Same may be stated for other notations at nearly this code
        # (at exactly this part of it).

        # input messages:
        c_text = translation(text, dest="cyryllic")
        g_text = translation(text, dest="glagolic")
        trg_text = glagolic_transliterate(text)

        # title, description, text:
        c_title = bytes("Перевод на кириллицу", encoding='utf-8')
        c_description = c_text
        # c_text = c_text
        # ^ cyryllic
        g_title = bytes("Перевод на глаголицу", encoding='utf-8')
        g_description = g_text
        # g_text = g_text
        # ^ glagolic
        trg_title = bytes("Транслитерация на глаголицу", encoding='utf-8')
        trg_description = trg_text
        # trg_text = trg_text
        # ^ transliterated to glagolic

        # results:
        r_c = builder.article(c_title, c_description,
            text=c_text, thumb=c_thumb)
        r_g = builder.article(g_title, g_description,
            text=g_text, thumb=g_thumb)
        r_trg = builder.article(trg_title, trg_description,
            text=trg_text, thumb=trg_thumb)

        answers = [r_c, r_g, r_trg] + answers

        await event.answer(answers, cache_time=CACHE_TIME)
    except Exception as e:
        print(type(e), ': ', e, sep='')


# v:undefined
# TODO Check | Requires test
@bot.on(InlineQuery(func=lambda event: not event.text))
async def answer_empty_query(event):
    await _add_user(event.sender.id)

    try:
        title = bytes("Перевод на славянские языки: кириллица, глаголица.",
            encoding='utf8')
        description = "Введи текст для перевода, жми на нужный для отправки"
        # thumb data:
        thumb_config = COMMON_THUMB_CONFIG

        url = A_LATER_GLAGOLIC
        size = thumb_config['size']
        mime_type = thumb_config['mime_type']
        attributes = [thumb_config['attributes']]
        thumb = InputWebDocument(url, size, mime_type, attributes)

        builder = event.builder
        r = builder.article(title, description, text='no text', thumb=thumb)

        answer = await event.answer([r], cache_time=CACHE_TIME)
    except Exception as e:
        print(e)


# v:undefined
# TODO Check, do tests
@bot.on(events.NewMessage)
async def answer_message(event):
    """Answer the text message.

    Actually, realises a move at game words.
    """
    c = configparser.ConfigParser()
    chat_id = str(event.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        # Аnswer can be performed only if section exists.
        return
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    if (c.has_option(chat_id, 'status') and
        c.get(chat_id, 'status') == 'paused'):
        return

    if event.is_private:
        pattern = r'(?i)\!?[-а-яё]+'
        if (s := re.fullmatch(pattern, event.text)):
            await play_words(event)
    else:
        pattern = WORDS_GAME_PATTERN
        if re.fullmatch(pattern, event.text):
            await play_words(event)


def main():
    """Run the bot."""
    asyncio.run(bot.run_until_disconnected())


if __name__ == '__main__':
    with bot:
        print("Running main... (the bot)")
        main()
