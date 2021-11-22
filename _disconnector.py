# Simple tool to disconnect from Telegram manually
# ================================================
# *Note*: telebot and aiogram usage do not require this file

import os
from typing import NoReturn

from telethon.sync import TelegramClient

import globalconfig  # Run `load_dotenv`
del globalconfig


_get = os.environ.get

default_session_name = 'null'
api_id = _get('API_ID')
api_hash = _get('API_HASH')


def disconnect(api_id=api_id, api_hash=api_hash, client=None,
               session_name=default_session_name) -> NoReturn:
    """Ensure previous client session is closed."""
    print("Trying to end the previous client session...")
    try:
        if client is None:
            client = TelegramClient(session_name, api_id, api_hash)
        client.log_out()
        print('Ended previous client session')
    except ConnectionError:
        print('Connection error raised: already disconnected from Telegram')
    except:
        raise
    print("Disconnected from Telegram")


if __name__ == '__main__':
    disconnect()
