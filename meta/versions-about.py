# -*- coding: utf-8 -*-

# This states for a meta about to what does the versions names notation here is

# versions' names syntax:
# version = `<library>:<version>[-<extra_mark>]`
# example: 'telebot:1.0.1-lw-making'; or 'telethon:1.2'


def parse_version(full_name: str) -> tuple:
	"""Parse the version's full name and return `(library, version, extra)`.

	Extra may be either `None`, or a `str` object.
	"""
	# library name can not contain ':'
	library, other = full_name.split(':', maxsplit=1)
	dash = '-'
	if dash in other:
		version, extra = other.split(dash, maxsplit=1)
	else:
		version = other
		extra = None
	return (library, version, extra)


# Test ---

def test(full_names: 'iterable') -> 'generator':
	return (parse_version(full_name)
			for full_name in full_names)

if __name__ == '__main__':
	gen = test([
		'lib:1.0-bot-basic',
		'aiogram:test'
	])
	print(*gen)
