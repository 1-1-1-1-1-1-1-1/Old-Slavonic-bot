# **NOTE**
# =============================================================================
#
# This file can be parsed by some func. in order to get comments, as a text.  A
# Python ext. is set **only** in order to give a hint to the text editor:
# > **it is a Python file** (there comments can be edited somehow easier).

# See <root>/meta/utils/../parse_comment.

<comment>:general
# THIS CODE AND APP ARE FREE FOR USAGE AND MAINTAINED & DISTRIBUTED UNDER THE
# TERMS OF *MIT License*. See LICENSE for more info.
# 
# The code is FREE FOR COPY, CHANGE, AND THE CODE's SHARING.  (?) **QUESTION**
#
# =============================================================================
# Main file, written preferably with PEP8, required modules/libraries
# are in requirements.txt.
# 
# **PLEASE NOTE:** The `version: lib:v_name` is important at the beginning of
# this file. It is parsed while writing this file to the root in order to get
# the most recent information about what version of app is used and write it 
# to the "current-version.txt" immediately.
#
# -----------------------------------------------------------------------------
# See also:
# - README for some info.
# - "metalog.txt"|TODO for some instant/following/current changes.
# - File config.py to view or change the configurations
# - File .env or its analogues.
# - Launcher and similar to have a possible help with launching the bot app
# - File "meta/All TODO/TODO.md" to view some TODO and notes on the code or
#   other objects, somehow connected with this code and the bot.
# Requires Python >=3.8 to allow the use of `:=`
# set the required version at runtime.txt (see also: runtime info at [1])
# 
# [1]: https://devcenter.heroku.com/articles/python-runtimes#supported-runtime-versions
#
# -----------------------------------------------------------------------------
# 
# Development notes
# -----------------
# 
# - possible meta-notes at this file:
#   note, question/questions (different), mark,
#   checked, to test/to check, test, TODO, meta, OR, task
#    + these are sometimes not case-sensitive
# - [telethon] this can help to ignore further triggers for an exact update:
#   `raise events.StopPropagation`
# - may use "case 1"/another (use quote symbol) to mark, which words are
#   included.
# - noting versions at some places (e.g. functions/classes) to show, which of
#   version they are ("at which version"/when they were written/added)
#   + marking versions: either "version-name", or "v:<comment>", e.g. when
#     comment is "undefined"
#     * "to-check" means "nearly final version, to check still, and merge"
# - `configparser.ConfigParser()` is sometimes created exactly at the
#   function's call, which is to work correctly, if several users use a
#   bot simultaneously (TODO: What? Solve.)
# 
# TODO
# ----
# 
# - Marked with TODO, question[s].
# - Merge TODO, questions etc. from everywhere.
# - Test: triggers to start, words, BotException (see comments)
# - TODO from "../TODO".
#
# Meta
# ----
# 
# versions stages:
# '-editing' (means editing in process)
# rcN means realise candidate; if no issues are mentioned -- considired to
# be ready
# 
# See also: PEP440.
# 
# Notes & comments syntax
# -----------------------
# 
# - Mixed Markdown and Sphinx, also using some Sphinx-styled maybe-not-existed
#   commands. Markdown is either plain or a GFM. Example of a pseudo-Sphinx
#   syntax:
#   .. edit-date::
#   
#       2021-06-01T12:00:00Z
# - `re` expressions
# - Such as:
#   + [...] -- optional part
#   + <var>, meaning an exact variable, inserted at a place of the "<var>".
#   + Several Markdown-styled, but not really existed, e.g. `word_or_text'
# - Can be related somehow to pyTorch.
</comment>:general
