import telebot
from telebot import types
import random
import re
from os.path import join

import requests
import configparser

from config import TOKEN, CACHE_TIME, NAMES_REPLACE
from config import ADMINS, LOGGING_CHAT
from functions import translation, glagolic_transliterate


CHANNEL = -1001285323449
TEST_CHAT = -1001341084640
SPEAK_CHAT = -1001370491506
HEAD_CHAT = -1001172242526

WORDS_GAME_PATTERN = r"(?is)!?\s?([-а-яё]+)(?:\s*\(.+\))?"


INLINE_EXAMPLES = [
    "Пример текста. 12 — число",
    "Тест. Вот-вот. Знаки иногда не писал... Число: 1",
    "Текст, выражающий в примере. 1 — число, 2 — также. Тест-тест"
    ]


from config import PROD, PASSWORD_ENABLED


bot = telebot.TeleBot(TOKEN)


from config import ON_HEROKU, CHAT_LOGS_MODE_ALL

def bot_inform(msg, chat_id=LOGGING_CHAT, type_=None, **kwargs):
    if type_ is not None and type_ not in CHAT_LOGS_MODE_ALL:
        return
    bot.send_message(LOGGING_CHAT, msg, **kwargs)


bot_inform(f"""
Launched the bot.
Is <u>{"" if PROD else 'not '}the production</u> version.
Is on Heroku: <u>{str(ON_HEROKU).lower()}</u>.
""", type_="launch", parse_mode='HTML')

del ON_HEROKU


BOT_USERNAME = bot.get_me().username


NoSectionError = configparser.NoSectionError


def _cmd_pattern(cmd, *, flags='i'):  # Internal
    """See code to view the example of it."""
    if flags:
        _flags_add = r'(?' + flags + r')'
    else:
        _flags_add = ""
    cmd_pattern = _flags_add + r'/' + cmd + r'(?:@' + BOT_USERNAME + r')?'
    return cmd_pattern


def feature_exists(fid):  # Internal
    d = {
    'teach_word': False
    }
    if fid in d:
        return d[fid]
    return False


def _chatMember(user_id, of):
    # Is it needed NOT for users, new in the chat?

    try:
        return bot.get_chat_member(of, user_id)
    except:
        return types.ChatMember(*([None]*4 + [False]*12))

def is_participant(user_id, of=HEAD_CHAT):
    """User is participant of `of` (chat), returns bool."""
    return _chatMember(user_id, of).status in [
            "creator",
            "administrator",
            "member",
            "restricted"
        ]

def _add_user(user_id):
    # Internal, add ID to the base. Comments are allowed.
    filename = join('data', 'users.txt')
    with open(filename, 'a') as f:
        pass
    with open(filename, 'r', encoding='utf8') as f:
        data = f.read()
    data_ = ""
    if data and data.rstrip('\n') == data:
        data_ += '\n'
    if (s := str(user_id)) not in data:
        bot_inform('New user: \
            <a href="tg://user?id={0}>{1}</a>\nuser_id: {0}'.format(
                user_id, "User"), type_='new user', parse_mode='HTML')
        data_ += s + '\n'
    with open(filename, 'a', encoding='utf8') as f:
        f.write(data_)

def full_name(user):
    return f'{user.first_name}{" " + u if (u := user.last_name) else ""}'

def user_text_mention(user, fill_as=None):
    # `fill_as` — a text to insert at mention.
    if fill_as is None:
        filling = full_name(user)
    else:
        filling = fill_as
    return f'<a href="tg://user?id={user.id}">{filling}</a>'

def load_users():
    # Allowed comments.
    with open(join('data', 'users.txt'), encoding='utf-8') as f:
        users = map(eval, f.read().strip().split('\n'))
    return users

def make_move(chat_id, message, letter, mentioned):
    bot.send_chat_action(chat_id, 'typing')
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
        maxn = 4  # Should it be so?
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
            bot.send_message(chat_id, msg,   # continuing game — ?
                reply_to_message_id=message.message_id)
            return
        msg = res_word + ' (' + meaning + ')'

        return res_word, msg  # test st.

def play_words(chat_id, message, current=0):
    # """Да, тут считают, что е и ё — одна буква."""

    c = configparser.ConfigParser()
    chat_id = str(chat_id)
    filename = "words.ini"
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Ошибка: не найдено игру."
        bot.send_message(chat_id, msg,
            reply_to_message_id=message.message_id)
        raise NoSectionError
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    cur_letter = section["letter"]
    mentioned = eval(section["mentioned"])
    
    dot = '.' * (random.choice([0, 1, 2]) < 1)
    if (n := message.from_user.id) in order and \
        (match := re.fullmatch(WORDS_GAME_PATTERN, message.text)):
        if message.chat.type != 'private' and not (
            re.fullmatch(r"(?s)!\s?([-\w]+)(?:\s*\(.+\))?", message.text) or
            (message.reply_to_message and
            message.reply_to_message.from_user.id == order[current - 1])):
            return
        if n != order[current]:
            answer_msg = f"Не твой сейчас ход{dot}"  # " Ход игрока "
            # user_text_mention(user)!
            bot.send_message(chat_id, answer_msg, 
                reply_to_message_id=message.message_id)
            return  #~
        word = match.group(1)
        print(word)  # test
        if cur_letter != "." and word[0].lower().replace('ё', 'е') != cur_letter:
            answer_msg = f"На букву {cur_letter!r}{dot}"
            bot.send_message(chat_id, answer_msg, 
                reply_to_message_id=message.message_id)
            return  #~
        if requests.get(f"https://loopy.ru/?word={word}&def=").status_code \
            == 404:
            answer_msg = f"Вау. Кажется, я не знаю этого слова. Хотя, \
возможно, оно лежит где-то на полке в папке data, но я не смотрел." \
 + f" Переходи, пожалуйста{dot}" + " Что \
это слово значит? (Ход не засчитан. Потом либо напиши ответом на это \
сообщение толкование слова, я его в словарь запишу, либо назови другое \
слово. И вообще, это not implemented ещё{dot})"*feature_exists('teach_word')
            bot.send_message(chat_id, answer_msg, 
                reply_to_message_id=message.message_id)
            return  #~
        if word.casefold() in map(lambda s: s.casefold(), mentioned):
            answer_msg = f"Слово {word!r} уже было в этой игре{dot}"
            bot.send_message(chat_id, answer_msg, 
                reply_to_message_id=message.message_id)
            return  #~
        mentioned.append(word)
        res = word.lower().rstrip('ь')
        assert re.fullmatch("(?i)[-а-яё]+", res)  #~
        letter = res[-1]
        section["letter"] = letter
        current = (current + 1) % len(order)
        if str(order[current]) == TOKEN[:TOKEN.index(':')]:
            print("Bot's move at game `words`")  # test-log
            
            try:
                answer, msg = make_move(chat_id, message, letter, mentioned)
            except Exception as e:
                print(e)
                return

            current = (current + 1) % len(order)
            
            mentioned.append(answer)
            
            next_let = answer.lower().rstrip('ьъ')[-1]
            if next_let == 'ё': next_let = 'е'
            section["letter"] = next_let

            bot.send_message(chat_id, msg, reply_to_message_id=message.message_id)

        section["current"] = str(current)
        section["mentioned"] = str(mentioned)

        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

@bot.message_handler(commands=['test_start'])
def test_start_message(message):
    if message.from_user.id not in ADMINS:
        return

    msg = "some msg.\n\n\
Тут можно попробовать ввод в режиме inline (перевод):"
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
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    pass

# examples for it:
# /do -password=pw -action=eval code
# /do -password=pw -time=mm:ss -action=eval code
@bot.message_handler(commands=['do'])
def do_action(message):
    if message.from_user.id not in ADMINS:
        return

    filename = join("data", "do_logs.log")
    mid = "{},{}".format(message.chat.id, message.message_id)
    try:  # to let the polls tracker go further
        with open(filename, 'rt', encoding='utf-8') as f:
            _data = f.read().split('\n')
        if mid in _data:
            return
    finally:
        os = __import__("os")
        if not 'data' in os.listdir():
            os.mkdir("data")
        del os
        with open(filename, 'at', encoding='utf-8') as f:
            f.write(mid)
            f.write('\n')
    
    pattern = (_cmd_pattern('do', flags='is')
        + r"(?: {1,2}-password=(" + r'\S+' + r"))?"
        + r"(?:\s+-time=(\d{,2}:\d{,2}))?"
        + r"(?:\s+-action=(exec|eval))?"
        + r"\s+(.+)")
    string = message.text
    if not (match := re.fullmatch(pattern, string)):
        print(pattern, string)
        return
    pw, time, *other = match.groups()
    uid = message.from_user.id
    if PASSWORD_ENABLED:
        from config import password as _password
        if time is not None:
            time = time.split(':')
        password = _password(uid, time=time)
        print('pw:', password)
        if pw != password:
            return
    action, code = other
    if action is None:
        action = 'eval'
    action0 = action
    action = eval(action)
    if action is eval:
        res = eval(code)
        bot.send_message(message.chat.id, str(res),
            reply_to_message_id=message.message_id)
    elif action is exec:
        exec(code)

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    _add_user(user_id)

    test = False

    chat_id = message.chat.id

    header = "\[test]"*test
    # ~0:01 at 2021-08-02: once said "can't parse ent.",
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
    if allow_to_all or is_participant(user_id):
        def invite_link(chat_id_):
            # No `export_chat_invite_link`!
            try:
                link = bot.get_chat(chat_id_).invite_link
            except:
                link = "not found"
            return link

        channel = invite_link(CHANNEL)
        chat = invite_link(HEAD_CHAT)

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
    switch_cur_chat_button = types.InlineKeyboardButton(
        text="Да", switch_inline_query_current_chat=example)
    keyboard = types.InlineKeyboardMarkup(
        [[switch_cur_chat_button]]
        )
    bot.send_message(chat_id, msg, parse_mode='Markdown',
                     reply_markup=keyboard,
                     disable_web_page_preview=True)


@bot.message_handler(commands=["help"])
def send_help_msg(message):
    _add_user(message.from_user.id)

    msg = """\
Переводчик на старославянский язык. Правило перевода: ввести в чате\
 слово "@""" + BOT_USERNAME.replace('_', r'\_') + """\
\" и, после пробела, — текст для перевода.
Для отправки текста из списка нажать на тот текст.
`*` Возможные ошибки: недописывание символов.

Ещё: игра в слова (см. /words help). Значение слова: \
см. /meaning help.
"""
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')


def words_skip_move(message):
    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
    filename = "words.ini"
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        msg = "Игра не найдена"
        bot.send_message(chat_id, msg,
            reply_to_message_id=message.message_id)
        return
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    current += 1
    current %= len(order)
    section["current"] = str(current)

    if str(order[current]) == TOKEN[:TOKEN.index(':')]:
        mentioned = eval(section["mentioned"])
        cur_letter = section["letter"]
        letter = cur_letter

        print("Bot's move")  # test

        answer, msg = make_move(chat_id, message, letter, mentioned)

        current = (current + 1) % len(order)

        section["current"] = str(current)
        next_let = answer.lower().rstrip('ьъ')[-1]
        mentioned.append(answer)
        if next_let == 'ё': next_let = 'е'
        section["letter"] = next_let
        section["mentioned"] = str(mentioned)

        bot.send_message(chat_id, msg, reply_to_message_id=message.message_id)
    else:
        msg = "Ход пропущен."
        bot.send_message(chat_id, msg, reply_to_message_id=message.message_id)
    with open(filename, 'w', encoding='utf-8') as f:
        c.write(f)

    print('Performed skip of move.')  # test

@bot.message_handler(commands=['meaning'])
def send_meaning(message):
    """Priority to search for a word:
    dict. 1 -> dict. '3' -> in the exact place at the I-net.
    """
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    try:
        cmd_pattern = _cmd_pattern('meaning')
        text = message.text
        word = re.fullmatch(cmd_pattern + '\s*([-а-яё]+)', text).group(1)
    except:
        try:
            text = message.reply_to_message.text
            word = re.fullmatch(WORDS_GAME_PATTERN, text).group(1)
        except:
            msg = """Не распознано слово. Напиши либо в ответ на сообщение, \
где искомое слово, либо `/meaning слово`."""
            bot.send_message(chat_id, msg,
                             reply_to_message_id=message.message_id,
                             parse_mode='Markdown')
            return

    from functions import d as d0
    order = [1, '3']
    def by_rule(kid):
        if kid == 1:
            for a, q in d.items():
                a = a.replace(')', '')
                a = a.replace('(', ',')
                a = a.lower().split(',')
                a = map(lambda ph: ph.strip(), a)

                if word.lower() in a:
                    bot.send_message(chat_id, q,
                        reply_to_message_id=message.message_id)
                    return 0
        elif kid == '3':
            for k in d:
                if k.lower() == word.lower():
                    meaning = d[k]
                    bot.send_message(chat_id, meaning,
                        reply_to_message_id=message.message_id)
                    return 0
    for k in order:
        try:
            d = d0[k]
            if by_rule(k) != 0:
                continue
            return
        except:
            continue
        del d
    del d0, order, by_rule

    url = f"https://loopy.ru/?word={word}&def="
    
    if (sc := (r := requests.get(url)).status_code) == 404:
        msg = f"Слово {word!r} не найдено в словаре."
        bot.send_message(chat_id, msg)
    elif sc != 200:
        msg = f"Непонятная ошибка. Код ошибки: {sc}."
        bot.send_message(chat_id, msg)
    else:
        rtext = r.text
        rtext_part = rtext[rtext.find('Значения'):]
        rtext_part = rtext_part[:rtext_part.index('</div>')]
        finds = re.findall(r'<p>(.*?)</p>', rtext_part)[1:]
            # 1-st item — a header or what?
        assert finds
        res = random.choice(finds)

        bot.send_message(chat_id, res,
                         reply_to_message_id=message.message_id)
        
@bot.message_handler(commands=['words'])
def reg_game_words(message):
    chat = message.chat
    # Processing further actions may take a great amount of time.
    bot.send_chat_action(chat.id, 'typing')
    _add_user(message.from_user.id)

    cmd_pattern = _cmd_pattern('words')
    help_pattern = cmd_pattern \
        + r'\s(?:[-—\s:]*)(?:правила|инструкция|команды|help)\s*\??'

    if re.fullmatch(cmd_pattern + r'.*?\s+[-!]?skip', message.text):
        words_skip_move(message)
        return
    if re.fullmatch(cmd_pattern + r'\s+(?:приостановить|pause)', message.text):
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = "words.ini"
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
           msg = "Игра не найдена."
           bot.send_message(chat_id, msg,
               reply_to_message_id=message.message_id)
           return
        c[chat_id]['status'] = 'paused'
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Игра приостановлена. Продолжение: /words continue{dot}"
        bot.send_message(chat_id, msg,
            reply_to_message_id=message.message_id)

        return
    if re.fullmatch(cmd_pattern + r'\s+(?:хватит|удалить игру|stop)', message.text):
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = "words.ini"
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
           c.remove_section(chat_id)
        else:
            msg = "Игра не найдена."
            bot.send_message(chat_id, msg,
                reply_to_message_id=message.message_id)
            return
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        dot = '.' * (random.random() > 1/2)
        msg = f"Текущая игра убрана{dot}"
        bot.send_message(chat_id, msg,
            reply_to_message_id=message.message_id)
        return
    if re.fullmatch(cmd_pattern + r'\s+(?:очередь|порядок|order)', message.text):
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = "words.ini"
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            bot.send_message(chat.id,
                "Игра в этом чате не найдена."
                )
            return
        section = c[chat_id]
        order = eval(section["order"])
        current = int(section["current"])
        uid = order[current]
        cuser = bot.get_chat_member(chat_id, uid).user
        order_ = ', '.join(map(full_name,
            (bot.get_chat_member(chat_id, _uid).user for _uid in order)))
        text_mention = user_text_mention(cuser, fill_as=None)
        msg = f"""Последовательность: {order_}
Сейчас ходит: {text_mention}"""
        bot.send_message(chat_id, msg, parse_mode='HTML')
        return
    if re.fullmatch(help_pattern, message.text):
        bot.send_chat_action(chat.id, 'typing')
        msg = """\
Начало игры
`-----------`
В личной переписке: /words `[начать|start]` `[single]` (single — игра самому)
В группе: /words пользователь\_1 ...
    Имена пользователей — упоминанием
    Своё имя можно не указывать, тогда оно первое в очереди

Хода
`----`
В личной переписке: `!слово` либо `слово`
В группе: либо `!слово`, либо `слово` в ответ на сообщение того, кто ходил прошлым.

Другие:
`-------`
`/words приостановить|pause` — остановка игры
`/words хватит|удалить игру|stop` — прекратить игру и удалить
`/words skip` — пропуск хода
`/words очередь|порядок|order` — порядок ходов, текущий игрок
`/words правила|инструкция|команды|help` — это сообщение
`/words продолжить|continue` — продолжение (после `pause`)
"""
        bot.send_message(chat.id, msg, parse_mode='Markdown')
        return

    if re.fullmatch(cmd_pattern + r'\s+(?:продолжить|continue)', message.text):
        bot.send_chat_action(chat.id, 'typing')

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = "words.ini"
        c.read(filename, encoding='utf-8')
        if (c.has_option(chat_id, 'status') and 
            c[chat_id]['status'] == 'paused'):
            c.set(chat_id, 'status', 'active')
            with open(filename, 'w', encoding='utf-8') as f:
                c.write(f)
            dot = '.' * (random.random() > 1/2)
            msg = f"Игра продолжена{dot}"
            bot.send_message(chat_id, msg,
                reply_to_message_id=message.message_id)

            return

    if chat.type == 'private':
        if 'single' in message.text:
            order = [message.from_user.id]
        else:
            order = [message.from_user.id, eval(TOKEN[:TOKEN.index(':')])]
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = "words.ini"
        c.read(filename, encoding='utf-8')
        if c.has_section(chat_id):
            if not re.search('(?:начать|start)', message.text):
                msg = "Игра уже есть. Новая игра: /words начать|start. " \
                      "Также см.: /words help."
                bot.send_message(chat_id, msg,
                    reply_to_message_id=message.message_id)
                return  # Do the game being not registered then.
        if not c.has_section(chat_id):
            c.add_section(chat_id)
        section = c[chat_id]
        section["order"] = str(order)
        section["current"] = str(current)
        section["letter"] = '.'  # Any
        section["mentioned"] = str(mentioned)
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)

        print("Done.")
        bot.send_message(chat_id, "Done. Registered.")
    elif 'group' in chat.type:
        def user_id_(e):
            if e.type == 'text_mention':
                return e.user.id
            elif e.type == 'mention':
                users = load_users()
                for user_id in users:
                    # +1: Skips `@`
                    uname = message.text[e.offset + 1: e.offset + e.length]
                    if _chatMember(user_id, of=chat.id).user.username \
                        == uname:
                        return user_id
                msg = f"Unknown user: @{uname}"
                bot.send_message(chat.id, msg,
                    reply_to_message_id=message.message_id)

        order = [user_id_(e) for e in message.entities[1:]]
        if (n := message.from_user.id) not in order:
            order = [n] + order
        if None in order:
            return
        current = 0
        mentioned = []

        c = configparser.ConfigParser()
        chat_id = str(chat.id)
        filename = "words.ini"
        c.read(filename, encoding='utf-8')
        if not c.has_section(chat_id):
            c.add_section(chat_id)
        section = c[chat_id]
        section["order"] = str(order)
        section["current"] = str(current)
        section["letter"] = '.'  # Any
        section["mentioned"] = str(mentioned)
        with open(filename, 'w', encoding='utf-8') as f:
            c.write(f)
        
        print("Done. chat_id: " + chat_id)
        bot.send_message(chat_id, "Done. Registered.")


#  ---


@bot.message_handler(content_types=['new_chat_members'])
def greet_new_chat_member(message):
    user = message.new_chat_members[0]
    chat = message.chat

    _add_user(message.from_user.id)
    _add_user(user.id)

    if chat.id == SPEAK_CHAT \
    and TOKEN == __import__("config").TOKEN_INIT:  #!
        if not is_participant(user.id):
            until_date = 0
            bot.send_message(chat.id, "Сюда можно онли участникам чата курса. Сóри.",
                reply_to_message_id=message.message_id)
            bot.kick_chat_member(chat.id, user.id, until_date=until_date)
            return

        dash = "—"  # m-dash  # <- ?
        is_test_msg = False
        day = __import__("datetime").datetime.now()
        till = (
            "26.02.2021"
            # day.strftime("%d.%m.%Y")
            )

        msg = f"""{"[Это тест.]"*is_test_msg}
Привет, {user_text_mention(user)}!
Этот чат — флудилка, не основной чат. Ссылка на основной чат находится в \
закрепе. Бот может быть полезен попыткой перевода текста на старославянский \
язык. Инструкция: см. /help@{BOT_USERNAME}.

© Anonym, 27.01.2021{dash}{till}
"""
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    elif chat.id == HEAD_CHAT:
        msg = f"""\
Здравствуй, <a href="tg://user?id={user.id}">\
{user.first_name}{" " + u if (u := user.last_name) else ""}</a>!
Это основной чат курса, ссылка на флудилку есть в закрепе.
Бот может быть полезен попыткой перевода текста на старославянский \
язык, транслитерацией в старославянские алфавиты. Инструкция: \
см. /help@{BOT_USERNAME}.
"""
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    elif message.chat.id == TEST_CHAT:
        msg = f"""\
{user_text_mention(user)}
Этот чат — тестовый чат. 
/start
/help@{BOT_USERNAME}.
"""
        bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.inline_handler(func=lambda query: 0 < len(query.query) <= 256)  # Or 255?
def answer_query(query):
    print('user_id:', query.from_user.id)  # test
    
    try:
        answers = []
        text = query.query
        print('query:', text)  # test

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

            a_1 = types.InlineQueryResultArticle(
                id='0',
                title="Смена слов",
                description=show_text,
                input_message_content=types.InputTextMessageContent(
                    parse_mode='HTML',
                    message_text=text)
                )
            answers.append(a_1)

        text = query.query

        # Parse mode here — ?
        # And sending the text in HTML/Markdown.
        
        text_cyr = translation(text, dest="cyryllic")
        cyr = types.InlineQueryResultArticle(
            id='1',
            title="Перевод на кириллицу",
            description=text_cyr,
            input_message_content=types.InputTextMessageContent(
                message_text=text_cyr)
            )
        
        text_gla = translation(text, dest="glagolic")
        gla = types.InlineQueryResultArticle(
            id='2',
            title="Перевод на глаголицу",
            description=text_gla,
            input_message_content=types.InputTextMessageContent(
                message_text=text_gla)
            )
        
        text_transliterated_gla = glagolic_transliterate(text)
        transliterated_gla = types.InlineQueryResultArticle(
            id='3',
            title="Транслитерация на глаголицу",
            description=text_transliterated_gla,
            input_message_content=types.InputTextMessageContent(
                message_text=text_transliterated_gla)
            )
        answers = [cyr, gla, transliterated_gla] + answers
        bot.answer_inline_query(query.id, answers, cache_time=CACHE_TIME)
    except Exception as e:
        print(type(e), ': ', e, sep='')

@bot.inline_handler(func=lambda query: not query.query)
def answer_empty_query(query):
    _add_user(query.from_user.id)

    try:
        r = types.InlineQueryResultArticle(
            id='1',
            title="Перевод на славянские языки: кириллица, глаголица.",
            input_message_content=types.InputTextMessageContent(
                message_text="..."),
            description="Введи текст для перевода, жми на нужный для отправки"
            )
        bot.answer_inline_query(query.id, [r], cache_time=CACHE_TIME)
    except Exception as e:
        print(e)


@bot.message_handler(content_types=['text'])
def answer_message(message):
    _add_user(message.from_user.id)

    c = configparser.ConfigParser()
    chat_id = str(message.chat.id)
    filename = "words.ini"
    c.read(filename, encoding='utf-8')
    if not c.has_section(chat_id):
        # Answering can be performed only if that section exists.
        return
    section = c[chat_id]
    order = eval(section["order"])
    current = int(section["current"])
    if (c.has_option(chat_id, 'status') and
        c.get(chat_id, 'status') == 'paused'):
        return

    if message.chat.type == 'private':
        pattern = '(?i)(!)?[-а-яё]+'
        if (s := re.fullmatch(pattern, message.text)):
            play_words(chat_id, message)
    else:
        pattern = WORDS_GAME_PATTERN
        if re.fullmatch(pattern, message.text):
            play_words(chat_id, message)

bot.infinity_polling()
