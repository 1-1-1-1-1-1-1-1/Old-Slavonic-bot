<a id="top"></a>

# Old-Slavonic-bot

<!-- only at public GitHub repository: -->
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy) 

<!-- [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/1-1-1-1-1-1-1-1/Old-Slavonic-bot) -->

# Contents
 + [About](#about)
 + [Usage](#usage)
 + [Files](#files)
 + [References](#references)

# About
<a id="about"></a>
[MIT License](LICENSE)

Переводчик на старославянский язык.

Статья в Telegraph:
https://telegra.ph/Perevodchik-na-staroslavyanskij-02-28

Начиная с версий (1.0.0+, commit 14 в GitHub), где также добавляются файлы контроля версий (meta/versions-controll), есть три версии: в библиотеках telebot, aiogram, telethon.  Файлы/данные, записанные до этого момента, приоритетно считать не столь авторитетными, как после (начиная с) него.  Временно, в версии 1.0.0, структура папок и файлов не считается соблюденной и некоторые файлы отдельно вынесены в папку контроля версий (meta/versions-controll) с удалением этих файлов в корне. Эти файлы, вообще говоря, отличаются.

# Usage
<a id="usage"></a>
![Пример перевода слова](meta/media/usage-trans.jpg)

# Files & folders
<a id="files"></a>
Some data: [data/](data/)

# References
<a id="references"></a>
General
-------
 * https://www.ponomar.net/files/gama2/p002.htm (Название: "§2. Употребление и произношение букв")
 * Про inline: https://core.telegram.org/bots/inline
 * https://core.telegram.org/bots/api
 * Про числа: http://lukianpovorotov.narod.ru/Folder_Pravoslavie/tserkovnoslavyanskiye_chisla.html
 * Про inline: https://mastergroosha.github.io/telegram-tutorial/docs/lesson_07/,
   https://mastergroosha.github.io/telegram-tutorial/docs/lesson_08/
   <з
 * Some about numbers (5): ! http://konorama.ru/servisy/slacy/
 * http://info-7.ru/Titlo/Titlo.shtml (link to this was at Wikipedia, see prev. source)
 * Git docs, partial: https://git-scm.com/book/ru/v2/Основы-Git-Создание-Git-репозитория/

Heroku
------
 * Deployment: https://devcenter.heroku.com/categories/deployment
 * Creating a 'Deploy to Heroku' Button: https://devcenter.heroku.com/articles/heroku-button

Telegram API
------------
 * About InlineKeyboardMarkup:
 > Note: This will only work in Telegram versions released after 9 April, 2016.

 (from the [Telegram Bot API])

 * Query's text: 
 > Text of the query (up to 256 characters)

 (from the [Telegram Bot API])

Another
-------
 * https://pypi.org/project/python-dotenv/
 * http://www.fabfile.org/ link to it was at prev. (dotenv.)
 
[up to top](#top)

[Telegram Bot API]: https://core.telegram.org/bots/api

---
[![UNLICENSE](noc.png)](UNLICENSE)