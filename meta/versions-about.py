# -*- coding: utf-8 -*-

# This states for a meta about to what does the versions names notation here is

# versions' names syntax:
# version = `<library>:<version>[-<extra_mark>]`
# example: 'telebot:1.0.1-lw-making'; or 'telethon:1.2'

# For the test:
# version: lib:name-extra


__all__ = ['allowed_patterns', 'parse_version', 'get_version']


DEFAULT_PATTERN = r'(?i)[\t\f ]*#.*version[\t\f ]?[:=](.*)\n'
BASIC_PATTERN = r'(?i)# version: (.*)\n'


allowed_patterns = frozenset(
	DEFAULT_PATTERN,
	BASIC_PATTERN,
	"a compilable re object"
)


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


def get_version(fname, read_lines='all', pattern='default') -> tuple:
	"""Get a version from file."""
	# Syntax at file: `# version:\s?(?P<library>...):(name[-extra])`
	if read_lines != 'all' and type(read_lines) is not int:
		raise NotImplementedError("Read only either `all` lines,"
			" or `N` lines")
	# if read_lines == 'all':
	# 	read_lines = -1

	pattern = pattern.lower()

	if not 're' in globals():
		import re

	if pattern == 'default':
		pattern = DEFAULT_PATTERN
	elif pattern == 'basic':
		patern = BASIC_PATTERN
	else:
		try:
			pattern = re.compile(pattern)
		except:
			raise ValueError("pattern should be one of default, basic and "\
				"a compliable re pattern")

	with open(fname, 'r', encoding='utf-8') as f:
		lines = f.readlines()
		while lines and read_lines:
			line = lines.pop(0)
			match = re.fullmatch(pattern, line)
			if match:
				full_name = match.group(1).strip()
				return parse_version(full_name)
			if type(read_lines) is int:
				read_lines -= 1

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

	print(get_version(__file__))
