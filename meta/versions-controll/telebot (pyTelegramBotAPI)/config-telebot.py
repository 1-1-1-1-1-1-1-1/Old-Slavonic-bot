# -*- coding: utf-8 -*-
# version: telebot:1.0.9+


# ==== Imports +load config from uniconfig ====================================

import logging

import telebot

from uniconfig import *
from globalconfig import get


# === Inline settings =========================================================

_THUMB_CONFIG = {
    'common': {
        'width': 48,
        'height': 48
    }
}

COMMON_THUMB_CONFIG = _THUMB_CONFIG['common']


# Logging & bot settings ======================================================

# Set logging
logging.basicConfig(level=logging.INFO)

# Initialise the bot
bot = telebot.TeleBot(TOKEN)

# Now the bot is connected, get some data
BOT_ID: int = int(TOKEN[:TOKEN.index(':')])
BOT_USERNAME: str = bot.get_me().username
