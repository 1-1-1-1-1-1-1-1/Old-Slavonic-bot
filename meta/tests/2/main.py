"""View the message's json."""


import json
from typing import NoReturn

from telebot import TeleBot
from telebot import types

from config import TOKEN


bot = TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def get_text(message: types.Message):
    global message_

    def store_data(fname, data) -> NoReturn:
        with open(fname, 'w') as f:
            f.write(data)

    message_ = message
    _data: dict = message.json
    data: str = json.dumps(_data, indent=4, ensure_ascii=False)
    print(data)  # test
    store_data('1.txt', data)


bot.polling()
