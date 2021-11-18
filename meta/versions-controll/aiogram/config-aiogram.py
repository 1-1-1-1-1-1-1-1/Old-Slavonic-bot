# -*- coding: utf-8 -*-
# version: aiogram:1.0.9+


# ==== Imports +load config from uniconfig ====================================

import asyncio
import logging

from aiogram import Bot, Dispatcher, types

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

# Initialise the bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Now the bot is connected, get some data
bot_data = asyncio.get_event_loop().run_until_complete(
    bot.get_me()
)
BOT_ID: int = bot_data.id
BOT_USERNAME: str = bot_data.username
