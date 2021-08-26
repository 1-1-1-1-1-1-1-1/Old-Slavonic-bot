# TODOs description file
<a id="top"></a>

## Table of contents

 - [Translating and transliterating](#tra_and_tra)
    + [Translating](#translating)
    + [Transliterating](#transliterating)
    + [Mixed](#tr_mixed)
 - [Documentation, code, style](#docs)
 - [Inline queries](#inline)
 - [Game 'words'](#game_words)
 - [Hosting the bot](#hosting)
 - [Other notes](#other_notes)

## Translating and transliterating
<a id="tra_and_tra"></a>

### Translating
<a id="translating"></a>

**TODO:**

 * Make great dictionaries. In particular, the dictionary, named "2" and, as temporary, "3".

### Transliterating
<a id="translating"></a>

**TODO:**

 * [ ] Numbers' transliteration
     + [ ] Transliterating to Glagolitic — ?. Was strange, see at [/media/extra]([/media/extra]).
     + [ ] Transliterating to Cyryllic.
         - [ ] [Optional] Add tranliterating using parts of symbols for 10^5, ..., 9 (?).
         - [x] [Optional] Add: `от` instead of `омега`, putting titlo only at some cases.
           Not putting at `омега`, `і`.

**Maybe TODO:**

- Add several dictionary transliterations.

### Mixed
<a id="tr_mixed"></a>

**Possible features:**

 * [availaible] translation with no transliteration
 * [availailbe] with just the transliteration
     - transliteration of numbers
         + [availaible] with no numbers transliteration
         + [availaible] with the transliteration of numbers
      - to the scripts of the Old Slavonic language:
          + [availaible] Cyryllic
          + [availaible] Glagolitic
* Do translation or a transliteration action, when initial language is not Russian. Possible strategy: the text can be translated to Russian firstly, then a normal action with a translated text can be done; see other code parts to view what the normal action is.

**Notes:**

 * Translating mix of numbers and letters — ?
 * The correct/sufficient/suitable translation generally — ?

***References***

 * File with functions: functions.py at root.
 * See 'Scheme.txt'.

## Directly the bot

This is a part describing some 'features / TODO' connected directly with the bot.

 - [ ] Make great commands. See notes from https://core.telegram.org/bots/api#june-25-2021.
 - [ ] [Optional] Set commands maybe+ at chats individually. Can use Bot API.

## Documentation, code, style
<a id="docs"></a>

Here several TODO connected with docs, code and style are described. Also, here may be notes on those.

**TODO:**

 * [ ] Delete all dispansable.
 * [ ] Make great structure and style.
 * [ ] Make the code clear.
 * [ ] Write great docstrings for functions, which are better to exist with them or just require it.
 * [ ] Write great docstrings for all. Great docstring for a place, which does not required a docs, and it's useless there -- no docs at all. Make it [simple](#cite-simple).
 * [ ] Add great logs and logging system.

## Inline queries
<a id="inline"></a>

This is a part describing some 'features / TODO' connected directly with the inline queries at this bot.

**TODO:**

 * [ ] What do happens with symbols there, i.e. how should the bot be done in order to put them greatly?
 * [ ] Using it with replacing names: which is the prefered way? (E.g., it can be at query's *start* only.)

**Notes:**

 - See https://core.telegram.org/bots/inline.

## Game 'words'
<a id="game"></a>

**Possible TODO:**

 * Add transliterating at phrases. [What is it?]
 * Add the support of dash (can be different?) at words. Can other be? Should be?
 * Add an ability to teach a word (if not found at any dictionary).
 * ...
 * ... + transliterate.

**Notes:**

 * What is the best way to perform bot's moves in a row (if it is put in order twice in a row)? Or should it be even? How to react then?

## Hosting & deploying
<a id="hosting"></a>

Possible places:

 * https://www.pythonanywhere.com (1)
 * https://heroku.com

## Other notes
<a id="other_notes"></a>

**NOTES:**

File `tokens.py` (see earlier/pretty first versions) may be added in a such way, that it is absent in the code storage, where the main part is taken from (considering `GitHub` as it). Hosting at (1), maybe, it can be added to the files there. Deploying at the Heroku, may be added via config vars.

 * Restricting user in group requires enough rights.
 * Permission to use functions/commands: mind it! E.g., command "do".
 * Is it on the best way?
 * Parse at folder '_2 col' and find all there.
 * Exceptions at code: what it the better part and better at all?
 * See file `.env-todo` at commit `181e106`.
     - All values changed there, beside a single.
     - Single not changed: `NAMES_REPLACE`.

**TODO**:

 * [ ] Solve all TODO at worker.py and other.
 * [ ] Test all, which do requires the test.
 * [ ] There may be some issues with the correct work of things, connected with hidden via gitignore files, writing files or doing stuff, special to Heroku, meaning "but common for usage via PC (was done at least on some Windows)". Fix them all, if any such issues do exist.
 * [ ] [Possible] At the auto-insert of random example with inline button:
 add the change of query's query on, i.e. after, the click on it.
 * [ ] [Possible] Realise some of this as things at DB, not as files *at* the project. E.g., storing users' IDs or storing the data of game "words".
 * [ ] [Possible] [Is partially availailbe by default] Add ability to make `е/ё` equal at:
     - [Is partially availaible by default] game "words"
     - translating
 * [x] Add a base for storing `help` messages for any chat (e.g. at `.json`).
     - Made as a store at `.json` file.
 * [ ] Write all meta-parts.
 * [ ] Finish writing the telebot version, if required.


<a id="cite-simple"></a>

> Everything should be made as simple as possible, but no simpler

*Albert Einstein’s*

> Сделай настолько просто, насколько это возможно, но не проще.

*Альберт Эйнштейн*


[*up to top*](#top)

