# This is to write an escape function to escape text at the MarkdownV2 style.
# 
# **NOTE**
# The [1]'s content provides some notes on how strings should be escaped,
# but let the user deal with it himself; there are such things as "the string
# ___italic underline___ should be changed to ___italic underline_\r__,
# where \r is a character with code 13", but this program's aim is not being a
# perfect text parser/a perfect escaper of symbols at text.
# 
# References:
# -----------
# 
# [1]: https://core.telegram.org/bots/api#markdownv2-style
# 
# Bot API version: 5.3


# import re


_special_symbols = {
	'_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{',
	'}', '.', '!'
}


def escape(string: str) -> str:
	for symbol in _special_symbols:
		# Escape each special symbol
		string = string.replace(symbol, '\\' + symbol)
		# Mind that such sequences, being replaced, do not intersect.
		# Replacement order is not important.
	return string
