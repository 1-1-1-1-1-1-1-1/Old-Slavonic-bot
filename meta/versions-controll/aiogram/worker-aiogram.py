# -*- coding: utf-8 -*-
# version: aiogram:1.0.6

# THIS CODE AND APP ARE FREE FOR USAGE AND MAINTAINED & DISTRIBUTED UNDER THE
# TERMS OF *MIT License*. See LICENSE for more info.
# 
# The code is FREE FOR COPY, CHANGE, AND THE CODE's SHARING.  (?) **QUESTION**
# ---------------
# NOTE ALSO: The terms, under which the product is distributed, may be edited
# or changed at the future.  See the file LICENSE for info.
# =============================================================================
# Main file, written preferably with PEP8, required modules/libraries
# are in requirements.txt.
# 
# -----------------------------------------------------------------------------
# See also:
# - README for some info
# - metalog for some instant/following/current changes
# - config.py to view or change the configurations; also, .env or its analogues
# - launcher and similar to have a help (maybe) with launching the bot app
# Requires Python >=3.8 to allow the use of `:=`
# set the required version at runtime.txt (see also: runtime info at [1])
# 
# [1]: https://devcenter.heroku.com/articles/python-runtimes#supported-runtime-versions
# -----------------------------------------------------------------------------
# Since 27.06.2021 -- rewriting to aiogram
# NOTE: telethon/telebot versions may be still here, also devepeloped &
# maintained
# 
# Developer marks & notes
# -----------------------
# 
# - here 2 files are edited simultaneously: this and with telethon version. See
#   to merge (main difference/to merge -- all this notes, at the beg. of file)
# - configparser.ConfigParser() is sometimes created exactly at the function's
#   call, which is to work correctly, if several users use a bot simultaneously
# - TODO: test: triggers to start, words, BotException (see comments)
# - meta at this file (dev): note, *question*/*questions* (different), mark
#   (only previous), checked, to test/to check, test, TODO, meta, OR, task
#    + these are sometimes not case-sensitive
# - See PEP440 about version format standart
# - Another TODO: merge TODO, questions etc. from other versions.

import random
import re
from os.path import join
import asyncio
import urllib, warnings  # are not really required, but required

import requests
from aiogram import types
from aiogram.types import (
    # inline keyboard:
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    # inline bot results:
    InputTextMessageContent,
    InlineQueryResultArticle
    )

from config import (
    # some bot-connected constants:
    TOKEN, CACHE_TIME, NAMES_REPLACE, UIDS_BASE,
    # pics:
    A_CYRYLLIC, A_GLAGOLIC, A_LATER_GLAGOLIC,
    # technical:
    ANY_LETTER,
    ADMINS, LOGGING_CHAT, HELP_URL,
    PROD, PASSWORD_ENABLED, ON_HEROKU, CHAT_LOGS_MODE_ALL,
    # configparser:
    configparser, NoSectionError,
    # chats:
    CHANNEL, TEST_CHAT, SPEAK_CHAT, HEAD_CHAT,
    # other/unsorted:
    bot, BOT_ID, BOT_USERNAME,
    WORDS_GAME_PATTERN,
    INLINE_EXAMPLES,
    GAME_WORDS_DATA,
    TOKEN_INIT,
    COMMON_THUMB_CONFIG,
    LOCAL_LOGS
    )
from functions import translation, glagolic_transliterate
from functions import d as _d
from meta.edit_date import short_cright, full_cright  # <- meta


edit_note = r"end of June, 2021: 30.06.2021"
# ^ dummy, to check for updates while running.

# checked
async def bot_inform(text, chat_id=LOGGING_CHAT, type_=None, **kwargs):
    if type_ is not None and type_ not in CHAT_LOGS_MODE_ALL:
        return
    await bot.send_message(chat_id, text, **kwargs)

# *comments* (task): do, +applications
class BotException(Exception):
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

        future = bot_inform(text, type_='bot-exception', parse_mode='MarkdownV2')
        asyncio.get_event_loop().run_until_complete(future)

# test
# d = dict(chat_id='chat_id', user_id=0)
# raise BotException('test', extra=d)

# checked; *question*: loop
loop = asyncio.get_event_loop()
prod_word = "" if PROD else 'not '
on_heroku = 'yes' if ON_HEROKU else 'no'
text = f"""\
Launched the bot.
Is <u>{prod_word}the production</u> version.
Is whether on Heroku: <u>{on_heroku}</u>.
"""
future = bot_inform(text, type_="launch", parse_mode='HTML')
loop.run_until_complete(future)
# test
loop.run_until_complete(
    bot.send_message(699642076, 'Test #1')
)
del text, ON_HEROKU, on_heroku, future, loop


# v:1.0.6
# checked
def _cmd_pattern(cmd: str, *, flags='i') -> str:  # Internal
    if flags:
        _flags_add = r'(?' + flags + r')'
    else:
        _flags_add = ""
    cmd_pattern = _flags_add + r'/' + cmd + r'(?:@' + BOT_USERNAME + r')?'
    return cmd_pattern

# v:1.0.6
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

# v:1.0.6
# checked
def feature_exists(fid):  # Internal
    d = {
        'teach_word': False
    }
    if fid in d:
        return d[fid]
    return False

# checked; *question*: if not chat member -- ?
async def is_participant(user_id, of=HEAD_CHAT):
    """User is participant of chat `of`, returns bool."""
    return (await bot.get_chat_member(of, user_id)).is_chat_member()
print(is_participant(ADMINS[0]))  # test
raise SystemExit


# v1.0.6
# Tested for 2**2 different cases of (case, is_coro), when they are
# :obj:`bool`.
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
        await bot_inform(text, type_='new user', parse_mode='HTML')
        data_ += suid + '\n'
    with open(filename, 'a', encoding='utf8') as f:
        f.write(data_)


# v1.0.6
def full_name(user):
    """Full name of a user."""
    return f'{user.first_name}{" " + u if (u := user.last_name) else ""}'

# v1.0.6
def user_text_mention(user, fill=None) -> str:
    """Text mention of a user."""
    # :param fill: text to insert at mention
    # Link: https://core.telegram.org/bots/api#formatting-options.
    if fill is None:
        filling = full_name(user)
    else:
        filling = fill
    return f'<a href="tg://user?id={user.id}">{filling}</a>'


# v1.0.6
def is_private(message) -> bool:
    return message.chat.type == 'private'

# v1.0.6
def is_group(message) -> bool:
    # See e.g. "type" at https://core.telegram.org/bots/api#chat
    return 'group' in message.chat.type

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


# get_word_and_meaning def

# checked
async def make_move(message, letter, mentioned):
    """Make move at a game, checking for a word, whether exists."""
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, 'typing')
    _, word, meaning = await \
        get_word_and_meaning(letter, message, mentioned=mentioned,
            increase_allowed=True)
    msg = word + ' (' + meaning + ')'
    return word, msg


# checked
async def play_words(message, current=0):
    # """Да, тут считают, что е и ё -- одна буква."""

    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Ошибка: не найдено игру."
        await message.reply(msg)
        raise NoSectionError
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    cur_letter = section["letter"]
    mentioned = eval(section["mentioned"])

    dot = '.' * (random.choice([0, 1, 2]) < 1)
    local_pattern = r"(?s)!\s?([-\w]+)(?:\s*\(.+\))?"
    if (n := message.from_user.id) in order and \
        (match := re.fullmatch(WORDS_GAME_PATTERN, message.text)):
        if is_private(message) and not (
            re.fullmatch(local_pattern, message.text) or
            (message.reply_to_message and
            message.reply_to_message.from_user.id == order[current - 1])):
            return
        if n != order[current]:
            answer_msg = f"Не твой сейчас ход{dot}"  # \ 
            # f" Ход игрока {user_text_mention(user)}!"
            await message.reply(answer_msg)
            return  #~  # <- *question:* why `~`?
        word = match.group(1)
        print(word)  # test
        if cur_letter != "." and word[0].lower().replace('ё', 'е') != cur_letter:
            answer_msg = f"На букву {cur_letter!r}{dot}"
            await message.reply(answer_msg)
            return
        if requests.get(f"https://loopy.ru/?word={word}&def=").status_code \
            == 404:
            answer_msg = "Вау. Кажется, я не знаю этого слова. Хотя, \
возможно, оно лежит где-то на полке в папке data, но я не смотрел." \
 + f" Переходи, пожалуйста{dot}" + " Что \
это слово значит? (Ход не засчитан. Потом либо напиши ответом на это \
сообщение толкование слова, я его в словарь запишу, либо назови другое \
слово. И вообще, это not implemented ещё{dot})"*feature_exists('teach_word')
            await message.reply(answer_msg)
            return
        if word.casefold() in map(lambda s: s.casefold(), mentioned):
            answer_msg = f"Слово {word!r} уже было в этой игре{dot}"
            await message.reply(answer_msg)
            return
        mentioned.append(word)
        res = word.lower().rstrip('ь')
        assert re.fullmatch("(?i)[-а-яё]+", res)
        # ^ *question about assertions like this*: is/are required?
        letter = res[-1]
        section["letter"] = letter
        current = (current + 1) % len(order)
        if int(order[current]) == BOT_ID:
            # Bot's move.

            try:
                answer, msg = await make_move(message, letter, mentioned)
            except Exception as e:
                print(e)
                return

            current = (current + 1) % len(order)

            mentioned.append(answer)

            next_let = answer.lower().rstrip('ьъ')[-1]
            if next_let == 'ё': next_let = 'е'
            section["letter"] = next_let

            await message.reply(msg)

        section["current"] = str(current)
        section["mentioned"] = str(mentioned)

        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)


# v1.0.6
# test-start, may be used for tests
# see the `start` command
@enabled(is_coro=True)
async def test_start_message(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    msg = "some msg.\n\n\
Ввод в режиме inline (перевод):"
    choices = INLINE_EXAMPLES
    url = "https://telegra.ph/Test-02-20-154"  # test
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
    await message.answer(msg, reply_markup=keyboard)

    return "Success"  # required?


# v1.0.6
# examples for it:
# /do -password=pw -action=eval code
# /do -password=pw -time=mm:ss -action=eval code
# exact example:
# /do -password={some_password} 1+2 (it gives 3)
@dp.message_handler(regexp=commands('do') + '.*')
async def do_action(message: types.Message):
    # **NOTE**:
    # Some imports were made exactly here,
    # as this function's call is uncommon
    sid = message.from_user.id
    if sid not in ADMINS:
        return

    # Assume an appropriate folder exists
    filename = LOCAL_LOGS
    mid = "{},{}".format(message.chat.id, message.id)

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
    string = message.text
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
            await message.reply(str(res))
        elif action is exec:
            exec(code)
    except Exception as e:
        msg = f"Ошибка. __{e}__"  # to test
        await message.reply(msg, parse_mode='MarkdownV2')


# v1.0.6
@dp.message_handler(regexp=commands('start') + '.*')
async def start(message):
    """Answer the start message.

    Start message is a text message, starts with '/start'.
    See also: https://core.telegram.org/bots#commands.
    """
    await _add_user(message.from_user.id)
    p = commands('start') + r'\s+[-=]?test'
    if 'test_start_message' in globals() and re.fullmatch(p, message.text):
        await test_start_message(message)
        return
    sid = message.from_user.id
    cid = message.chat.id
    is_test = False

    header = r"\[test]"*is_test

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
    allow_links_to_all = False
    if allow_links_to_all or await is_participant(sid):
        async def invite_link(chat_id_):
            # may be helpful: `export_chat_invite_link`
            try:  # TODO Test
                link = (await bot.get_chat(chat_id_)).invite_link
            except:
                link = "не найдено"
            return link

        channel_link = await invite_link(CHANNEL)
        chat_link = await invite_link(HEAD_CHAT)

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

    button = InlineKeyboardButton(
        text="Да", switch_inline_query_current_chat=example
    )
    keyboard = InlineKeyboardMarkup([[button]])
    await message.answer(msg, parse_mode='MarkdownV2',
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

    
# v1.0.6
@dp.message_handler(regexp=commands("add_user", "add_users") + ".*")
async def add_user_via_message(message):
    """Add the reply-to-message sender's ID to the IDs base."""
    await _add_user(message.from_user.id)
    if (m := message.reply_to_message):
        sid = m.from_user.id
        await _add_user(sid)
        await message.answer("Пользователь добавлен.")


# v1.0.6
@dp.message_handler(regexp=commands('help') + ".*")
async def send_help_msg(message):
    """Answer the help message.

    Help message is '/help' or the same with parameters.
    See also: https://core.telegram.org/bots#commands.
    """
    await _add_user(message.from_user.id)
    pattern = commands('help') + r'\s+[-+]?full'
    is_full = re.fullmatch(pattern, message.text)
    is_not_full = not is_full
    msg = f"""\
Переводчик на старославянский язык. Правило перевода: ввести в чате\
 слово "@{BOT_USERNAME}\
\" и, после пробела, — текст для перевода/транслитерации.
Для отправки текста из списка нажать на тот текст.{'''
 `-` Очень много символов за раз бот не может отправить, только около 220.
 `-` Возможные ошибки: недописывание символов.'''*is_full}

Ещё:
🔸игра в слова (см. `/words help`);
🔸значение слова: \
см. /meaning help.
{'''
`-` Полное сообщение — `/help full`.
'''*is_not_full}
{short_cright if is_not_full else full_cright}
"""
    h_text = "Руководство"
    h_url = HELP_URL
    help_message = InlineKeyboardButton(text=h_text, url=h_url)
    keyboard = InlineKeyboardMarkup([[help_message]])
    await message.answer(msg, parse_mode='MarkdownV2', reply_markup=keyboard)


# v1.0.6
# checked
async def words_skip_move(message: types.Message):
    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
    filename = GAME_WORDS_DATA
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Игра не найдена"
        await message.reply(msg)
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
        answer, msg = await make_move(message, letter, mentioned)

        current = (current + 1) % len(order)

        section["current"] = str(current)
        next_let = answer.lower().rstrip('ьъ')[-1]
        mentioned.append(answer)
        if next_let == 'ё': next_let = 'е'
        section["letter"] = next_let
        section["mentioned"] = str(mentioned)

        await message.reply(msg)
    else:
        msg = "Ход пропущен."
        await message.reply(msg)
    with open(filename, 'w', encoding='utf-8') as f:
        c.write(f)

    print('Performed skip of move.')  # test


# processing
@dp.message_handler(regexp=commands('meaning') + ".*")
async def send_meaning(message):
    """Send meaning of a word.  See help for syntax.

    Syntax: either `/meaning word`, or `/meaning` in reply to the message with
    the word the meaning searched for.  Priority to search at the reply.
    """
    # **Note**: Priority to search for a word:
    # dict. 1 -> dict. '3' -> in the exact place at the I-net.
    
    await _add_user(message.from_user.id)
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, 'typing')

    try:
        cmd_pattern = _cmd_pattern('meaning')
        text = message.text
        word = re.fullmatch(cmd_pattern + r'\s*([-а-яё]+)', text).group(1)
    except:
        try:
            text = message.reply_to_message.text
            word = re.fullmatch(WORDS_GAME_PATTERN, text).group(1)
        except:
            msg = "Не распознано слово. Напиши либо в ответ на сообщение, \
где искомое слово, либо `/meaning слово`."
            await message.reply(msg, parse_mode='MarkdownV2')
            return
    from functions import d as d0
    order = [1, '3']

    for k in order:
        try:
            d = d0[k]
            if await by_rule(k) != 0:
                continue
            return
        except:
            continue
        del d
    # _, meaning = \
    # await get_info_by_rule(word, k)
    # await message.reply(meaning)
    # return

    result = await get_word_and_meaning(word, message, strict_level=0)
    if result is not None and result[0] == 1:
        await message.reply(result[1])
    else:
        code, word, meaning = result
        await message.reply(meaning)

    '''  # to look
    if word is not None and meaning is not None:
        await message.reply(meaning)
        return

    
    del d0, order, by_rule

    url = f'https://loopy.ru/?word={word}&def='

    if (sc := (r := requests.get(url)).status_code) == 404:
        msg = f"Слово {word!r} не найдено в словаре."
        await message.answer(msg)
    elif sc != 200:
        msg = f"Непонятная ошибка. Код ошибки: {sc}."
        await message.answer(msg)
    else:
        rtext = r.text
        _rtext_part = rtext[rtext.find('Значения'):]
        try:  # *dev question*: great?
            rtext_part = _rtext_part
            rtext_part = rtext_part[:rtext_part.index('</div>')]
            finds = re.findall(r'<p>(.*?)</p>', rtext_part)[1:]
            # ^ *request question*: 1-st item here — a header?
            assert finds
        except AssertionError:
            rtext_part = _rtext_part
            rtext_part = rtext_part[:rtext_part.index('</ul>')]
            finds = re.findall(r'<li>(.*?)</li>', rtext_part)
            if not finds:
                text = \
                f"A <b>great</b> error occured: haven't found a meaning"
                " for {word!r}."
                await bot_inform(text, parse_mode='HTML')
        res = random.choice(finds)

        await message.reply(res)
    '''

# checked
@dp.message_handler(regexp=commands('words') + ".*")
async def react_game_words(message):  # TODO Merge with telethon v.
    """React commands and triggers at game 'words'."""
    await _add_user(message.from_user.id)
    chat = message.chat
    text = message.text
    scid = str(chat.id)  # scid -- string chat_id
    chat_id = scid  # Be careful: telethon does not recognize str object as a
                    # chat id if passed as an entity
                    # (e.g. while sending message via `send_message`)

    # Processing further actions may take a significant amount of time.
    await bot.send_chat_action(chat.id, 'typing')

    cmd_pattern = _cmd_pattern('words')
    help_pattern = cmd_pattern \
        + r'\s(?:[-—\s:]*)(?:правила|инструкция|команды|help)\s*\??'

    if re.fullmatch(cmd_pattern + r'.*?\s+[-!]?skip', text):
        await words_skip_move(message)
        return
    if re.fullmatch(cmd_pattern + r'\s+(?:приостановить|pause)', text):
        await bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()  # TODO Such parts
        # Is really plural `c` objects at this code (whole) a good work?

        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
           msg = "Игра не найдена."
           await message.reply(msg)
           return
        c[chat_id]['status'] = 'paused'
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Игра приостановлена. Продолжение: /words continue{dot}"
        await message.reply(msg)

        return
    if re.fullmatch(cmd_pattern + r'\s+(?:хватит|удалить игру|stop)', text):
        await bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
           c.remove_section(chat_id)
        else:
            msg = "Игра не найдена."
            await message.reply(msg)
            return
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Текущая игра убрана{dot}"
        await message.reply(msg)
        return
    if re.fullmatch(cmd_pattern + r'\s+(?:очередь|порядок|order)', text):
        await bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            await message.answer("Игра в этом чате не найдена.")
            return
        section = c[chat_id]
        order = eval(section["order"])
        current = int(section["current"])
        uid = order[current]

        async def get_user(uid_):
            try:
                user = (await bot.get_chat_member(chat.id, uid_)).user
                if user:
                    return user
            except:
                pass
            raise BotException('not found')
        u = await get_user(uid)
        order_ = ', '.join(map(
            full_name,
            [(await get_user(uid_)) for uid_ in order]
            ))
        text_mention = user_text_mention(u, fill=None)
        msg = f"""Последовательность: {order_}
Сейчас ходит: {text_mention}"""
        await message.answer(msg, parse_mode='HTML')
        return
    if re.fullmatch(help_pattern, text):
        await bot.send_chat_action(chat.id, 'typing')
        mark_item_point = ' `-` '  # OR: '◽️'
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
        await message.answer(msg, parse_mode='MarkdownV2')
        return

    if re.fullmatch(cmd_pattern + r'\s+(?:продолжить|continue)', text):
        await bot.send_chat_action(chat.id, 'typing')

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
            await message.reply(msg)

            return

    if is_private(message):
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
            if not re.search('(?:начать|start)', text):
                msg = "Игра уже есть. Новая игра: /words начать|start. " \
                      "Также см.: /words help."
                await message.reply(msg)
                return  # Do the game being not registered then.
        if not c.has_section(chat_id):
            c.add_section(chat_id)
        section = c[chat_id]
        section["order"] = str(order)
        section["current"] = str(current)
        section["letter"] = ANY_LETTER
        section["mentioned"] = str(mentioned)
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

        print("Registered. chat_id: " + chat_id)  # test
        await message.answer("Done. Registered.")
    elif is_group(message):
        if re.fullmatch(cmd_pattern, text):
            return
        group = chat.id
        async def user_id_(e: 'Entity') -> int:
            if e.type == 'text_mention':
                return e.user.id
            elif e.type == 'mention':
                users = load_users()
                # :note: +1: Skips `@`
                uname = message.text[e.offset + 1 : e.offset + e.length]
                for user_id in users:
                    #! TODO Test, do it first
                    if (_user := (await get_chat_member(user_id,
                                                        of=chat.id)).user) \
                    and _user.username == uname:
                        return user_id
                msg = f"Unknown user: @{uname}"
                await bot.reply(msg)

        order: list = []
        for e in message.entities[1:]:
            order.append(await user_id_(e))
        if None in order:
            return
        if (n := message.from_user.id) not in order:
            order = [n] + order
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            c.add_section(chat_id)
        section = c[chat_id]
        section["order"] = str(order)
        section["current"] = str(current)
        section["letter"] = ANY_LETTER
        section["mentioned"] = str(mentioned)
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

        print("Game registered. chat_id: " + chat_id)  # test
        await message.answer("Done. Game registered.")


...  # command to add a greeting, TODO. Firstly do at telethon v.


# TODO, also greetings new features, see telethon version code.
@dp.message_handler(func=lambda message: message.new_chat_members)
async def greet_new_chat_members(message: types.Message):
    """Welcome every new user"""
    # print(message)  # test
    await _add_user(message.from_user.id)
    should_greet_all = False
    members = message.new_chat_members
    members = users

    chat_id = message.chat.id
    user_id = message.from_user.id
    if (await bot.get_chat_member(chat_id, user_id)).is_admin():
        should_greet_all = True

    uids = [u.id for u in users]
    for uid in uids:
        await _add_user(uid)

    if chat_id == SPEAK_CHAT and TOKEN == TOKEN_INIT:
        should_ban = []
        if not should_greet_all:
            for user in users:
                if not await is_participant(user.id):
                    should_ban.append(user)

        if should_ban:
            await message.reply("Сюда можно онли участникам чата курса. Сóри.")
            for u in should_ban:
                await bot.restrict(chat.id, user.id, until_date=0)

        should_greet = [user for user in users if user not in should_ban]
        if not should_greet:
            return

        is_test_msg = False

        mentions = [user_text_mention(user) for user in should_greet]
        mentions = ", ".join(mentions)
        msg = f"""{"[Это тест.]"*is_test_msg}
Привет, {mentions}!
Этот чат — флудилка. Ссылка на основной чат находится в \
закрепе. Бот может быть полезен аля-переводом текста на старославянский \
язык. Инструкция: см. /help@{BOT_USERNAME}.

{short_cright}
"""
        await message.answer(msg, parse_mode='HTML')
    elif chat_id == HEAD_CHAT:
        msg = f"""\
Здравствуй, <a href="tg://user?id={user.id}">\
{user.first_name}{" " + u if (u := user.last_name) else ""}</a>!
Это основной чат курса, ссылка на флудилку есть в закрепе.
Бот может быть полезен аля-переводом текста на старославянский \
язык, транслитерацией в старославянские алфавиты. Инструкция: \
см. /help@{BOT_USERNAME}.
"""
        await message.answer(msg, parse_mode='HTML')
    elif chat_id == TEST_CHAT:
        msg = f"""\
{user_text_mention(user)}
Этот чат — тестовый чат. 
/start
/help@{BOT_USERNAME}.
"""
        await message.answer(msg, parse_mode='HTML')


# checked
@dp.inline_handler(func=lambda inline_query: 0 < len(inline_query.query) <= 255)
async def answer_query(inline_query: types.InlineQuery):
    """Answer a non-empty query, but not big.
    
    See https://core.telegram.org/bots/api#inlinequery.
    See also: https://core.telegram.org/bots/#inline-mode.
    """
    await _add_user(inline_query.from_user.id)
    try:
        answers = []
        text = inline_query.query
        print('query:', text)  # test

        if any(text.startswith(k) for k in NAMES_REPLACE):
            show_text = text
            # ... Or do the following with `html.escape(text, quote=False)`,
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

            zero_title = "Смена слов"
            zero_description = show_text
            zero_text = text
            parse_mode = 'HTML'  # *question:here* pretty nice?

            zero_input_content = InputTextMessageContent(zero_text)
            item_0 = InlineQueryResultArticle(
                    id='0',
                    title=zero_title,
                    description=zero_description,
                    input_message_content=zero_input_content,
                    parse_mode=parse_mode
            )
            answers.append(item_0)

        text = message.text

        # parse_mode *question*
        # Parse mode here — ?
        # And sending the text in HTML/Markdown.

        # *dev note*: Shortages here:
        #  - c, g -- cyryllic, glagolic
        #  - trg -- transliterated (to) glagolic

        # thumb configs:
        c_url = A_CYRYLLIC
        g_url = A_GLAGOLIC
        trg_url = A_LATER_GLAGOLIC

        # title, text, description:
        c_title = "Перевод на кириллицу"
        c_text = translation(text, dest="cyryllic")
        c_description = c_text
        # ^ cyryllic
        g_title = "Перевод на глаголицу"
        g_text = translation(text, dest="glagolic")
        g_description = g_text
        # ^ glagolic
        trg_title = "Транслитерация на глаголицу"
        trg_text = glagolic_transliterate(text)
        trg_description = trg_text
        # ^ transliterated to glagolic

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
        await bot.answer_inline_query(answers, cache_time=CACHE_TIME)
    except Exception as e:
        print(type(e), ': ', e, sep='')


# checked
@dp.inline_handler(func=lambda inline_query: not inline_query.query)
async def answer_empty_inline_query(inline_query: types.InlineQuery):
    """Answer any empty inline query."""
    await _add_user(inline_query.from_user.id)
    try:
        # general
        title = "Перевод на славянские языки: кириллица, глаголица."
        description = "Введи текст для перевода, жми на нужный для отправки"
        
        # other
        text = 'no text'
        input_content = InputTextMessageContent(text)
        url = A_LATER_GLAGOLIC  # thumb url
        common_thumb_kwargs = dict(
            thumb_width=COMMON_THUMB_CONFIG['width'],
            thumb_height=COMMON_THUMB_CONFIG['height'],
        )

        item = InlineQueryResultArticle(
                id='0',  # id -- dummy ('any' string)
                title=title,
                description=description,
                input_message_content=input_content,
                thumb_url=url,
                **common_thumb_kwargs
        )
        await bot.answer_inline_query([item], cache_time=CACHE_TIME)
    except Exception as e:
        print(e)


# checked
@dp.message_handler()
async def answer_message(message: types.Message):
    """Answer the text message.

    Actually, realises a move at game words.
    """
    await _add_user(message.from_user.id)
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
        return

    if is_private(message):
        pattern = r'(?i)\!?[-а-яё]+'
        if (s := re.fullmatch(pattern, message.text)):
            await play_words(message)
    else:
        pattern = WORDS_GAME_PATTERN
        if re.fullmatch(pattern, message.text):
            await play_words(message)


if __name__ == '__main__':
    with bot:  # *dev question*: what?
        print('Starting polling... (aiogram version)')
        executor.start_polling(dp, skip_updates=False)
