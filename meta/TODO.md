# TOC
 - [Translating and transliterating](#tra_and_tra)
    + [translating](#translating)
        * possible: from not Russian
    + [transliterating](#transliterating)
    + [mixed](#tr_mixed)
 - [inline queries](#inline)
 - [Game 'words'](#game_words)
 - [Hosting the bot](#hosting)
 - [Other notes](#other_notes)

## Translating and transliterating
<a id="tra_and_tra"></a>

### Translating
<a id="translating"></a>
TODO:

 * Great dictionaries. As a part, the dict., named there '2' once.

### Transliterating
<a id="translating"></a>
TODO:

 * [ ] <u>Numbers' transliteration</u>
     + Transliterating to glagolic — ?. Was strange, see at `./media`.
     + Transliterating to cyryllic.
         - Can add: parts of symbols for 10^5, ..., 9 (?).
         - Can add: `от` instead of `омега`, putting titlo only at some cases.
           Not putting at `омега`, `і`.
         - Make it great.

Maybe TODO:

- add some dictionary transliterations (if required).

### Mixed
<a id="tr_mixed"></a>

Possible (maybe, not availaible here):

 * translation with no transliteration
 * just transliteration
     - numbers
         + with no numbers' transliteration
         + ... or with it.
      - alphabeth
          + cyryllic
          + glagolic
* when initial language is not Russian
  (can be translated to Russian firstly, then see other parts of this)

See 'Scheme.txt'.

## Inline queries
<a id="inline"></a>
Tasks:

 * What do happens with symbols there, i. e. how should the bot be done in order to put them greatly?
 * Using it with replacing names: the prefered way — ? (E. g., it can be at query's *start* only)

Notes:

 - See https://core.telegram.org/bots/inline

## Game 'words'
<a id="game"></a>
Possible TODO:

 * Add transliterating at phrases.
 * Add the support of dash (can be different?) at words. Can other be? Should be?
 * Add an ability to teach a word (if not found at any dictionary).
 * Add an option to search for a word, whether exists, at the Slavonic dictionaries.
 * ... + transliterate.

Notes:

 * Bot moves in a row (if it is put in order twice in a row) — ?

## Hosting & deploying
<a id="hosting"></a>

Possible places:

 * at https://www.pythonanywhere.com (1)
 * at https://heroku.com

## Other notes
<a id="other_notes"></a>

`tokens.py` may be added in a such way, that it is absent in the code storage, where the main part is taken from (considering `GitHub` as it). (?->no) Hosting at (1), it can be added to the files there.  Deploying at the Heroku, may be added via config vars.

 * Restricting user requires in the group some enough rights.
 * Permission to use functions/commands — !

 * Translating mix of numbers and letters — ?

 * The correct translation generally — ?

 * The correct match of case at tanslations — ?
 * Is it in the best way?
 * Parse at folder '_2 col' and find all there.

TODO:

 * [ ] Write great docstrings.
 * [ ] Add `meaning` as a single function, can be used at here: command `meaning`, checking for the word, whether exists at game words' play.
 * [ ] change tokens and/or other params, were at .env-todo (commit 181e106)
     + *note*: changed; to check/swallow, what is

Maybe-TODO, general:

 * Possible: add great logs and logging system.
 * Possible: add the great sctructure.
 * Possible: delete all dispansable files.
 * Write great docstrings for the functions.
 * Realize some of this as things at DB, not as files *at* the project.
 * Add ability to make `е/ё` equal at:
     + game 'words'
     + translating
 * At the auto-insert at chat (at the inline):
 add the change of query's query at the click on it (after).
 * Make the process of adding users' ids to the bases more strict and exact, multifunctional.

Delete dispansable!

Exceptions at code: what it the better part and better at all?

...
