# -*- coding: utf-8 -*-
# version: telebot:1.0.9

# THIS CODE AND APP ARE FREE FOR USAGE AND MAINTAINED & DISTRIBUTED UNDER THE
# TERMS OF *MIT License*. See LICENSE for more info.
# 
# The code is FREE FOR COPY, CHANGE, AND THE CODE's SHARING.  (?) **QUESTION**
#
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
# - README for some info.
# - "metalog.txt"|TODO for some instant/following/current changes.
# - File config.py to view or change the configurations
# - File .env or its analogues.
# - Launcher and similar to have a possible help with launching the bot app
# - File "meta/All TODO/TODO.md" to view some TODO and notes on the code or
#   other objects, somehow connected with this code and the bot.
# Requires Python >=3.8 to allow the use of `:=`
# set the required version at runtime.txt (see also: runtime info at [1])
# 
# [1]: https://devcenter.heroku.com/articles/python-runtimes#supported-runtime-versions
#
# -----------------------------------------------------------------------------
# 
# Development notes
# -----------------
# 
# - possible meta-notes at this file:
#   note, question/questions (different), mark,
#   checked, to test/to check, test, TODO, meta, OR, task
#    + these are sometimes not case-sensitive
# - [telethon] this can help to ignore further triggers for an exact update:
#   `raise events.StopPropagation`
# - may use "case 1"/another (use quote symbol) to mark, which words are
#   included.
# - noting versions at some places (e.g. functions/classes) to show, which of
#   version they are ("at which version"/when they were written/added)
#   + marking versions: either "version-name", or "v:<comment>", e.g. when
#     comment is "undefined"
#     * "to-check" means "nearly final version, to check still, and merge"
# - `configparser.ConfigParser()` is sometimes created exactly at the
#   function's call, which is to work correctly, if several users use a
#   bot simultaneously (TODO: What? Solve.)
# 
# TODO
# ----
# 
# - Marked with TODO, question[s].
# - Merge TODO, questions etc. from everywhere.
# - Test: triggers to start, words, BotException (see comments)
# - TODO from "../TODO".
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
# Notes & comments syntax
# -----------------------
# 
# - Mixed Markdown and Sphinx, also using some Sphinx-styled maybe-not-existed
#   commands. Markdown is either plain or a GFM. Example of a pseudo-Sphinx
#   syntax:
#   .. edit-date::
#   
#       2021-06-01T12:00:00Z
# - `re` expressions
# - Such as:
#   + [...] -- optional part
#   + <var>, meaning an exact variable, inserted at a place of the "<var>".
#   + Several Markdown-styled, but not really existed, e.g. `word_or_text'
# - Can be related somehow to pyTorch.


# === Imports =================================================================


import random
import re
import typing
from collections.abc import Iterable
from typing import Optional, Union, Any
import json
from html import escape as _html_escape
from urllib.parse import urlsplit
import warnings
from textwrap import dedent  # Readability.

import requests
import telebot
from telebot import types
from telebot.types import ChosenInlineResult

from config import (
    # Pictures/media:
    A_CYRYLLIC, A_GLAGOLITIC, A_LATER_GLAGOLITIC,
    # configparser:
    configparser, NoSectionError,
    # Chats & channels:
    CHANNEL, TEST_CHAT, SPEAK_CHAT, HEAD_CHAT,
    # Connected with bot:
    # * Version-specific:
    bot,
    # * Other:
    TOKEN, BOT_ID, BOT_USERNAME, TOKEN_INIT,
    # Game words:
    WORDS_GAME_PATTERNS, GAME_WORDS_DATA, ANY_LETTER,
    # Inline:
    INLINE_EXAMPLES, NAMES_REPLACE, CACHE_TIME, COMMON_THUMB_CONFIG,
    # Greeting:
    FILE_GREETING, DEFAULT_GREETING_EVAL_SOURCE, DEFAULT_GREETING,
    # Logging at chats:
    LOGGING_CHAT, LOGGING_CHAT_INLINE_FEEDBACK, CHAT_LOGS_MODE_ALL,
    # Other:
    ADMINS, HELP_URL, UIDS_BASE, PROD, PASSWORD_ENABLED,
    ON_HEROKU, LOCAL_LOGS, FEATURES_EXIST
)
from functions import (
    translation, glagolitic_transliterate,
    d as _d
)
from meta.edit_date import short_cright, full_cright


# === Some config =============================================================


WORDS_GAME_PRIVATE_PATTERN = WORDS_GAME_PATTERNS["private"]
WORDS_GAME_PATTERN = WORDS_GAME_PATTERNS["general"]

HTML = 'html'
MARKDOWN_V2 = 'MarkdownV2'


edit_note = "telebot:1.0.9"
# ^ Dummy, to check for updates while running.


# Since v1.0.9.
def bot_send_message(text, chat_id=LOGGING_CHAT, type_=None, **kwargs):
    """Send a text message via bot to chat with chat_id, if it is required."""
    if type_ is not None and type_ not in CHAT_LOGS_MODE_ALL:
        return
    bot.send_message(chat_id, text, **kwargs)


# Since v1.0.9.
# TODO Do this great, applications.
class BotException(Exception):
    """Class to handle bot exceptions."""
    # Appears to be more a template then a complete object.
    def __init__(self, *args, extra={}, kwargs={}):
        super(BotException, self).__init__(*args, **kwargs)
        self.extra = extra
        chat_id = extra.get('chat_id')
        from_user = extra.get('from_user')
        if args:
            exception = self.args[0]
        else:
            exception = "no info given"

        text = f"""\
**An exception occured**
 - `chat_id`: __{chat_id}__
 - `from_user.id`: __{from_user.id}__
 - `exception`: __{exception}__
"""

        bot_send_message(text, type_='bot-exception',
            parse_mode=MARKDOWN_V2)

# d = dict(chat_id='chat_id', user_id=0)
# raise BotException('test', extra=d)  # test


prod_word = "" if PROD else 'not '
on_heroku = 'yes' if ON_HEROKU else 'no'
text = f"""\
Launched the bot.
Is <u>{prod_word}the production</u> version.
Is whether on Heroku: <u>{on_heroku}</u>.
"""
bot_send_message(text, type_="launch", parse_mode='html')

# Clear space:
del text, ON_HEROKU, on_heroku


# === Several internal functions ==============================================

# --- Section: str utils ------------------------------------------------------


# Since v1.0.9.
def html_escape(text: str, quote=False) -> str:
    return _html_escape(text, quote=quote)


# Since v1.0.9.
def capitalized(s: str) -> str:
    """Returned the string, where first letter is capitalized.

    Id est:
    >>> capitalized("Two Words") -> "Two Words"

    >>> capitalized("another examplE") -> "Another examplE"

    And so on. Str is empty => return it.
    """
    if not s:
        return s
    c, *s_ = s
    return c.capitalize() + ''.join(s_)


# Since v1.0.9.
def casefold(s: str) -> str:
    return s.casefold()


# --- Section: triggers helpers -----------------------------------------------
# Here some functions, useful for setting triggers, are defined.


# Since v1.0.9.
def _cmd_pattern(cmd: str, *, flags: Optional[str] = 'i') -> str:
    # Internal function.
    # Strategy: `'cmd'` -> pattern for either '/cmd' or '/cmd@bot_username'.
    if flags:
        _flags_add = r'(?' + flags + r')'
    else:
        _flags_add = ""
    cmd_pattern = _flags_add + r'/' + cmd + r'(?:@' + BOT_USERNAME + r')?'
    return cmd_pattern


# Since v1.0.9.
def commands(*cmds: str, flags: Optional[str] = None) -> str:
    # Internal function.
    #
    # Goal: create a pattern for '/cmd' or '/cmd@bot_username', where
    #       cmd is one of items at `cmds`.
    # Strategy:
    # * cmds = [cmd] => return pattern for "/cmd[@bot_username]"
    # * cmds = [cmd_1, cmd_2, ...] => return
    #   "/(?:cmd_1|cmd_2|...)[@bot_username]" with flags
    # * flags are omited => flags are as default at `_cmd_pattern`
    if flags is not None:
        kwargs = {'flags': flags}
    else:
        kwargs = {}

    cmd_styled = '|'.join(cmds)
    if len(cmds) > 1:
        cmd_styled = r'(?:' + cmd_styled + r')'
    
    return _cmd_pattern(cmd_styled, **kwargs)


# Since v1.0.9.
# Tested for 2**2 different cases of (case, is_coro), when they are
# of type `bool`.
def enabled(case=True, *, is_coro=False):
    """Help-function to enable/disable the required trigger.

    Internal function. See code. Works both with functions and coroutines.
    Pass is_coro=True to work with coroutines. Defaults to False.

    ---------------------------------------------------------------------------

    Usage
    =====

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
    # arguments/kw, and for functions names; at this code there is no sense
    # in those.
    
    if type(case) is not bool:
        warnings.warn(
            "Using case of type different from bool may cause errors."
            )
    
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
                        # `dummy()` -> `None`
                        """Dymmy function. dummy() is a coroutine object."""
                    return dummy()
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator


# --- Section: other utils ----------------------------------------------------


# Since v1.0.9.
def feature_exists(fid: typing.Hashable) -> bool:
    # Whether feature exists.
    # Internal function.
    # To manage these features' activation, change `FEATURES_EXIST` at config.
    d = FEATURES_EXIST
    if fid in d:
        return d[fid]
    return False


# Since v1.0.9.
def load_json(fname: "None or File Object" = None, encoding='utf-8',
              do_warn_on_fail=True):
    """Load the json from file. Return {} on fail."""
    if fname is None:
        fname = FILE_GREETING
    data = {}  # Store for case of unsuccessful load of data.
    try:
        with open(fname, encoding=encoding) as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        if do_warn_on_fail:
            msg = "Exception occured on load json. "\
            "Treating content as empty dict."
            warnings.warn(msg)
    except OSError:
        pass

    return data


# Since v1.0.9.
def is_participant(user_id: int, chat_id=HEAD_CHAT) -> bool:
    """User is participant of chat with id `chat_id`, return bool."""
    # See: https://core.telegram.org/bots/api#chatmember.
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
    except:
        return False
    # Otherwise chat_member is a ChatMember object.
    participant_statuses = [
        "creator",  # Creator
        "administrator",  # Administrator
        "member"  # Member
    ]
    if chat_member.status == "restricted":
        return chat_member.is_member
    return chat_member.status in participant_statuses


# Since v1.0.9.
def _add_user(user_id: Union[int, str]) -> typing.NoReturn:
    """Add ID to the base. Comments are allowed."""
    filename = UIDS_BASE
    with open(filename, 'a') as f:
        # Ensure file exists.
        pass

    with open(filename, encoding='utf-8') as f:
        data = f.read()  # Only to read.
    data_ = ""  # To write.
    if data and data[-1] != '\n':
        data_ += '\n'  # Add newline if absent.
    if (suid := str(user_id)) not in data:
        text = 'New user: \
<a href="tg://user?id={0}">{1}</a>\nuser_id: {0}'.format(
            user_id, "User"
            )
        bot_send_message(text, type_='new user', parse_mode='html')
        data_ += suid + '\n'

    with open(filename, 'a', encoding='utf-8') as f:
        f.write(data_)


# Since v1.0.9.
def full_name(user) -> str:
    """Full name of a user."""
    return f'{user.first_name}{" " + u if (u := user.last_name) else ""}'


# Since v1.0.9.
def user_text_mention(user: 'User', fill: Any = None) -> str:
    """Text mention of a user."""
    # :param fill: Text to insert at mention.
    # Link: https://core.telegram.org/bots/api#formatting-options.
    if fill is None:
        filling = full_name(user)
    else:
        filling = fill
    return f'<a href="tg://user?id={user.id}">{filling}</a>'


# Since v1.0.9.
def is_private(message) -> bool:
    """Whether message is private."""
    # See "type" at https://core.telegram.org/bots/api#chat.
    return message.chat.type == 'private'


# Since v1.0.9.
def is_group(message) -> bool:
    """Whether message was sent at a group."""
    # See "type" at https://core.telegram.org/bots/api#chat.
    return 'group' in message.chat.type


# Since v1.0.9.
def get_reply_message(message):
    """Message the `message` is replying to, or `None`."""
    # This function is made for better compatibility
    # with other versions.
    return message.reply_to_message


# Since v1.0.9.
def load_users() -> map:
    """Return a `map` object, containing users' IDs."""
    with open(UIDS_BASE, encoding='utf-8') as f:
        users = map(eval, f.read().strip().split('\n'))
    return users


# Since v1.0.9.
def get_info_by_rule(pattern: str, kid: Any,
                     mentioned: Iterable = [],
                     add_d=None) -> Optional[tuple[str, str]]:
    """Get word and meaning from the given dictionary.

    :return: A tuple ``(word, meaning)'' if found; ``None'' when not found.
    :rtype: typing.Optional[tuple[str, str]]

    when `d` (see code) is not given, pass::

        add_d=:obj: of type `dict`
    type(d) is ``dict''.
    """
    if add_d:
        d = add_d

    def is_mentioned(word: str, src_dict=mentioned):
        return word.casefold() in map(casefold, src_dict)

    if kid == 1:
        # Meta: `*a*nswer`,  # *d*efinition  #
        #        `*q*uestion`

        possible = []
        for a, q in d.items():
            a = a.replace(')', '')
            a = a.replace('(', ',')
            a = a.lower().split(',')
            a = map(lambda ph: ph.strip(), a)
            filter_ = lambda k: not is_mentioned(k) and \
                    re.fullmatch(r'[-\w]+', k)
            a = list(filter(
                filter_,
                a
            ))

            if any(re.fullmatch(pattern.lower(), a_part) for a_part in a):
                # `a` is not empty
                # `a` -- list of str (each is word)
                # `q` -- str (definition)
                possible.append((a, q))

        _word, q = random.choice(possible)
        word = random.choice(_word)

        return word, q
    elif kid == '3':
        searched = []
        for k in d:
            if is_mentioned(k):
                continue
            if re.fullmatch(pattern.casefold(), k.casefold()):
                meaning = d[k]
                searched.append((k, meaning))
        
        k, meaning = random.choice(searched)
        return k, meaning


# Since v1.0.9.
def get_word_and_meaning(pattern: Union[str, dict],
                               message: types.Message,
                               mentioned: Iterable = ()) \
    -> Optional[tuple[str, str]]:
    r"""Get a word, which matches pattern, and meaning of a word.

    :param pattern: A pattern. Is prefered to be :obj:`dict`.
        * Either str, which matches ``"(?i)[-а-яё\*\?]+"'',
        * or a dictionary, where each key's value matches such a pattern.
    :param message: Message, with a help of which the information is
                    send to the user or written somewhere else, if
                    required (is better, if only in development state),
                    when it is required immediately. Example: when
                    something unexpected occured or a search failed.
    :param mentioned: Iterable, containing all mentioned words.
                      Is used to search words from the complement of
                      that iterable. Defaults to an empty tuple.
    :return: A tuple ``(word, meaning)'' if found, ``None'' otherwise.
    :rtype: typing.Optional[tuple[str, str]].

    :pattern's keys:
    * Is either "normal" (="dictionary"), or "site";
    * key 'normal' is changed to 'dictionary'. For user it is not essential.
    
    Development notes
    -----------------
    
    * This code may be partially strange, see version 1.0.4
      (maybe 1.0.5) or earlier to view the previous state.
    * This code may be strange at least because of it's aim only for
      satisfying 2 cases: (letter)**..* and `whole_word` (i.e.
      search by patterns :re_pattern:`f"{letter}.*"` and exact word
      pattern). However, writing a complete is not a goal of this work.
    * See also: something like "<root>/meta/utils/../form_word.*".

    See also
    --------

    * Something like "<root>/meta/utils/../form_word.*".
    * "<root>/meta/most-recent.txt".
    """
    _pattern = pattern  # Register word/name/"place to work at".

    if type(_pattern) is dict and 'normal' in _pattern:
        _pattern['dictionary'] = _pattern['normal']
        del _pattern['normal']
    
    if type(_pattern) is str:
        if '?' in _pattern:
            raise NotImplementedError
        if _pattern == ANY_LETTER:
            _pattern = ""
        else:
            assert re.fullmatch(r'(?i)[-\w\*\?]+', _pattern)
        ## _pattern = re.sub(r'[^\w?]', '*', _pattern)
        ## case of `{letter}**.*`, just named `_pattern=letter`
        func = lambda n: _pattern + '*'*(n - max(0,
                                                 len(_pattern)))
        word_pattern = {
            'dictionary': _pattern + r'.*',
            'site': func
        }
    else:
        assert type(_pattern) is dict
        supported_search_types = {'dictionary', 'site'}
        keys = set(_pattern.keys())
        if not keys.issubset(supported_search_types):
            warnings.warn("Unsupported search type(s) passed: "
                ', '.join(keys - supported_search_types)
                )
        word_pattern = _pattern

    order = [
        ('dictionary', (None, 1,)),
        ('dictionary', (None, '3',)),
        ('site', ("https://loopy.ru/?word={0}&def=",
                  {
                      "word": 'word_pattern["site"]',
                      "def": None
                   },
                   {
                       'word_pattern': word_pattern
                    })
        )
    ]

    def _allowed(s='-а-яё', *, add_s=''):
        return eval(f"r'(?i)[{s + add_s}]'")

    allowed = _allowed()  # Here are all symbols at word, not more or less.
    if type(word_pattern["site"]) is str:
        assert re.fullmatch(_allowed(add_s='*?') + r'+', word_pattern["site"])
    else:
        # If a callable, it should be like lambda n: <string>.
        pass
        # raise NotImplementedError("Word's search error: "
        #     "Should use pattern of type `str`.")
    del _allowed
    
    def search_at_dictionary(k, *, _d=None) -> Optional[tuple[str, str]]:
        """Search at dictionary dict[k].

        Dictionary ``dict'' is considired to be ``_d'' if it is provided,
        and ``d'' from ``globals()'' otherwise.

        :return: A tuple ``(word, meaning)'' if found, ``None'' otherwise.
        :rtype: typing.Optional[tuple[str, str]].
        """
        if _d is None:
            _d = globals()['_d']
        pattern = word_pattern['dictionary']
        d = _d[k]
        result = get_info_by_rule(pattern, k, mentioned, add_d=d)
        # Result is either ``None'', or a tuple ``(word, meaning)''.
        return result

    def search_on_loopy(_url, args: dict = {}, provide_space={}) -> tuple[int, ...]:
        """Search on site loopy.ru.

        :return: A tuple `(exit_code, *result)`.
                 It is either a (0, word, meaning), or (2, dict_).
        """
        if 'word' not in args:
            # No word is being searched for. Nothing should be done.
            raise Exception("No word searched")
        try:
            pattern = eval(args['word'], provide_space)
        except (NameError, Exception) as e:
            print(e)
        def_ = args['def']
        if def_ is not None:
            def_ = eval(def_)

        def _is_strict_word(word):
            if type(word) is callable:
                return False
            return re.fullmatch(f'{allowed}+', word)

        is_strict_word = bool(_is_strict_word(pattern))
        
        increase_allowed = not is_strict_word
        if increase_allowed:
            maxn = 4
            # Developer can set another, if "it is required"/"he wants".

            possible = list(range(1, maxn))
        else:
            maxn = len(pattern)
            possible = [maxn - 1]
        searched = None

        def one_iteration(url):
            """One iteration of a search.

            :return: A tuple ``(exit_code, result)''.

            .. exit_code-info::
                
                * 0 means success,
                * 1 means ``not found'',
                * 2 means ``a message/exc'' is returned.
            
            .. result-info::
            
                * code == 1 (not found) --> ``None''
                * code == 2 --> a dict, is data of 'a message'/exc
                * code == 0 (success) --> a tuple ``(word, meaning)'',
            where code is ``exit_code''.
            """
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
                    item: str = base.pop(i).group()
                    word_ = word(item)
                    if word_ not in mentioned:
                        searched = word_  # String.
                        meanings_: list[str] = meanings(item)
                        if not meanings_:
                            # Can this actually happen?
                            pass
                        meaning = random.choice(meanings_)
                        # Dev note: Mind adding `searched` to the mentioned.
                        return 0, (searched, meaning)
                return 1, None

            else:  # I. e. `is_strict_word == True`
                word = pattern

                sc = r.status_code
                # External link:
                # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes.
                if sc == 404:
                    # Not found.
                    msg = f"Слово {word!r} не найдено в словаре."
                    return 2, {"msg": msg}
                elif sc != 200:
                    # Status code 200 means that response status is OK.
                    msg = f"Непонятная ошибка. Код ошибки: {sc}."
                    return 2, {"msg": msg}
                rtext = r.text
                _rtext_part = rtext[rtext.find('Значения'):]

                try:
                    # Result getter: version 1.
                    rtext_part = _rtext_part
                    rtext_part = rtext_part[:rtext_part.index('</div>')]
                    finds = re.findall(r'<p>(.*?)</p>', rtext_part)[1:]
                    # Request question: Is 1-st item here: ^ — a header?

                    assert finds
                except AssertionError:
                    # Result getter: version 2.
                    rtext_part = _rtext_part
                    rtext_part = rtext_part[:rtext_part.index('</ul>')]
                    finds = re.findall(r'<li>(.*?)</li>', rtext_part)
                    if not finds:  # Can it actually be?
                        return 2, {"msg": 'Unexpected error'}
                meanings: str = random.choice(finds)
                return 0, (word, meanings)

        # Search for word and meaning.
        iterations_made = 0  # Iterations counter. It is optional.
        max_allowed_iterations = 100
        if not is_strict_word:
            while maxn <= 20 and iterations_made < max_allowed_iterations:
                # While not too much iterations had been made, continue making
                # the search, increasing the number of iterations.
                possible.append(maxn)
                n = possible.pop(random.choice(range(len(possible))))
                format_ = pattern(n)  # Can be done, actually, for any pattern.
                # But it's not a goal of this work.
                # See form_word for some help to doing search for any pattern.
                # That obj. maybe can be found somewhere at <root>/meta/utils.

                url = _url.format(format_)
                code, result = one_iteration(url)
                iterations_made += 1
                maxn += 1

                if code == 1:
                    # Not found.
                    continue
                else:
                    # Either found, or an exception occured.
                    break
        else:
            # At this case the word pattern is strict.
            word = pattern
            url = _url.format(word)
            code, result = one_iteration(url)
        
        # Get results, if they hadn't been received earlier. Still,
        # if they had, do the required stuff with them now.
        if code == 0:
            word, meaning = result
        elif code == 1:  # Shouldn't come here, unless `searched is None`
                         # occures when `not is_strict_word` is true.
            # Result wasn't received.
            pass
        elif code == 2:
            # Word/meaning not found. Message or an exception data is returned
            # at the `result`.
            return 2, result
        else:  # Not implemented; is a sample.
            pass

        if searched is None and not is_strict_word:
            if iterations_made >= max_allowed_iterations - 1:
                return 2, {"msg": "Unexpected error"}
            # Commented:
            """'''
            msg = (
            "Wow!😮 How can it happen? I had found no words for this pattern."
            "❌Game is stopped. Realise move's skip to continue"  #!
            )  # Question: continuing game -- ?
            '''"""
            # Or simply return the number of iterations_made.
            # return 2, {"iterations_made": iterations_made}

        return 0, (word, meaning)

    def search_at(source_type: str = 'dictionary',
                  parameters=None,
                  *,
                  return_on_fail: 'callable or object to return' = 1):
        """Search at a given source.

        :return: A tuple ``(exit_code, result)''.
        """
        # .. exit_code-info::
        # 
        #     0 means found, 1 means fail.
        #     exit_code == 0 --> result is ``(word, meaning)''.
        try:
            if source_type == 'dictionary':
                dict_, *params = parameters
                return 0, search_at_dictionary(*params, _d=dict_)
            elif source_type == 'site':
                _url, *other_args = parameters
                netloc = urlsplit(_url).netloc
                if netloc == "loopy.ru":
                    # Search on "loopy.ru".
                    # Unpack args.
                    args, provide_space = other_args
                    # Perform the search.
                    code, result = search_on_loopy(
                        _url,
                        args,
                        provide_space=provide_space
                    )
                    # Retrieve the result.
                    if code == 2:
                        # Word/meaning not found. If a desired information is
                        # received, do the stuff with it.
                        if "msg" in result:
                            bot.send_message(message.chat.id, result['msg'],
                                reply_to_message_id=message.message_id)
                        elif 'bot_send_message' in result:
                            bot_send_message(result['bot_send_message'], 
                                             **result['kwargs'])
                        else:
                            pass
                        
                        return 1, None
                    # Otherwise code is 0, do the action: return.
                    return 0, result
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        except NotImplementedError as e:
            # Explicitly raise an error to catch it then. Is used to skip the
            # search result at the current case.
            raise e
        except Exception as e:
            if callable(return_on_fail):
                return return_on_fail(e),
            return return_on_fail,
    
    # Define function: Whole search.
    def whole_search():
        # Perform search through the all requested sources.  See variable
        # `order` to view order.
        # 
        # :return: Either `1`, or a tuple `(word, meaning)`.
        while order:
            item = order.pop(0)
            source_type, parameters = item
            try:
                # Search for result. An exception may occur, so this is made
                # at a try-except stmt.
                search_result = search_at(source_type, parameters)
            except NotImplementedError:
                continue
            if search_result[0] != 1:
                # Desired result was received, it is a tuple `(0, result)`.
                _, result = search_result
                return result
        return 1  # Not found.

    # Get the result. It will be one of "1" (`str`) or the ``(word, meaning)''
    # (desired) tuple.
    result = whole_search()
    if result == 1:
        # All is considired to be done.
        # If smth. appears to be undone, it is unexpective.
        return
    
    word, meaning = result
    word = word.capitalize()

    return word, meaning


# Tests =======================================================================


mk_the_test = False
endwith_exit = False


def mktest(d: dict) -> typing.NoReturn:
    print(get_word_and_meaning(d, None))


pattern_1 = {
    "normal": "слов.+",
    "site": "слов*"
}
pattern_2 = {
    "normal": "сила",
    "site": "сила"
}
pattern_3 = {
    "normal": "текст",
    "site": "текст"
}

if mk_the_test:
    mktest(pattern_1)
    mktest(pattern_2)
    mktest(pattern_3)

if mk_the_test and endwith_exit:
    raise SystemExit(0)

del (
    mk_the_test, endwith_exit,
    pattern_1, pattern_2, pattern_3,
    mktest
    )


# =============================================================================
# == Functions for handlers ===================================================
# = + Helpers. Auxiliary functions ============================================


# Since v1.0.9.
def _make_move(message, letter: str, mentioned: Iterable) \
    -> Optional[tuple[str, str]]:
    """Make "move" at a game, checking for a word, whether exists.

    It may be not a full move. See also: `make_move`.
    The move's performing there is more complete.
    """
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    result = \
        get_word_and_meaning(letter, message, mentioned=mentioned)
    
    if result:
        word, meaning = result
        msg = word + ' (' + meaning + ')'
        return word, msg
    else:  
        # Question: What?
        pass


# Since v1.0.9.
def make_move(message: types.Message) -> typing.NoReturn:
    """Make a move at game "words". If it's the bot's move, perform the move.
    Otherwise rule the game:
    * search for named words to ensure they exist and
      do not allow to name words, which were had not been found.
    * Also, check, whether the word was named *in the order*,
    * and check for the repeated words, *not* to allow theirs naming.

    When it's the bot's move, also give the "definition" of named words in the
    brackets.

    Actually, the case of bot's unability to find a suitable word *can* happen,
    but the chance of it is *really* small. That's because the chance of that
    is so, expectably, when the word is taken from the site (see `_make_move`).
    That it all about the happenings in case of the bot's move.
    
    Тут считается, что е и ё -- одна буква.
    """
    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Ошибка: не найдено игру."
        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)
        raise NoSectionError

    # Get data.
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    cur_letter = section["letter"]
    mentioned = eval(section["mentioned"])

    dot = '.' * (random.choice([0, 1, 2]) < 1)
    # Considered to be meaning of a word, is ignored
    #                                      vvvvvvvvv
    local_pattern = r"(?s)!\s?(?:[-\w]+)(?:\s*\(.+\))?"
    #                            ^^^^^^ Is a word
    if (match := re.fullmatch(WORDS_GAME_PATTERN, message.text)) \
    and (n := message.from_user.id) in order:
        if is_private(message) and not (
            # Message's text matches '![ ]word[...]'.
            re.fullmatch(local_pattern, message.text)
            or
            # Message is a reply to the appropriate sender's message
            # (and its text matches '[ ]word[...]').
            ((reply := get_reply_message(message)) and
             reply.from_user.id == order[current - 1])
        ):
            # Message is neither a reply, nor a message with expected pattern.
            return

        if n != order[current]:
            answer_msg = (
                f"Не твой сейчас ход{dot}"
                # + f" Ход игрока {user_text_mention(user)}!"*
                # feature_exists('wrong-order-show_expected_user')
            )
            bot.send_message(message.chat.id, answer_msg,
                reply_to_message_id=message.message_id)
            return

        word = match.group(1)
        
        if cur_letter != ANY_LETTER and \
        word[0].lower().replace('ё', 'е') != cur_letter:
            # Letter, that the word starts with, is found as unappropriate.
            answer_msg = f"На букву {cur_letter!r}{dot}"
            bot.send_message(message.chat.id, answer_msg,
                reply_to_message_id=message.message_id)
            return

        try:
            # Assert that that word can be found via get_word_and_meaning's.
            # call.
            tmp_pattern = {
                'dictionary': word,
                'site': word
            }
            result = get_word_and_meaning(tmp_pattern, message=None)
            del tmp_pattern
            assert result
        except AttributeError:
            # Expectably, an error occured when sending a message while
            # doing stuff at get_word_and_meaning. It's not common, so let
            # it happen, letting the word being named,
            # and just inform via bot, as at logs, that this happened.
            bot_send_message(
                "Unexpected error! Searching for a word {0!r}".format(word)
                + " at game words, checking its existance, this occured. "
                "Used get_word_and_meaning, no message had been given at args."
                )
        except AssertionError:
            answer_msg = ("Вау. Кажется, я не знаю этого слова. Хотя, "
    "возможно, оно лежит где-то на полке в папке data, но я не смотрел."
    f" Переходи, пожалуйста{dot}") + \
    (" Что это слово значит? Ход не засчитан. Либо напиши ответом на это "
    "сообщение толкование слова, я его в словарь запишу, либо назови другое "
    f"слово. <strike>И вообще, это not implemented ещё{dot}</strike>") \
    * feature_exists('teach_word')
            bot.send_message(message.chat.id, answer_msg, parse_mode='html',
                reply_to_message_id=message.message_id)
            return

        if word.casefold() in map(casefold, mentioned):
            # Word was already mentioned earlier.
            answer_msg = f"Слово {word!r} уже было в этой игре{dot}"
            bot.send_message(message.chat.id, answer_msg,
                reply_to_message_id=message.message_id)
            return

        mentioned.append(word)
        res = word.lower().rstrip('ьъы')
        assert re.fullmatch(r"(?i)[-а-яё]+", res)
        # Question about assertions like this: Is/are they required?

        next_letter = letter = res[-1]  # Next letter.
        current = (current + 1) % len(order)

        if int(order[current]) == BOT_ID:
            # Bot's move. Perform it.

            # Normally this answer exists,
            # so normally this ``_make_move(...)''
            # gives a pair ``(word: str, message: str)''.            
            answer, msg = _make_move(message, letter, mentioned)

            current = (current + 1) % len(order)
            mentioned.append(answer)

            # Determine the value of next letter.
            next_letter = answer.lower().rstrip('ьъы')[-1]
            if next_letter == 'ё': next_letter = 'е'

            bot.send_message(message.chat.id, msg,
                reply_to_message_id=message.message_id)

            # perform_bots_move()
        else:
            # All is done. Do nothing.
            pass

        section["letter"] = next_letter
        section["current"] = str(current)
        section["mentioned"] = str(mentioned)

        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
    elif match:
        # # User, who sent a message, is not registered as a player,
        # # but maybe the sent message matches the pattern as in game.
        # msg = ...
        # bot.send_message(message.chat.id, msg,
        #     reply_to_message_id=message.message_id)
        pass


# Since v1.0.9.
def words_skip_move(message: types.Message) -> typing.NoReturn:
    """Skip the move at game "words".

    If it's a bot move after skipping, perform that move.
    """
    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')

    if not c.has_section(chat_id):
        # No game was found in that chat.
        msg = "Игра не найдена"
        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)
        return
    
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    current += 1
    current %= len(order)
    section["current"] = str(current)

    # Get the recent data.
    mentioned = eval(section["mentioned"])
    cur_letter = section["letter"]
    letter = cur_letter

    try:
        # Ensure things go great.
        result = _make_move(message, letter, mentioned)
        assert result
    except (Exception, AssertionError) as e:
        # Some error occured. Just change the current "next letter" to any.
        letter = ANY_LETTER
    
    if int(order[current]) == BOT_ID:
        # Bot's move is required. Perform it.

        # Normally this answer exists,
        # so normally this ``_make_move(...)''
        # gives a pair ``(word: str, message: str)''.
        answer, msg = _make_move(message, letter, mentioned)

        current = (current + 1) % len(order)
        mentioned.append(answer)

        # Determine the value of next letter.
        next_letter = answer.lower().rstrip('ьъы')[-1]
        if next_letter == 'ё': next_letter = 'е'

        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)

        # perform_bots_move()  # See def at version telethon v1.0.9.

        # Set the updated data.
        section["current"] = str(current)
        section["letter"] = next_letter
        section["mentioned"] = str(mentioned)
    else:
        # All is done. Notify the user about it.
        msg = "Ход пропущен."
        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)

    with open(filename, 'w', encoding='utf-8') as f:
        c.write(f)


# === Handlers ================================================================


# Since v1.0.9.
# Test-start, may be used for tests.
# See also: the command 'start' react.
@enabled()
def test_start_message(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    msg = "some msg.\n\n\
Ввод в режиме inline (перевод):"
    choices = INLINE_EXAMPLES
    url = "https://telegra.ph/Test-02-20-154"
    example = random.choice(choices)

    switch_cur_chat_button = InlineKeyboardButton(
        text="Да", switch_inline_query_current_chat=example
    )
    go_to_help_message = InlineKeyboardButton(
        text="Open help (test)", url=url
    )
    keyboard = InlineKeyboardMarkup([
        [switch_cur_chat_button],
        [go_to_help_message]
    ])
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)

    return "Success"


# Since v1.0.9.
@bot.message_handler(commands=['do'])
def do_action(message: types.Message):
    """Eval or exec the command.

    Action defaults `eval`.
    Is_coro defaults False.
    Syntax:
    "/do[ -password=<password>][ -time=<time>]"\
    "[ -action=<action>][ -is_coro=<...>]<code>"
    
    TIME    HH:MM (not all is *required*)
    ACTION  `eval` or `exec`
    IS_CORO true | false | yes | no
    """
    # examples for it:
    # /do -password=pw -action=eval code
    # /do -password=pw -time=mm:ss -action=eval code
    # exact example:
    # /do -password={some_password} 1+2 (it gives 3)

    # **NOTE**:
    # Some imports are made exactly here,
    # as this function's call is uncommon.

    sid = message.from_user.id  # Sender's id
    if sid not in ADMINS:
        return

    # Assume an appropriate folder exists.
    filename = LOCAL_LOGS
    mid = "{},{}".format(message.chat.id, message.message_id)

    # Do some stuff in order to let the polls tracker go further.
    try:
        with open(filename, encoding='utf-8') as f:
            _data = f.read().split('\n')
        if mid in _data:
            # Answer had been already given.
            return
    except OSError:
        pass
    except Exception as e:
        print(e)
    finally:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(mid)
            f.write('\n')

    pattern = (
        _cmd_pattern('do', flags='is')  # Command's pattern
        + r"(?: {1,2}-password=(" + r'\S+' + r"))?"  # Password
        + r"(?:\s+-time=(\d{,2}:\d{,2}))?"  # Time
        + r"(?:\s+-action=(exec|eval))?"  # Type of action
        + r"(?:\s+-is_coro=(true|yes|false|no)?)"  # Whether is coroutine
        + r"\s+(.+)"  # The code
    )
    string = message.text

    # Parse the text according to `pattern`, another local stuff.
    
    if not (match := re.fullmatch(pattern, string)):
        # Even not a respective pattern.
        return

    pw, time, *other = match.groups()
    if PASSWORD_ENABLED:
        from uniconfig import password as _password
        if time is not None:
            time = time.split(':')
        password = _password(sid, time=time)
        print('pw:', password)  # Be careful!
        if pw != password:
            return

    action, is_coro, code = other

    # Set defaults.
    if action is None:
        action = 'eval'
    if is_coro is None:
        is_coro = False

    if is_coro.lower() in ('true', 'yes'):
        is_coro = True
    else:
        is_coro = False

    action0 = action
    action = eval(action)

    # Evaluate or execute the code. Inform, if is required.
    try:
        if action is eval:
            res = eval(code)
            if is_coro:
                msg = "Request `/do ... is_coro=True` made\."
                bot_send_message(msg, parse_mode=MARKDOWN_V2)
            bot.send_message(message.chat.id, str(res),
                reply_to_message_id=message.message_id)
        elif action is exec:
            exec(code)
    except Exception as e:
        msg = f"Ошибка. __{e}__"  # TODO Test, do
        bot.send_message(message.chat.id, msg, parse_mode=MARKDOWN_V2,
            reply_to_message_id=message.message_id)


# Since v1.0.9.
@bot.message_handler(commands=commands('start'))
def start(message):
    """Answer the start message.

    Start message is a text message, starts with '/start'.
    See also: https://core.telegram.org/bots#commands.
    """
    _add_user(message.from_user.id)
    p = commands('start') + r'\s+[-=]?test'
    if 'test_start_message' in globals() and re.fullmatch(p, message.text):
        result = test_start_message(message)
        if result:  # If result appears `None`, consider message
                    # as unanswered and go to answer as to normal
                    # message "/start".
            # Comes here e.g. when @enabled(False) is set to
            # the test message trigger.
            return
    sid = message.from_user.id
    cid = message.chat.id
    
    msg = f"""\
Основные команды:
/start — это сообщение
/words — игра в слова. Глянь /words help.
/help — помощь по боту
/meaning — значение слова. Глянь /meaning для справки.

🔸Перевод текста
См. /help.
"""
    allow_links_to_all = False  # Whether viewing links to chats and channels
    # should be allowed to all users.
    if allow_links_to_all or is_participant(sid):
        def invite_link(chat_id_) -> str:
            # May be helpful: `export_chat_invite_link`.
            try:  # TODO Test
                link = bot.get_chat(chat_id_).invite_link
                if link is None:
                    bot_send_message(
                        "Chat invite line is None at chat {0}"
                        .format(chat_id_)
                    )
            except:
                link = "не найдено"
            return link

        channel = invite_link(CHANNEL)
        chat = invite_link(HEAD_CHAT)

        msg += f"""
Ссылки на материалы по курсу:
🔸канал: {channel}
🔸чат курса: {chat}
🔸файлы с занятий: https://t.me/c/1285323449/15
"""
    msg += """ 
Тест перевода:
"""
    msg = msg.replace('.', '\.')
    choices = INLINE_EXAMPLES
    example = random.choice(choices)

    button = InlineKeyboardButton(
        text="Да", switch_inline_query_current_chat=example
    )
    keyboard = InlineKeyboardMarkup([[button]])
    bot.send_message(message.chat.id, msg,
        parse_mode=MARKDOWN_V2,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

    
# Since v1.0.9.
@bot.message_handler(commands=["add_user", "add_users"])
def add_user_via_message(message):
    """Add the reply-to-message sender's ID to the IDs base."""
    _add_user(message.from_user.id)
    if (m := get_reply_message(message)):
        sid = m.from_user.id
        _add_user(sid)
        bot.send_message(message.chat.id, "Пользователь добавлен.")
    else:
        pass


# Since v1.0.9.
@bot.message_handler(regexp=commands('help'))
def send_help_message(message):
    """Answer the help message.

    Help message is '/help' or the same with parameters.
    See also: https://core.telegram.org/bots#commands.
    """
    _add_user(message.from_user.id)

    pattern = commands('help') + r'\s+[-+]?full'
    is_full = bool(re.fullmatch(pattern, message.text))
    is_not_full = not is_full
    # Mind escaping special symbols at the following.
    msg = f"""\
Переводчик на старославянский язык. Правило перевода: ввести в чате\
 слово "@{BOT_USERNAME}\
\" и, после пробела, — текст для перевода/транслитерации.
Для отправки текста из списка нажать на тот текст.{'''
 `-` Очень много символов за раз бот не может отправить, только около 220.
 `-` Возможные ошибки: недописывание символов.'''*is_full}

Ещё:
🔸игра в слова: см. `/words help`;
🔸значение слова: см. `/meaning help`;
🔸добавление приветствия: см. `/new_greeting help`.
{'''
`-` Полное сообщение — `/help full`.
'''*is_not_full}
{short_cright if is_not_full else full_cright}
"""
    for s in {'.', '(', ')', '_'}:
        msg = msg.replace(s, '\\' + s)
    h_text = "Руководство"
    h_url = HELP_URL
    help_message = InlineKeyboardButton(text=h_text, url=h_url)
    keyboard = InlineKeyboardMarkup([[help_message]])
    bot.send_message(message.chat.id, msg, reply_markup=keyboard,
        parse_mode=MARKDOWN_V2)


# Since v1.0.9.
@bot.message_handler(commands=['meaning'])
def send_meaning(message):
    """Send meaning of a word. See help for syntax.

    Syntax: either `/meaning word`, or `/meaning` in reply to the message with
    the word the meaning is searched for. Priority to search at the reply.
    """
    # **Note**: Priority to search for a word:
    # * dict. 1 ->
    # * dict. '3' ->
    # * in the exact place at the I-net; see code of `get_word_and_meaning`.
    # To view the dictionary, see object `d` at functions.py definition.
    
    _add_user(message.from_user.id)
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')

    # Get the word.
    try:
        cmd_pattern = _cmd_pattern('meaning')
        text = message.text
        word = re.fullmatch(cmd_pattern + r'\s*([-а-яё]+)', text).group(1)
    except:
        try:
            text = get_reply_message(message).text
            word = re.fullmatch(WORDS_GAME_PATTERN, text).group(1)
        except:
            msg = "Не распознано слово. Напиши либо в ответ на сообщение, \
где искомое слово, либо `/meaning слово`."
            bot.send_message(message.chat.id, msg,
                reply_to_message_id=message.message_id, parse_mode=MARKDOWN_V2)
            return
    
    # Search for the meaning, send an answer, replying.

    pattern = {
        'dictionary': word,
        'site': word
    }
    result = get_word_and_meaning(pattern, message)
    if not result:
        # Word wasn't found anywhere.
        # Note: It may be a possible issue, but here it is great because
        # of this: excpectably, it was going so because a `ValueError`
        # occured at the exact place.
        msg = "Слово не найдено."
        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)
        return

    # Otherwise word and it's meaning were found.
    _, meaning = result
    meaning = capitalized(meaning)

    bot.send_message(message.chat.id, meaning,
        reply_to_message_id=message.message_id)


# Since v1.0.9.
@bot.message_handler(regexp=commands('words') + ".*")
def react_game_words(message):
    """React the triggers at game "words"."""
    _add_user(message.from_user.id)
    chat = message.chat
    text = message.text
    scid = str(chat.id)  # scid -- string chat_id
    chat_id = scid  # Be careful: telethon does not recognize str object as a
                    # chat id if passed as an entity
                    # (e.g. while sending message via `send_message`)

    # Processing further actions may take a significant amount of time.
    # Notify the user about it.
    bot.send_chat_action(chat.id, 'typing')

    cmd_pattern = _cmd_pattern('words')

    def matches(regexp: str, mode='default') -> bool:
        _regexp = regexp  # Register local name.
        if mode == 'default':
            _regexp = r'\s+' + r'(?:' + _regexp + ')'
        regexp = cmd_pattern + _regexp
        return bool(re.fullmatch(regexp, text))

    help_pattern = \
    r'\s(?:[-—\s:]*)(?:правила|инструкция|команды|help)\s*\??'

    #
    # Define the main triggers. Firstly not the game "words" registering.
    #

    if matches(r'.*?\s+[-!]?skip', mode=0):
        # Skip the move.
        words_skip_move(message)
        return

    if matches(r'приостановить|pause'):
        # Pause the game.
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()  # TODO Such parts
        # Do plural `c` objects at this (whole) code really do a good job?

        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
           msg = "Игра не найдена."
           bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)
           return
        c[chat_id]['status'] = 'paused'
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Игра приостановлена. Продолжение: /words continue{dot}"
        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)

        return

    if matches(r'хватит|удалить игру|stop|delete'):
        # Delete the game.
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')

        if c.has_section(chat_id):
            c.remove_section(chat_id)
        else:
            msg = "Игра не найдена."
            bot.send_message(message.chat.id, msg,
                reply_to_message_id=message.message_id)
            return

        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

        dot = '.' * (random.random() > 1/2)
        msg = f"Текущая игра убрана{dot}"
        bot.send_message(message.chat.id, msg,
            reply_to_message_id=message.message_id)
        return

    if matches(r'очередь|порядок|order'):
        # Show the order of players.
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            bot.send_message(message.chat.id, "Игра в этом чате не найдена.")
            return

        section = c[chat_id]
        order = eval(section["order"])
        current = int(section["current"])
        uid = order[current]

        def get_user(uid_):
            try:
                user = bot.get_chat_member(chat.id, uid_).user
                return user
            except:
                pass
            raise BotException('not found')

        u = get_user(uid)
        order_ = ', '.join(map(
            full_name,
            [get_user(uid_) for uid_ in order]
            ))
        text_mention = user_text_mention(u, fill=None)
        msg = f"""Последовательность: {order_}
Сейчас ходит: {text_mention}"""
        bot.send_message(message.chat.id, msg, parse_mode='html')
        return

    if matches(help_pattern, mode=0):
        # Show the help message.
        bot.send_chat_action(chat.id, 'typing')
        mark_item_point = ' `-` '  # OR: '◽️'
        msg = f"""\
🔸_Начало игры_
В личной переписке: /words `[начать|start]` `[single]` \(`single` — игра \
самому\);
В группе: `/words пользователь\_1 ...`
{mark_item_point}Имена пользователей — упоминанием;
{mark_item_point}Если своё имя не указывать, оно первое в очереди\.

🔸_Хода_
{mark_item_point}В личной переписке: `!слово` либо `слово`;
{mark_item_point}В группе: либо `!слово`, либо `слово` в ответ на \
сообщение того, кто ходил прошлым\.
 `>` Иногда бот может медлить, ожидая секунд 5; это нормально\.

🔸_Другие:_
`/words pause``|``приостановить` — остановка игры;
`/words stop``|``delete|хватит|удалить игру` — прекратить игру и удалить;
`/words skip` — пропуск хода или, _заодно, постановка обнуления первой \
буквы в случае чего_;
`/words order``|``очередь|порядок` — порядок ходов, текущий игрок;
`/words help``|``правила|инструкция|команды` — это сообщение;
`/words continue``|``продолжить` — продолжение \(после `/words pause`\)\.
"""
        bot.send_message(message.chat.id, msg, parse_mode=MARKDOWN_V2)
        return

    if matches(r'продолжить|continue'):
        # Continue the game, if it had been paused before.
        bot.send_chat_action(chat.id, 'typing')

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
            bot.send_message(message.chat.id, msg,
                reply_to_message_id=message.message_id)
            return

    # Following is for registering the game.

    if is_private(message):
        # Sent the message "/words..." via private chat.
        # "Requested" the start of game via "/words[...]" at private chat.
        # Case of just "/words" goes also here.
        if 'single' in text:
            order = [message.from_user.id]
        else:
            order = [message.from_user.id, BOT_ID]
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
            if not re.search(r'начать|start', text):
                # Prevent the user's sending of just
                # "/words[@bot_username]"
                # of registering the new game.
                msg = "Игра уже есть. Новая игра: /words `начать|start`. " \
                      "Также см.: /words `help`."
                bot.send_message(message.chat.id, msg,
                    reply_to_message_id=message.message_id,
                    parse_mode=MARKDOWN_V2)
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
        bot.send_message(message.chat.id, "Done. Registered.")
    elif is_group(message):
        # Message was sent via group.

        def user_id_(e: 'Entity') -> Optional[int]:
            # Get a user id from an entity.
            # Return `user_id: int` on success, reply and return None is not found.

            # Reference:
            # https://core.telegram.org/bots/api#messageentity

            # Actually, text_link also can be a mention of a user,
            # e.g. when it is a `t.me/@id<USER_ID>`, but here it is considired
            # to be a wrong entity, as an official Telegram client commonly
            # provides an opportunity to make a mention via either mention,
            # or text mention.

            if e.type == 'text_mention':
                return e.user.id
            elif e.type == 'mention':
                users = load_users()
                # +1: Skips `@`
                uname = message.text[e.offset + 1 : e.offset + e.length]
                for user_id in users:
                    # TODO Test, do it
                    try:
                        _user = bot.get_chat_member(chat.id,
                                                    user_id).user
                        if _user and _user.username == uname:
                            return user_id
                    except:
                        # Well, let an error occur silently and just don't
                        # register the user, who hadn't been found. Note:
                        # expectably, he can be be added via "/add_user".
                        continue
                msg = f"Unknown user: @{uname}"
                bot.send_message(message.chat.id, msg)
            elif e.type == 'text_link':
                pass

        # Here is the order of players at the registering game.
        order: list = []
        for e in message.entities[1:]:
            maybe_user_id = user_id_(e)
            if maybe_user_id:
                order.append(maybe_user_id)
            else:
                # Some entity wasn't helpful to found an id.
                # Let the user do one or more of the following (^*):
                # - put any entity at a text and
                #   just ignore it there, if it is not a mention. E.g.,
                #   the user can put links to anything at that message.
                # - put an unrecognizable mention entity at the text, then
                #   just ignore it. Such a situation can happen when
                #   user's id is not in the base of users' IDs.
                pass
        if not order:
            # (^*): Still, when no users were registered, this case happens.
            # If the user really wants to play the game at his own at a group
            # chat (and even without the bot's moves), he maybe can do it by
            # registering the game with his own mention.
            # 
            # [^1]: "Maybe" means the following: if his client gives him an
            # appropriate chance and his id can be recognised at the code in
            # that way.

            # So, do not register the game if only command was passed.
            # It prevents the game restart at the case of unwanted click to
            # the command.
            return

        # Otherwise the message `message` is considered to be a request to
        # register the game at that chat.

        if (n := message.from_user.id) not in order:
            # Register that user, who requested this game's registration,
            # if he is not in order yet. Put him first.
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
            # the user wrote an exact text like
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
        bot.send_message(message.chat.id, "Done. Game registered.")
    else:
        # Chat's type is another.
        pass


# Since v1.0.9.
@bot.message_handler(commands=['greeting', 'new_greeting'])
def manage_greeting(message):
    """Manage the greeting of new chat member(s).

    Set new greeting via bot/manage existed.
    See the greeting's help message for description.
    It is shown on "/greeting help" or "/new_greeting help".
    """
    # Mind the Markdown/HTML escape or set.
    #
    # Possible: add Markdown/HTML. Also, doing a perfect function
    # of invite is a goal of not this bot.
    
    # Note: aiogram lib provides Message.get_command(), but it can be not
    # suitable here. The required command is to be defined here greatly.
    _pattern: str = (
    re.compile(r"[^@\w]")  # Such pattern is because ...
        .split(message[1:])  # `message[1:]` is like "\w+[@username][...]".
            [0]  # Only the command is needed here.
    )
    text = message.text
    
    def pattern(command_part, cont=r'(?!\w).*'):
        part = r'\s*[-\s]?' + command_part + cont
        return _pattern + part

    help_pattern = pattern(r'help')
    del_pattern = pattern(r'(?:del(?:ete)?|remove)')
    show_pattern = pattern(r'show')

    def match(regexp):
        return re.fullmatch(regexp, text)

    if match(help_pattern):
        sep = '🔸'
        dash = '-'
        reply_msg = ("Добавить текст приветствия: "
"<code>/new_greeting текст</code>. "
r"Доступная разметка: {user.method}, {mention(user)}, (1). Весь "
"текст — в HTML.") + r"""

Пример: <i>"Привет, {mention(user)}! Твое имя: {user.first_name}."</i>.
""" + f"""
{sep}Это сообщение: <code>/greeting help</code> или \
<code>/new_greeting help</code>;
{sep}Показать приветствие: <code>/greeting show</code>;
{sep}Удалить приветствие: одно из \
<code>/greeting del</code>, \
<code>/greeting delete</code>, \
<code>/greeting remove</code>;
Перед параметрами можно добавить тире, например, \
<code>/greeting {dash}del</code>.
(1): mentions — упоминания <i>добавленных пользователей</i> через запятую, \
bt_uname — @имя_бота, scright и fcright — длинный и короткий, \
соответственно, тексты копирайта.
"""
        bot.send_message(message.chat.id, reply_msg,
            reply_to_message_id=message.message_id, parse_mode='html')
        return
    else:
        data = load_json()
    
    section = str(message.chat.id)
    is_new_greeting = bool(match(commands('new_greeting')))
    should_set_new = True
    greeting_not_found_text = "Приветствия не найдено."

    if not is_new_greeting:
        should_set_new = False
        if match(del_pattern):
            case = 'delete'
            try:
                del data[section]
                deleted = True
            except:
                bot.send_message(message.chat.id, greeting_not_found_text,
                    reply_to_message_id=message.message_id)
                deleted = False
        elif match(show_pattern):
            case = 'show'
            try:
                greeting: str = data[section]
                bot.send_message(message.chat.id, greeting,
                    reply_to_message_id=message.message_id)
            except KeyError:
                bot.send_message(message.chat.id, greeting_not_found_text,
                    reply_to_message_id=message.message_id)
            return
        else:
            should_set_new = True

    if should_set_new:
        case = 'add'
        new_greeting_text_pattern = re.compile(
            _pattern + r'\s*(.+)',
            re.DOTALL
        )
        match = new_greeting_text_pattern.fullmatch(text)  # Always matches.
        greeting = match.group(1)
        data[section] = greeting

    with open(FILE_GREETING, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    if case == 'delete':
        if deleted:
            bot.send_message(message.chat.id, "Приветствие удалено.",
                reply_to_message_id=message.message_id)
    elif case == 'add':
        bot.send_message(message.chat.id, "Приветствие добавлено.",
            reply_to_message_id=message.message_id)


# Since v1.0.9.
@bot.message_handler(lambda message: message.new_chat_members)
def greet_new_chat_members(message: types.Message):
    """Welcome every new chat member.

    Strategy
    ^^^^^^^^

    If member joined a chat with chat_id==SPEAK_CHAT and is not a
    member of the head chat (with chat_id==HEAD_CHAT), ban him; otherwise he
    is considered to be a normal user to greet him at that chat. It is made in
    order to add some safety to the chat of speaking. If user/users joined an
    *another* chat, just greet him/them. If this chat is not with chat_id in
    [SPEAK_CHAT, HEAD_CHAT, TEST_CHAT], try to greet him using the greeting,
    set by using the command /add_greeting or similar to this text. If it
    doesn't goes still, try to greet with a default greeting. In this order,
    every new user (which is pointed as a user to greet; if not banned in case
    of upper-mentioned coinsedences) is welcomed with exactly one greeting.

    Notes
    *****

    However, when an **admin** added new chat member, that member is considired
    to be *not* banned in any case.
    """
    _add_user(message.from_user.id)
    
    should_greet_all = False
    # Only for chat with `chat_id == SPEAK_CHAT`.
    # Whether all new chat members should be greeted by the bot.
    # If not, it means that filtering is enabled. Filtering means greeting only
    # *those* chat members (new), who are found as participants of chat with
    # `chat_id == HEAD_CHAT`.

    users = message.new_chat_members

    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member and chat_member.is_admin():
            should_greet_all = True
    except:
        # Executing `bot.get_chat_member(...)` failed.
        pass

    uids = [u.id for u in users]
    for uid in uids:
        _add_user(uid)

    def _mentions(_users, *, escape=True, escape_with='html') -> str:
        # Return mentions of _users, separated by ', '.
        # HTML symbols are escaped (or not) in order to make an appropriate
        # message to send it then. TODO: Test such mentions + unescape.
        # E.g. this as a name: `<a href="google.com">Hello</a>`.
        # Some link(s) about es-pes at Telegram bots/(?)operations:
        # - https://core.telegram.org/bots/api#formatting-options
        # 
        # This action appears to be so common here, that this is a great to
        # make at as a call of a separate function. I. e., this function.

        escape = escape_with if escape else None
        def _escape(s, style=None) -> str:
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
                return html_escape(s)
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
            # Prevent the case when two bots were put at that chat together
            # and run simultaneously.
            # More precisely, greet than only if the working bot is a bot
            # with TOKEN==TOKEN_INIT.
            return
        should_ban = []
        if not should_greet_all:
            for user in users:
                if not is_participant(user.id):
                    should_ban.append(user)

        if should_ban:
            bot.send_message(message.chat.id,
                "Сюда можно онли участникам чата курса. Сóри.",
                reply_to_message_id=message.message_id)
            for u in should_ban:
                # See https://core.telegram.org/bots/api#banchatmember.
                bot.ban_chat_member(chat.id, u.id, until_date=0)

        should_greet = [user for user in users if user not in should_ban]
        if not should_greet:
            # No one found to greet him.
            return

        mentions = _mentions(should_greet)
        msg = f"""\
Привет, {mentions}!
Этот чат — флудилка. Ссылка на основной чат находится в \
закрепе. Бот может быть полезен аля-переводом текста на старославянский \
язык. Инструкция: см. /help@{BOT_USERNAME}.

{short_cright}
"""
        bot.send_message(message.chat.id, msg, parse_mode='html')
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
        bot.send_message(message.chat.id, msg, parse_mode='html')
    elif chat_id == TEST_CHAT:
        msg = f"""\
        {_mentions(users)}
        Этот чат — тестовый чат. 
        /start
        /help@{BOT_USERNAME}.
        """
        msg = dedent(msg)
        bot.send_message(message.chat.id, msg, parse_mode='html')
    else:
        mentions = _mentions(users)
        data = load_json()

        greeted = False  # Whether users had been greeted.
        # This variable is stored to prevent no greeting at the case
        # of unsuccessful evaluating of the string at greeting.

        try:
            if (k := str(chat_id)) in data:
                # However, this action is not complete when
                # it greets members separately and disallows greeting
                # them all in *one* message.
                # 
                greeting_given = data[k]
                for user in users:
                    source = eval(DEFAULT_GREETING_EVAL_SOURCE)
                    _msg = 'f' + repr(greeting_given)
                    msg = eval(_msg, source)
                    bot.send_message(message.chat.id, msg, parse_mode='html')
                greeted = True
        except Exception as e:
            raise BotException("Whoops, an error occured while greeting "
                "new chat member(s). "
                "Users joined: {0}. ".format(mentions)
                + "Text of the greeting: {0}".format(greeting_given))

        if not greeted:
            msg = eval(DEFAULT_GREETING)
            bot.send_message(message.chat.id, msg, parse_mode='html')


# Since v1.0.9.
@bot.inline_handler(lambda inline_query: 0 < len(inline_query.query) <= 255)
def answer_query(inline_query: types.InlineQuery):
    """Answer a non-empty query, but not big.
    
    See https://core.telegram.org/bots/api#inlinequery.
    See also: https://core.telegram.org/bots/#inline-mode.
    """
    _add_user(inline_query.from_user.id)
    try:
        answers = []  # Storage for the results.
        text = inline_query.query
        
        if any(text.startswith(k) for k in NAMES_REPLACE):
            show_text = text
            send_text = html_escape(text)

            for k in NAMES_REPLACE:
                # Replace each name occured here, at send_text and show_text.
                i1, i2 = NAMES_REPLACE[k]
                show_text = show_text.replace(k, i1)
                i1 = html_escape(i1)
                send_text = send_text.replace(k,
                    '<a href="tg://user?id={1}">{0}</a>'.format(i1, i2))

            zero_title = "Смена слов"
            zero_description = show_text
            zero_text = send_text
            parse_mode = 'html'

            zero_input_content = InputTextMessageContent(zero_text)
            item_0 = InlineQueryResultArticle(
                id='0',
                title=zero_title,
                description=zero_description,
                input_message_content=zero_input_content,
                parse_mode=parse_mode
            )
            answers.append(item_0)

        # parse_mode question  # TODO Solve this question.
        # Parse mode here — ?
        # And sending the text in HTML/Markdown.

        # Shortages:
        #  - c, g -- cyryllic, glagolitic
        #  - trg -- transliterated to Glagolitic
        # Same notation may be applied for other code-parts at this file.

        # thumb configs:
        c_url = A_CYRYLLIC
        g_url = A_GLAGOLITIC
        trg_url = A_LATER_GLAGOLITIC

        # title, text, description:
        c_title = "Перевод на кириллицу"
        c_text = translation(text, dest="cyryllic")
        c_description = c_text
        # ^ Cyryllic
        g_title = "Перевод на глаголицу"
        g_text = translation(text, dest="glagolitic")
        g_description = g_text
        # ^ Glagolitic
        trg_title = "Транслитерация на глаголицу"
        trg_text = glagolitic_transliterate(text)
        trg_description = trg_text
        # ^ transliterated to Glagolitic

        # input contents:
        c_input_content = InputTextMessageContent(c_text)
        g_input_content = InputTextMessageContent(g_text)
        trg_input_content = InputTextMessageContent(trg_text)

        # result ids':
        result_id_1 = '1'
        result_id_2 = '2'
        result_id_3 = '3'

        common_thumb_kwargs = dict(
            thumb_width=COMMON_THUMB_CONFIG['width'],
            thumb_height=COMMON_THUMB_CONFIG['height'],
        )

        # results:
        item_1 = InlineQueryResultArticle(
            id=result_id_1,
            title=c_title,
            description=c_description,
            input_message_content=c_input_content,
            thumb_url=c_url,
            **common_thumb_kwargs
        )
        item_2 = InlineQueryResultArticle(
            id=result_id_2,
            title=g_title,
            description=g_description,
            input_message_content=c_input_content,
            thumb_url=g_url,
            **common_thumb_kwargs
        )
        item_3 = InlineQueryResultArticle(
            id=result_id_3,
            title=trg_title,
            description=trg_description,
            input_message_content=trg_input_content,
            thumb_url=trg_url,
            **common_thumb_kwargs
        )

        # answer
        answers = [item_1, item_2, item_3] + answers
        bot.answer_inline_query(inline_query.id, answers,
            is_personal=True, cache_time=CACHE_TIME)
    except Exception as e:
        print("{er_type}: {er_text}".format(
            er_type=type(e), er_text=e)
        )


# Since v1.0.9.
@bot.inline_handler(lambda inline_query: not inline_query.query)
def answer_empty_inline_query(inline_query: types.InlineQuery):
    """Answer any empty inline query."""
    _add_user(inline_query.from_user.id)
    try:
        # General
        title = "Перевод на славянские языки: кириллица, глаголица."
        description = "Введи текст для перевода, жми на нужный для отправки"
        
        # Other
        url = A_LATER_GLAGOLITIC
        common_thumb_kwargs = dict(
            thumb_width=COMMON_THUMB_CONFIG['width'],
            thumb_height=COMMON_THUMB_CONFIG['height'],
        )

        sample_to_translate = random.choice(INLINE_EXAMPLES)
        c_text = translation(sample_to_translate, dest="cyryllic")
        g_text = translation(sample_to_translate, dest="glagolitic")

        sample_to_translate = html_escape(sample_to_translate)
        c_text = html_escape(c_text)
        g_text = html_escape(g_text)

        text = """\
        <i>Пример перевода фразы "{0}".</i>
        
        Кириллица: {1}
        Глаголица: {2}
        """.format(
            sample_to_translate, c_text, g_text
        )
        text = dedent(text)

        input_content = InputTextMessageContent(text)
        item = InlineQueryResultArticle(
            id='0',
            title=title,
            description=description,
            input_message_content=input_content,
            parse_mode='html',
            thumb_url=url,
            **common_thumb_kwargs
        )
        bot.answer_inline_query(inline_query.id, [item],
            is_personal=True, cache_time=CACHE_TIME)
    except Exception as e:
        print(e)


# Since v1.0.9.
def realise_move(message) -> Optional[int]:
    """Realise a move at game "words".

    Returns
        Either 0, or None.
        ``0'' marks that response to the message has been made.
        ``None'' is returned otherwise.
    
    See also
    --------

    Sections at configuration files (config.py etc.):
    * section 'Game "word": data'.

    Constants:
    * re patterns: ``WORDS_GAME_PATTERNS''.

    Functions:
    * defined at this file: ``_make_move'', ``make_move''.
    """
    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
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
        # Game is paused.
        return

    if is_private(message):
        pattern = WORDS_GAME_PRIVATE_PATTERN
        match = re.fullmatch(pattern, message.text)
        if match:
            make_move(message)
            return 0
    else:
        pattern = WORDS_GAME_PATTERN
        match = re.fullmatch(pattern, message.text)
        if match:
            make_move(message)
            return 0


# Since v1.0.9.
@bot.message_handler()
def answer_message(message: types.Message):
    """Answer the text message.

    Actually, realises a move at game "words".
    """
    result = None

    # Following is a list containing functions to
    # try to call until the result ``0'' is received.
    # Order at this iterable is an order in which
    # the attemps, described in upper text, are made.
    to_call_possible = [realise_move]

    while to_call_possible and result != 0:
        func = to_call_possible.pop(0)
        result = func(message)


# Since v1.0.9.
bot.chosen_inline_handler(func=lambda _: True)
def chosen_inline_query_handler(chosen_inline_query: ChosenInlineResult):
    """Handle the received chosen inline result update.

    See https://core.telegram.org/bots/api#choseninlineresult,
    https://core.telegram.org/bots/inline#collecting-feedback.
    """
    mention = user_text_mention(chosen_inline_query.from_user)
    msg = f"""\
    result_id: {chosen_inline_query.result_id}
    Query is from {mention}.
    Query's query: {chosen_inline_query.query}
    """
    msg = dedent(msg)
    bot_send_message(msg, chat_id=LOGGING_CHAT_INLINE_FEEDBACK,
        parse_mode='html')


# Since v1.0.9.
def main():
    """Run the bot."""
    print("Version: telebot. Running the bot.")
    bot.infinity_polling()


if __name__ == '__main__':
    main()
