# Simple tool to disconnect from Telegram manually
# ================================================

import os

from telethon.sync import TelegramClient

from globalconfig import ON_HEROKU as _  # also run `load_dotenv`


__all__ = ['_get', 'ON_HEROKU', 'disconnect']  # required: `disconnect`


_get = os.environ.get


session_name = 'null'
api_id = _get('API_ID')
api_hash = _get('API_HASH')


def disconnect():
    try:
        TelegramClient(session_name, api_id, api_hash).log_out()
        print('Disconnected from Telegram')
    except ConnectionError:
        print('Connection error raised: already disconnected from Telegram')


if __name__ == '__main__':
    disconnect()
