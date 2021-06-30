import asyncio
import os

import configparser
from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeImageSize

from globalconfig import get, ON_HEROKU
from _disconnector import disconnect


print("Parsing the beginning of configs' file...")


def password(uid, time=None, *, test_mode=False):
    import os, datetime  #?
    now = datetime.datetime.now()

    if time is not None:
        maxdelta = 3*60
        def number(s: str) -> int:
            zero = '0'
            return int(res) if (res := s.lstrip(zero)) else 0
        minute, second = map(number, time)
        res_date = now.replace(  # timedelta
            minute=minute, second=second)
        # not to let be static:
        if not abs((res_date - now).total_seconds()) < maxdelta and not test_mode:
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


TOKEN_TEST = get('TOKEN_TEST')
TOKEN_INIT = get('TOKEN_INIT')

if not TOKEN_TEST or not TOKEN_INIT:
    raise SystemExit("No tokens found.")

del os
PASSWORD_ENABLED = False

# Whether the production version:
PROD_UNDEPLOYED = True  # ! (for tests)
PROD = ON_HEROKU or PROD_UNDEPLOYED

if ON_HEROKU:
    TEST_MODE = False
else:
    TEST_MODE = True  #~  # ADDED THEN  #! Launching 2 bots at the same time -- ?
        # Corrected at 19.02.2021T17:33: `or` -> `and`
    # [17:42] .. it as `if-else`

if PROD:
    TEST_MODE = False

if TEST_MODE:
    TOKEN = TOKEN_TEST
else:
    TOKEN = TOKEN_INIT


from os.path import join


DATAFILE = join("data", "data.json")

CACHE_TIME = 1  # test
if PROD:
    CACHE_TIME = 120

LOGGING_ENABLED = True
LOG_FILENAME = join("locals", "autologs.txt")

ANY_LETTER = '.'

CONSONANTS = ["б", "в", "г", "д", "ж", "з", "к", "л", "м", "н", "п", "р",
              "с", "т", "ф", "х", "ц", "ч", "ш", "щ"]

# logs data
LOGGING_CHAT = -1001495851235
CHAT_LOGS_MODE_ALL = [
# 'launch',
'new user',
'bot-exception'
]

ADMINS = [
699642076
]

HELP_URL = "https://telegra.ph/Perevodchik-na-staroslavyanskij-02-28"

A_CYRYLLIC = \
"https://i.ibb.co/N9Vznhx/F67-C56-DB-732-C-468-B-BC4-B-81-FCCBEEE37-D.jpg"
A_GLAGOLIC = \
"https://i.ibb.co/DzwcQpr/16482-EB9-9-FF9-405-C-BD76-06-FFDD0613-C2.jpg"
A_LATER_GLAGOLIC = \
"https://i.ibb.co/2SS7nP7/3-FA71-E14-25-A0-4-B7-C-B8-F1-EDB9-DC8118-AF.jpg"

# A dictionary of `name: (replacement, uid)`
NAMES_REPLACE = eval(get('NAMES_REPLACE'))

NoSectionError = configparser.NoSectionError

# chats and channels
CHANNEL = -1001285323449
TEST_CHAT = -1001341084640
SPEAK_CHAT = -1001370491506
HEAD_CHAT = -1001172242526

UIDS_BASE = join("data", 'users.txt')
GAME_WORDS_DATA = join("locals", 'words.ini')

WORDS_GAME_PATTERN = r"(?is)!?\s?([-а-яё]+)(?:\s*\(.+\))?"

INLINE_EXAMPLES = [
    "Пример текста. 12 — число",
    "Тест. Слова: вот-вот, сразу, жизнь. Это бот. Число: 1",
    "Текст, выражающий действие бота в примере. 1 — число, 2 — также. Тест-тест",
    "Бот-переводчик на старославянский язык.",
    "Тестовая фраза. Если можно, иди делать дело.",  # test
    '"1 в поле не воин."',
    "7 раз отмерь, 1 раз отреж. Успехов."
    ]


session_name = 'translator-bot' if not TEST_MODE else 'translator-bot-test'
api_id = eval(get('API_ID'))
api_hash = get('API_HASH')


disconnect()  # to prevent the situation when another client was connected

# connect to Telegram:
bot = TelegramClient(session_name, api_id, api_hash).start(bot_token=TOKEN_INIT)

# now it is connected, get some data
bot_data = bot.get_me()
BOT_ID = bot_data.id
BOT_USERNAME = bot_data.username

_THUMB_CONFIG = {
    'common': {
    'size': 300,
    'mime_type': 'image/jpeg',
    'attributes': DocumentAttributeImageSize(48, 48)
    }
}

COMMON_THUMB_CONFIG = _THUMB_CONFIG['common']
