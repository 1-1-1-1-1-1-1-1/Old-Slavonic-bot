# globalconfig file, used at config.py and _disconnector.py
# =========================================================
# history
#   Added env. variables at 2021-02-17T21:05.

import os


get = os.environ.get


ON_HEROKU = get('ON_HEROKU', False)


if not ON_HEROKU:
    from dotenv import load_dotenv


    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    dotenv_path = os.path.join(BASEDIR, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, encoding='utf-8', interpolate=True)
