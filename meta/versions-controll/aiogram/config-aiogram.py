# -*- coding: utf-8 -*-
# version: aiogram:1.0.6-editing

import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram import executor  # test

from uniconfig import *
from globalconfig import get


# INLINE SETTING

_THUMB_CONFIG = {
    'common': {
        'width': 48,
        'height': 48
    }
}

COMMON_THUMB_CONFIG = _THUMB_CONFIG['common']

# LOGGING & BOT SETTING

# Set logging
logging.basicConfig(level=logging.INFO)

# Initialize the bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Now the bot is connected, get some data
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# May be commented for tests:
bot_data = asyncio.run(bot.get_me())
print(bot_data)  # test
BOT_ID = bot_data.id
BOT_USERNAME = bot_data.username
# ---

BOT_ID, BOT_USERNAME = (None,)*2  # is dummy, deletable_fully

loop = asyncio.new_event_loop()
if loop.is_closed():
    ...
executor.start_polling(dp, loop=loop, skip_updates=True)
