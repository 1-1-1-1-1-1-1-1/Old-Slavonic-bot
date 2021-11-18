# Old-Slavonic-bot
<a id="top"></a>

Бот-переводчик на старославянский язык. Ссылка на бота: [@TransToOldSlavonic_bot](https://t.me/TransToOldSlavonic_bot).

[![Supported Bot API versions](https://img.shields.io/badge/Bot%20API-5.3-blue?logo=telegram)](https://core.telegram.org/bots/api-changelog)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/TransToOldSlavonic_bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Only at public GitHub repository: can use Deploy to Heroku button with no explicit parameter. See: https://devcenter.heroku.com/articles/heroku-button -->

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/1-1-1-1-1-1-1-1/Old-Slavonic-bot/tree/master)

## Содержание

 * [Описание](#about)
 * [Применение](#usage)
     - [Перевод и странслитерация](#usage-trans)
     - [Значение слова](#usage-meaning)
 * [Файлы и папки](#files)
 * [References](#references)
     - [Функции перевода и транслитерации, их работа](#func-refs)
     - [Работа бота](#bot-refs)
     - [Heroku](#heroku-refs)
     - [Bot API](#bot-api-refs)
         + [Telethon API](#telethon-api-refs)
         + [Telegram Bot API](#telegram-bot-api-refs)
     - [Другое](#other-refs)
     - [Некоторая общая документация](#some-general-doc-refs)
 * [See also](#see-also)

## Описание
<a id="about"></a>

Бот [@TransToOldSlavonic_bot](https://t.me/TransToOldSlavonic_bot) в Telegram.

Переводчик на [cтарославянский язык](https://ru.wikipedia.org/wiki/%D0%A1%D1%82%D0%B0%D1%80%D0%BE%D1%81%D0%BB%D0%B0%D0%B2%D1%8F%D0%BD%D1%81%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA). Доступные функции: перевод, транслитерация на алфавиты письма [старославянской кириллицы](https://ru.wikipedia.org/wiki/%D0%A1%D1%82%D0%B0%D1%80%D0%BE%D1%81%D0%BB%D0%B0%D0%B2%D1%8F%D0%BD%D1%81%D0%BA%D0%B0%D1%8F_%D0%BA%D0%B8%D1%80%D0%B8%D0%BB%D0%BB%D0%B8%D1%86%D0%B0) и [глаголицы](https://ru.wikipedia.org/wiki/%D0%93%D0%BB%D0%B0%D0%B3%D0%BE%D0%BB%D0%B8%D1%86%D0%B0). Подробнее: см. /help в боте [@TransToOldSlavonic_bot](https://t.me/TransToOldSlavonic_bot).

Лицензия: [MIT License](LICENSE).

Статья в Telegraph:
https://telegra.ph/Perevodchik-na-staroslavyanskij-02-28.

* * *

В версии 1.0.0 некоторые файлы отдельно вынесены [в папку контроля версий](meta/versions-controll) с удалением этих файлов в корне.

Начиная с момента появления нумерованных версий (1.0.0+, [commit 16](https://github.com/1-1-1-1-1-1-1-1/Old-Slavonic-bot/commit/88eeaa768d4f2a382de0583ef23f162b91b60302) в GitHub) есть три версии, записываемые в папке [meta/versions-controll](meta/versions-controll): в библиотеках `telebot`, `aiogram`, `telethon`. Файлы/данные, записанные или подтвержденные до этого момента, приоритетно считать не столь авторитетными, как те, которые записаны или подтверджены во время, начиная с него.

Причина создания нескольких версий:

 - в `telethon` есть возможность удобно делать некоторые вещи (например писать код: `await event.reply(...)` вместо `bot.send_message(message.id, ..., reply_to_message_id=message.message_id)`, не говоря о возможности поиска пользователя в чате не по данным *только* Telegram, а с возможностью поиска в данных локального кеша). В `telebot` о таких возможностях, по крайней мере ранее, не было оглашено;
 - в `telebot` код простой и похож на код в `aiogram`, но не все вещи легко сделать;
 - в `aiogram` некоторое может быть писать удобнее, чем в `telebot`.

История изменений по номерам версий: [ChangeLog.txt](meta/versions-controll/ChangeLog.txt).

* * *

## Применение
<a id="usage"></a>

### Перевод и странслитерация
<a id="usage-trans"></a>

Бот при вводе его имени пользователя (@⁠TransToOldSlavonic_bot) и текста после него осуществляет попытку (см. \[1]) перевести текст на старославянский язык. Отправлять результат можно сразу в тот чат, где сделан такой ввод. Для отправки достаточно нажать на блок с отправляемым текстом.

\[1]: Подробно о функциях перевода: см., например,

 - [определение функции перевода вместе с транслитерацией](functions.py#L637),
 - [определение функции транслитерации на глаголическое письмо](functions.py#L349).

Пример перевода слова или текста в режиме [inline](https://core.telegram.org/bots/inline):

![Пример перевода слов](meta/media/usage-trans.jpg)
![Пример перевода текста](meta/media/trans-example.jpg)

### Значение слова
<a id="usage-meaning"></a>

По команде `/meaning` бот ищет значение слова. Возможен поиск со словами при игре в слова. См. `/meaning help` в боте для подробного описания.

В действии:

![](meta/media/meaning.jpg)

## Файлы и папки
<a id="files"></a>

* Папка с файлами, специфическими при написании бота с различными библиотеками: `telebot`, `aiogram`, `telethon`.
* Некоторые данные: в папке [data](data/).
* Файл с определением функций перевода и транслитерации: [functions.py](functions.py).

## References (литература; документация; ссылки)
<a id="references"></a>

### Функции перевода и транслитерации, их работа
<a id="func-refs"></a>

 * Схема переводов: в [meta/Scheme.txt](meta/Scheme.txt).
 * Работа функций транслитерации:
     - https://www.ponomar.net/files/gama2/p002.htm (Название: "§2. Употребление и произношение букв")
 * Про числа:
     - Общие сведения: http://lukianpovorotov.narod.ru/Folder_Pravoslavie/tserkovnoslavyanskiye_chisla.html
     - Подробности: http://konorama.ru/servisy/slacy/
     - Программа для конвертации чисел: http://info-7.ru/Titlo/Titlo.shtml (link to this was at Wikipedia, see prev. source)

### Работа бота
<a id="bot-refs"></a>

 - Режим inline:
     + https://core.telegram.org/bots/inline
 - Мануалы по режиму `inline` в `telebot`:
     + https://mastergroosha.github.io/telegram-tutorial/docs/lesson_07/,
     + https://mastergroosha.github.io/telegram-tutorial/docs/lesson_08/ <з
 - Telegram Bot API: https://core.telegram.org/bots/api

### Heroku
<a id="heroku-refs"></a>

 * Deployment: https://devcenter.heroku.com/categories/deployment
 * Creating a 'Deploy to Heroku' Button: https://devcenter.heroku.com/articles/heroku-button

### Bot API
<a id="bot-api-refs"></a>

#### Telethon API
<a id="telethon-api-refs"></a>

* Ссылка на Telethon API: https://tl.telethon.dev/.
* Bot API vs MTProto: https://docs.telethon.dev/en/latest/concepts/botapi-vs-mtproto.html.
* Также: https://docs.telethon.dev/en/latest/concepts/botapi-vs-mtproto.html?highlight=API#what-is-mtproto.
* Про Telethon API: https://docs.telethon.dev/en/latest/concepts/full-api.html
    + Часть текста про Telethon API:
    > While you have access to this, you should always use the friendly methods listed on  [Client Reference](https://docs.telethon.dev/en/latest/quick-references/client-reference.html#client-ref) unless you have a better reason not to, like a method not existing or you wanting more control.
* О переходе от `aiogram`/`telebot` к `telethon`: https://docs.telethon.dev/en/latest/concepts/botapi-vs-mtproto.html#botapi.

#### Telegram Bot API
<a id="telegram-bot-api-refs"></a>

Ссылка на Telegram Bot API: https://core.telegram.org/bots/api.

> **Замечание**: Библиотеки `aiogram` и `telebot` являются реализацией этого API. Библиотека `telethon` написана с применением [другого](https://tl.telethon.dev/) (собственного) API.

 * Про требуемую для действия inline-кнопок вещь (как пример в `/help`; `InlineKeyboardMarkup`):
 > Note: This will only work in Telegram versions released after 9 April, 2016.

 (*from the [Telegram Bot API]*)

 * Текст inline-запроса (через `@<bot_username> text`):
 > Text of the query (up to 256 characters)

 (*from the [Telegram Bot API]*)

### Другое
<a id="other-refs"></a>

 * Частичная документация по Git: https://git-scm.com/book/ru/v2/Основы-Git-Создание-Git-репозитория/.
 * https://pypi.org/project/python-dotenv/
 * http://www.fabfile.org/ link to it was at prev. (dotenv.).

### Некоторая общая документация
<a id="some-general-doc-refs"></a>

 * Боты в Telegram: https://core.telegram.org/bots.
 * Telegram Bot API: https://core.telegram.org/bots/api.
 * Документация к `telethon` (`pip`: `Telethon`): https://docs.telethon.dev/en/latest/.
 * Документация к `aiogram`: https://docs.aiogram.dev/en/latest/.
 * Документация к `telebot` (`pip`: `pyTelegramBotAPI`):
   + https://github.com/eternnoir/pyTelegramBotAPI#pytelegrambotapi;
   + https://pypi.org/project/pyTelegramBotAPI/.

[Telegram Bot API]: https://core.telegram.org/bots/api

## See also
<a id="see-also"></a>

 * История изменений, нумерация по версиям: [meta/versions-controll/ChangeLog.txt](meta/versions-controll/ChangeLog.txt).
 * Некоторые заметки: [meta/NOTES.md.txt](meta/NOTES.md.txt).
 
[К началу страницы](#top)
