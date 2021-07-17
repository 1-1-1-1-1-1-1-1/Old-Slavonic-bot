# -*- coding: utf-8 -*-
# version: telethon:1.0.6-editing

from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeImageSize

from uniconfig import *
from globalconfig import get
from _disconnector import disconnect


# INLINE SETTING

_THUMB_CONFIG = {
    'common': {
        'size': 300,
        'mime_type': 'image/jpeg',
        'attributes': DocumentAttributeImageSize(48, 48)
    }
}

COMMON_THUMB_CONFIG = _THUMB_CONFIG['common']

# LOGGING & BOT SETTING

session_name = 'translator-bot' if not TEST_MODE else 'translator-bot-test'
api_id = eval(get('API_ID'))
api_hash = get('API_HASH')

disconnect()  # prevent the situation when another client was connected

# Connect to Telegram:
bot = TelegramClient(
    session_name, api_id, api_hash
).start(bot_token=TOKEN_INIT)

# Now it is connected, get some data
bot_data = bot.get_me()
BOT_ID = bot_data.id
BOT_USERNAME = bot_data.username
