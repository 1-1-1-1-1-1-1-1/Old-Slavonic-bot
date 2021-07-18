# -*- coding: utf-8 -*-
# version: -:1.0.6-editing

# This is a file to import it from config and load config, *uni*versal
# for all bot version, i.e. libraries, with a help of which the bot is written.


from os.path import join
import warnings

import configparser

from globalconfig import get, ON_HEROKU


print("Parsing the beginning of configs' file...")
# Log that this action as processing


def password(uid, time=None, *, test_mode=False):
    """Generate a password. Dependes on time. Optionally, can choose time."""
    import datetime  # *Only* locally used
    now = datetime.datetime.now()

    if time is not None:
        max_delta = 3*60

        def number(s: str) -> int:
            # '0..0number' -> number: int
            zero = '0'
            return int(_res) if (_res := s.lstrip(zero)) else 0
        minute, second = map(number, time)
        res_date = now.replace(  # timedelta
            minute=minute, second=second)
        # Not to let the password being static:
        if not abs(
            (res_date - now).total_seconds()
        ) < max_delta and not test_mode:
            return
        now = res_date

    secret_code = get('SECRET_CODE')
    if not secret_code:
        return

    time_format = eval(get("SECRET_TIME_FORMAT"))
    H, M, S, d, m, Y = map(
        int,
        now.strftime(time_format).split()
    )
    res = eval(secret_code).split(',')
    space = {
        'H': H,
        'M': M,
        'S': S,
        'd': d,
        'm': m,
        'Y': Y,
        'uid': int(uid)
    }

    res = map(lambda i: eval(i, globals(), space), res)
    res = list(res)
    res = [str(int(item)) for item in res]
    s = eval(get('SECRET_S'))
    res = ("".join(res)[::s]*2)[:7]

    if __name__ == '__main__':
        print(res)  # test
    else:
        return res


# TOKENS, PRODUCTION MODE, TEST MODE, ON HEROKU and similar
# -- TOKEN, PRODUCTION, TEST_MODE etc. -- set and determine ---
TOKEN_TEST = get('TOKEN_TEST')
TOKEN_INIT = get('TOKEN_INIT')

if not TOKEN_TEST or not TOKEN_INIT:
    raise SystemExit("No tokens found.")

# Here PROD = "whether the production version":
_IS_UNSAFE_TESTS_MODE = True  # ! (Unsafe:for tests)
PROD_UNDEPLOYED = _IS_UNSAFE_TESTS_MODE
PROD = ON_HEROKU or PROD_UNDEPLOYED

if _IS_UNSAFE_TESTS_MODE and not ON_HEROKU:
    msg = "Running unsafe tests, "\
    "i. e. with `PROD_UNDEPLOYED=True`, is unsafe."
    warnings.warn(msg)

if ON_HEROKU:
    # *NOTE:* Launching 2 bots at the same time may be bad. (1)
    TEST_MODE = False
elif PROD:
    # (1)... Also, if it is as a production version, let is to be not a test.
    TEST_MODE = False
else:
    TEST_MODE = True

if TEST_MODE:
    TOKEN = TOKEN_TEST
else:
    TOKEN = TOKEN_INIT


if _IS_UNSAFE_TESTS_MODE:
    # (1)... however, if user (=developer and code writer) wants to
    # let them run, well, welcome.
    # Assuming the TOKEN is already set (previous part is important, here
    # can happen such a case: TEST_MODE is True, but TOKEN == TOKEN_INIT).
    # Pay attention for it!
    TEST_MODE = True


# TRANSLITERATING and TRANSLATING
# Part: translating / transliterating phrases, text ------------

DATAFILE = join("data", "data.json")

CONSONANTS = ["б", "в", "г", "д", "ж", "з", "к", "л", "м", "н", "п", "р",
              "с", "т", "ф", "х", "ц", "ч", "ш", "щ"]


# GAME 'words': data
# -- Data for playing the game 'words' -------

ANY_LETTER = '.'

GAME_WORDS_DATA = join("locals", 'words.ini')

WORDS_GAME_PATTERN = r"(?is)!?\s?([-а-яё]+)(?:\s*\(.+\))?"

# INLINE TRANSLITERATING: setting
# -- Inline examples, translating and transliterating query settings etc.

INLINE_EXAMPLES = [
    "Пример текста. 12 — число",
    "Тест. Слова: вот-вот, сразу, жизнь. Это бот. Число: 1",
    "Текст, выражающий действие бота в примере. 1 — число, 2 — также. Тест-тест",
    "Бот-переводчик на старославянский язык.",
    "Тестовая фраза. Если можно, иди делать дело.",  # test
    '"1 в поле не воин."',
    "7 раз отмерь, 1 раз отреж. Успехов."
]

A_CYRYLLIC = \
    "https://i.ibb.co/N9Vznhx/F67-C56-DB-732-C-468-B-BC4-B-81-FCCBEEE37-D.jpg"
A_GLAGOLIC = \
    "https://i.ibb.co/DzwcQpr/16482-EB9-9-FF9-405-C-BD76-06-FFDD0613-C2.jpg"
A_LATER_GLAGOLIC = \
    "https://i.ibb.co/2SS7nP7/3-FA71-E14-25-A0-4-B7-C-B8-F1-EDB9-DC8118-AF.jpg"

# A dictionary of `name: (replacement, uid)`
NAMES_REPLACE = eval(get('NAMES_REPLACE'))

# BOT & INTERNAL CONFIG -----------
# -- Some bot internal data -------

# Cache time for the inline query result:
CACHE_TIME = 1  # test
if PROD:
    CACHE_TIME = 120

UIDS_BASE = join("data", 'users.txt')

# Logging (dev. question: what?)
LOGGING_ENABLED = True
LOG_FILENAME = join("locals", "autologs.txt")

# Logs via bot to the Telegram chat: data
LOGGING_CHAT = -1001495851235
CHAT_LOGS_MODE_ALL = {
    # 'launch',
    'new user',
    'bot-exception'
}

ADMINS = [
    699642076
]

# Chats and channels
CHANNEL = -1001285323449  # The course channel
TEST_CHAT = -1001341084640  # The test chat
SPEAK_CHAT = -1001370491506  # The chat: place of speaking at group 
HEAD_CHAT = -1001172242526  # The initial, main chat of a group/course
# *Note:* Actually, the bot was written for a thing, connected with an exact
# course of that language (Old Slavonic), so the word 'course' appears here.

HELP_URL = "https://telegra.ph/Perevodchik-na-staroslavyanskij-02-28"

# OTHER CONFIG, SETTINGS, CONSTANTS
# -- Other ------------------------

PASSWORD_ENABLED = False

NoSectionError = configparser.NoSectionError

LOCAL_LOGS = join("locals", "do_logs.log")
# Upper is local, see the code of trigger to command '/do' at main (worker)
FILE_GREETING = join('data', "greeting.json")

DEFAULT_GREETING_EVAL_SOURCE = """{
    'user': user,
    'mention': user_text_mention,
    'mentions': mentions,
    'bt_uname': BOT_USERNAME,
    'scright': short_cright,
    'fcright': full_cright
}"""

DEFAULT_GREETING = '''f"""Hello, {mentions}!

🔸Bot is usible for like-a-translation to Old Slavonic, see \
/help@{BOT_USERNAME}.
"""'''