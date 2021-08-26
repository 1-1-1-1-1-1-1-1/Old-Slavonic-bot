# -*- coding: utf-8 -*-
# version: telethon:1.0.9+


# ==== Imports +load config from uniconfig ====================================

import logging

from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeImageSize

from uniconfig import *
from globalconfig import get
from _disconnector import disconnect


# === Inline settings =========================================================

_THUMB_CONFIG = {
    'common': {
        'size': 300,
        'mime_type': 'image/jpeg',
        'attributes': DocumentAttributeImageSize(48, 48)
    }
}

COMMON_THUMB_CONFIG = _THUMB_CONFIG['common']


# === Logging and bot settings ================================================

# Set logging.
logformat = '[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s'
logging.basicConfig(format=logformat,
                    level=logging.WARNING)

# Set bot configurations: session name, api_id and api_hash.
session_name = 'translator-bot' if not TEST_MODE else 'translator-bot-test'
api_id = eval(get('API_ID'))
api_hash = get('API_HASH')

# Prevent the situation when another client was already connected.
# **Caution**: Doing this action will end the previous client session.
disconnect()

# Connect to Telegram.
bot = TelegramClient(
    session_name, api_id, api_hash
).start(bot_token=TOKEN_INIT)

# Now it is connected, get some data.
bot_data = bot.get_me()
BOT_ID = bot_data.id
BOT_USERNAME = bot_data.username
