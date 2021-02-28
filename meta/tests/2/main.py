import json

from telebot import TeleBot

from config import TOKEN


bot = TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def get_text(message):
    global message_
    def store_data(fname, data):
        with open(fname, 'w') as f:
            f.write(data)
    message_ = message
    _data = message.json
    data = json.dumps(_data, indent=4, ensure_ascii=False)
    print(data)
    store_data('1.txt', data)

bot.polling()
