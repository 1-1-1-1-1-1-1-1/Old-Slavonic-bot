# main (init) file, written preferably with PEP8, required modules/libraries
# are in requirements.txt.
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
# --- -
# *marks* (dev.)
# - this can help to ignore further triggers for an exact update:
#   `raise events.StopPropagation`
# - see *questions*/*question*
# - see *mark* (maybe), and also: file metalog
# - see the `aiogram` version worker[.py] for info


import random
import re
from os.path import join
import asyncio
import typing
import logging

import requests
import telethon
from telethon import sync  # (maybe not required, but let it be)

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
    TOKEN, CACHE_TIME, NAMES_REPLACE, UIDS_BASE,
    # pics:
    A_CYRYLLIC, A_GLAGOLIC, A_LATER_GLAGOLIC,
    # technical
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
    COMMON_THUMB_CONFIG
    )
from functions import translation, glagolic_transliterate


logformat = '[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s'
logging.basicConfig(format=logformat,
                    level=logging.WARNING)


edit_note = r"end of June, 2021: 30.06.2021"
# ^ dummy, to check for updates while running.


async def bot_inform(text, chat_id=LOGGING_CHAT, type_=None, **kwargs):
    if type_ is not None and type_ not in CHAT_LOGS_MODE_ALL:
        return
    await bot.send_message(chat_id, text, **kwargs)

# TODO: do great
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


def _cmd_pattern(cmd: str, *, flags: typing.Union[None, 'empty', str] = 'i') \
        -> str:  # Internal
    if flags:
        _flags_add = r'(?' + flags + r')'
    else:
        _flags_add = ""
    cmd_pattern = _flags_add + r'/' + cmd + r'(?:@' + BOT_USERNAME + r')?'
    return cmd_pattern


def commands(*cmds, flags: typing.Union[None, 'empty', str] = None) \
        -> str:  # Internal
    if flags is not None:
        kwargs = {'flags': flags}
    else:
        kwargs = {}
    if len(cmds) == 1:
        cmd_styled = cmds[0]
    else:
        cmd_styled = r'(?:' + '|'.join(cmds) + r')'
    return _cmd_pattern(cmd_styled, **kwargs)


def feature_exists(fid):  # Internal
    d = {
    'teach_word': False
    }
    if fid in d:
        return d[fid]
    return False


async def is_participant(user_id, of=HEAD_CHAT):
    """User is participant of chat `of`, returns bool."""
    try:
        return not (await bot.get_permissions(of, user_id)).has_left
    except (ValueError, errors.UserNotParticipantError):
        return False


async def _add_user(user_id):
    """Add ID to the base. Comments are allowed."""
    filename = UIDS_BASE
    with open(filename, 'a') as f:
        pass
    with open(filename, 'r', encoding='utf8') as f:
        data = f.read()
    data_ = ""
    if data and data.rstrip('\n') == data:
        data_ += '\n'
    if (s := str(user_id)) not in data:
        text = 'New user: \
<a href="tg://user?id={0}">{1}</a>\nuser_id: {0}'.format(
            user_id, "User")
        await bot_inform(text, type_='new user', parse_mode='html')
        data_ += s + '\n'
    with open(filename, 'a', encoding='utf8') as f:
        f.write(data_)


def full_name(user):
    return f'{user.first_name}{" " + u if (u := user.last_name) else ""}'


def user_text_mention(user, fill=None):
    # `fill` : text to insert at mention
    if fill is None:
        filling = full_name(user)
    else:
        filling = fill
    return f'<a href="tg://user?id={user.id}">{filling}</a>'


def load_users():
    # NOTE: Return is a generator object!
    with open(UIDS_BASE, encoding='utf-8') as f:
        users = map(eval, f.read().strip().split('\n'))
    return users


# to test, assumed to be ready
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
        # meta: `*a*nswer, *q*uestion`
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
# TODO: check, test
async def make_move(event, letter, mentioned):
    chat_id = event.chat.id
    bot.action(chat_id, 'typing')
    try:
        from functions import d as _d
        try:
            d = _d[1]
            vars_ = {k: d[k] for k in d
                if k.lower().startswith(letter) and
                k.lower() not in (item.lower() for item in mentioned) and
                re.fullmatch(r'[-\w]+', k)}
            assert vars_

            def _answer(i):
                p = possible[i]
                return p[0]
            def _description(i):
                p = possible[i]
                return p[1]
        except AssertionError:
            d = _d['3']
            vars_ = {k: d[k] for k in d
                if k.lower().startswith(letter) and
                k.lower() not in (item.lower() for item in mentioned) and
                re.fullmatch(r'[-\w]+', k)}
            assert vars_

            def _answer(i):
                p = possible[i]
                return p[0]
            def _description(i):
                p = possible[i]
                return p[1]
        finally:
            del _d, d

        possible = list(vars_.items())  # Should be here?
        i = random.choice(range(len(possible)))

        answer = _answer(i).capitalize()
        description = _description(i)

        msg = answer + ' (' + description + ')'
        return answer, msg
    except AssertionError:
        maxn = 4  # perfect?
        possible = list(range(1, maxn))
        res_word = None

        while not res_word and maxn <= 20:
            possible.append(maxn)
            n = possible.pop(random.choice(range(len(possible))))
            url = "https://loopy.ru/?word={}{}&def=".format(letter, '*'*(n-1))
            r = requests.get(url)
            text = r.text

            base = re.finditer(r'<div class="wd">(?:.|\n)+?</div>', text)
            base = list(base)

            def word(item):
                return re.search(
                    r'<h3>.+?значение слова ([-\w]+).+?</h3>', item).group(1)

            def meanings(item):
                return re.findall(r'<p>(.+?)</p>', item)

            while base:
                item = base.pop(random.choice(range(len(base)))).group()
                _word = word(item)
                if _word not in mentioned:
                    res_word = _word
                    meaning = random.choice(meanings(item))

                    mentioned.append(_word)

                    break

            maxn += 1
        if res_word is None:
            msg = \
            "Wow! How can it happen? I had found any words for it."
            "Game is stopped. Realise move's skip to continue"  #!
            await event.reply(msg)  # continuing game -- ?
            return
        msg = res_word + ' (' + meaning + ')'

        return res_word, msg  # test st.  <- #?


async def play_words(event, current=0):
    # """Да, тут считают, что е и ё -- одна буква."""

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
            re.fullmatch(r"(?s)!\s?([-\w]+)(?:\s*\(.+\))?", event.text) or
            (get_reply_message(event) and  #(?)
            get_reply_message(event).from_user.id == order[current - 1])):
            return
        if n != order[current]:
            answer_msg = f"Не твой сейчас ход{dot}"  # " Ход игрока "
            # user_text_mention(user)!
            await event.reply(answer_msg)
            return  #~
        word = match.group(1)
        print(word)  # test
        if cur_letter != "." and word[0].lower().replace('ё', 'е') != cur_letter:
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
        assert re.fullmatch("(?i)[-а-яё]+", res)  # (*question*) required?
        letter = res[-1]
        section["letter"] = letter
        current = (current + 1) % len(order)
        if int(order[current]) == BOT_ID:
            print("Bot's move at game `words`")  # test

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

    raise events.StopPropagation


# add all users from either `NewMessage` or `InlineQuery`
@bot.on(InlineQuery)
@bot.on(events.NewMessage)
async def add_user(event):
    await _add_user(event.sender.id)


r'''
# test-start, may be used for tests
# see the `start` command
async def test_start_message(event):
    if event.sender.id not in ADMINS:
        return

    msg = "some msg.\n\n\
Ввод в режиме inline (перевод):"
    choices = INLINE_EXAMPLES
    HELP_URL = "https://telegra.ph/Test-02-20-154"  # test
    example = random.choice(choices)
    switch_cur_chat_button = types.InlineKeyboardButton(
        text="Да", switch_inline_query_current_chat=example)
    go_to_help_message = types.InlineKeyboardButton(
        text="Open help", url=HELP_URL)
    keyboard = types.InlineKeyboardMarkup([
        [switch_cur_chat_button],
        [go_to_help_message]
        ])
    event.respond(msg, reply_markup=keyboard)
    pass
'''

# examples for it:
# /do -password=pw -action=eval code
# /do -password=pw -time=mm:ss -action=eval code
@bot.on(events.NewMessage(pattern=commands('do')))
async def do_action(event):
    # NOTE:
    # Some imports were made exactly here,
    # as this function's call is uncommon
    sid = event.sender.id
    if sid not in ADMINS:
        return

    filename = join("locals", "do_logs.log")
    mid = "{},{}".format(event.chat.id, event.id)

    import os
    if not 'data' in os.listdir():
        os.mkdir('data')
    del os

    try:  # to let the polls tracker go further
        with open(filename, 'rt', encoding='utf-8') as f:
            _data = f.read().split('\n')
        if mid in _data:
            return
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)
    finally:
        with open(filename, 'at', encoding='utf-8') as f:
            f.write(mid)
            f.write('\n')

    pattern = (_cmd_pattern('do', flags='is')
        + r"(?: {1,2}-password=(" + r'\S+' + r"))?"
        + r"(?:\s+-time=(\d{,2}:\d{,2}))?"
        + r"(?:\s+-action=(exec|eval))?"
        + r"\s+(.+)")
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

# TODO: test it
@bot.on(events.NewMessage(pattern=commands('start')))
async def start(event):
    p = commands('start') + r'\s+[-=]?test'
    if 'test_start_message' in globals() and re.fullmatch(p, event.text):
        await test_start_message(event)
        return
    sid = event.sender.id

    test = False

    cid = event.chat.id

    header = "\[test]"*test
    # NOTES on happened:
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

# checked
@bot.on(events.NewMessage(pattern=commands('help')))
async def send_help_msg(event):
    msg = f"""\
Переводчик на старославянский язык. Правило перевода: ввести в чате\
 слово "@{BOT_USERNAME}\
\" и, после пробела, — текст для перевода.
Для отправки текста из списка нажать на тот текст.
 `-` Очень много символов за раз бот не может отправить, только около 220.
 `-` Возможные ошибки: недописывание символов.

Ещё:
 `-` игра в слова (см. `/words help`);
 `-` значение слова: \
см. /meaning help.
"""
    h_text = "Руководство"
    h_url = HELP_URL
    help_message = Button.url(h_text, url=h_url)
    await event.respond(msg, parse_mode='md', buttons=help_message)
    raise events.StopPropagation

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

# 3
@bot.on(events.NewMessage(pattern=commands('meaning')))
async def send_meaning(event):
    """Priority to search for a word:
    dict. 1 -> dict. '3' -> in the exact place at the I-net.
    """
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

# 5
async def _react_game_words(event):
    chat = event.chat
    text = event.text

    # Processing further actions may take a significant amount of time.
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
        chat_id = str(chat.id)
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
        chat_id = str(chat.id)
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
        chat_id = str(chat.id)
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            await event.respond("Игра в этом чате не найдена.")
            return
        section = c[chat_id]
        order = eval(section["order"])
        current = int(section["current"])
        uid = order[current]

        async def get_user(uid_):
            async for user in bot.iter_participants(chat.id):
                if user.id == uid_:
                    return user
            raise BotException('not found')  # TODO
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
        chat_id = str(chat.id)
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
        if 'single' in text:
            order = [event.sender.id]
        else:
            order = [event.sender.id, BOT_ID]
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = GAME_WORDS_DATA
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
            if not re.search('(?:начать|start)', text):
                msg = "Игра уже есть. Новая игра: /words начать|start. " \
                      "Также см.: /words help."
                await event.reply(msg)
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
        await event.respond("Done. Registered.")
    elif event.is_group:
        if re.fullmatch(cmd_pattern, text):
            return
        group = chat.id
        # can be helpful here: `bot.get_participants(group)`
        async def user_id_(e: 'Entity') -> int:  # TODO: do it
            # expectable:
            # - MessageEntityUnknown,  # what?
            # - MessageEntityMention,
            # - MessageEntityMentionName,
            # - InputMessageEntityMentionName

            other = (
                MessageEntityUnknown,
                InputMessageEntityMentionName
                )
            if isinstance(e, MessageEntityMention):
                index = e.offset
                # +1: Skips `@`
                text = event.text
                uname = text[index + 1 : index + e.length]
                return (await bot.get_entity(uname)).id
            elif isinstance(e, MessageEntityMentionName):
                return e.user_id
            elif isinstance(e, other):
                text = f'Unexpected! Type of entity (reg. game):'
                bot_inform(text + ' ' + str(e))
                print(text, e)

        order: list = []
        for e in event.entities[1:]:
            order.append(await user_id_(e))
        if None in order:
            return
        if (n := event.sender.id) not in order:
            order = [n] + order
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
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
        await event.respond("Done. Game registered.")

# 4
@bot.on(events.NewMessage(pattern=commands('words')))  # mark:editing
async def react_game_words(event):
    """React commands and triggers at game 'words'."""
    await _react_game_words(event)
    raise events.StopPropagation


@bot.on(events.ChatAction(func=lambda event: \
                          event.user_joined or event.user_added))
async def greet_new_chat_members(event):
    """Welcome every new user"""
    # print(event)  # test
    should_greet_all = False
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
        return

    chat_id = event.chat.id

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
            await event.reply("Сюда можно онли участникам чата курса. Сóри.")
            for u in should_ban:
                await bot.edit_permissions(chat_id, u.id,
                    view_messages=False  # i. e. banning
                    )
                # ref: (1)

        should_greet = [user for user in users if user not in should_ban]
        if not should_greet:
            return

        mdash = chr(8212)  # m-dash: "—"
        is_test_msg = False
        till = (
            "28.02.2021, 06.03.2021, 07.03.2021, 12.05.2021, 13.05.2021"
            )

        mentions = [user_text_mention(user) for user in should_greet]
        mentions = ", ".join(mentions) #  [1:-1]
        msg = f"""{"[Это тест.]"*is_test_msg}
Привет, {mentions}!
Этот чат — флудилка. Ссылка на основной чат находится в \
закрепе. Бот может быть полезен аля-переводом текста на старославянский \
язык. Инструкция: см. /help@{BOT_USERNAME}.

© Anonym, 27.01.2021{mdash}{till}
"""
        await event.respond(msg, parse_mode='html')
    elif chat_id == HEAD_CHAT:
        msg = f"""\
Здравствуй, <a href="tg://user?id={user.id}">\
{user.first_name}{" " + u if (u := user.last_name) else ""}</a>!
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

# TODO: place all styled as `_add_user`, if possible, to another handler.
@bot.on(InlineQuery(func=lambda event: 0 < len(event.text) <= 255))
async def answer_query(event):
    print('user_id:', event.sender.id)  # test  #?

    try:
        answers = []
        text = event.text
        print('query:', text)  # test

        builder = event.builder

        if any(text.startswith(k) for k in NAMES_REPLACE):
            show_text = text
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
        g_title = bytes("Перевод на глаголицу", encoding='utf-8')
        g_description = g_text
        # g_text = g_text
        trg_title = bytes("Транслитерация на глаголицу", encoding='utf-8')
        trg_description = trg_text
        # trg_text = trg_text

        # results:
        r_c = builder.article(c_title, c_description,
            text=c_text, thumb=c_thumb)
        r_g = builder.article(g_title, g_description,
            text=g_text, thumb=g_thumb)
        r_trg = builder.article(trg_title, trg_description,
            text=trg_text, thumb=trg_thumb)

        answers = [r_c, r_g, r_trg] + answers

        '''
        r1 = builder.article('Be nice', text='Have a nice day')
        r2 = builder.article('Be bad', text="I don't like you")
        

        r1 = builder.article('Be nice', text_cyr, text='Have a nice day',
            thumb=...)
        cyr = types.InlineQueryResultArticle(
            id='1',
            title="Перевод на кириллицу",
            description=text_cyr,
            input_message_content=types.InputTextMessageContent(
                message_text=text_cyr),
            thumb_url=A_CYRYLLIC, thumb_width=48, thumb_height=48,
            )
        
        
        gla = types.InlineQueryResultArticle(
            id='2',
            title="Перевод на глаголицу",
            description=text_gla,
            input_message_content=types.InputTextMessageContent(
                message_text=text_gla),
            thumb_url=A_GLAGOLIC, thumb_width=48, thumb_height=48,
            )
        
        
        transliterated_gla = types.InlineQueryResultArticle(
            id='3',
            title="Транслитерация на глаголицу",
            description=text_transliterated_gla,
            input_message_content=types.InputTextMessageContent(
                message_text=text_transliterated_gla),
            thumb_url=A_LATER_GLAGOLIC, thumb_width=48, thumb_height=48,
            )
        #TODO: answers = [cyr, gla, transliterated_gla] + answers
        '''
        await event.answer(answers, cache_time=CACHE_TIME)
    except Exception as e:
        print(type(e), ': ', e, sep='')


# 7 (requires test)
# TODO: test
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

# 6
@bot.on(events.NewMessage)
async def answer_message(event):
    # Answer message, realises a game words play, actually.
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
        pattern = r'(?i)(!)?[-а-яё]+'
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
