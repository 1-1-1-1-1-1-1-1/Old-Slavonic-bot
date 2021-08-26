# -*- coding: utf-8 -*-

# This states for a meta about to what does the versions names notation here is

# versions' names syntax:
# version = `<library>:<version>[-<extra_mark>]`
# example: 'telebot:1.0.1-lw-making'; or 'telethon:1.2'

# For the test:
# version: lib:name-extra


import re
from collections.abc import Iterable
from typing import Optional, NoReturn


VersionTuple = tuple[str, str, Optional[str]]


__all__ = ['allowed_patterns', 'parse_version', 'get_version']


DEFAULT_PATTERN = r'(?i)[\t\f ]*#.*version[\t\f ]?[:=](.*)\n'
BASIC_PATTERN = r'(?i)# version: (.*)\n'


allowed_patterns = (
	DEFAULT_PATTERN,
	BASIC_PATTERN,
	"a compilable re object"
)
allowed_patterns = frozenset(allowed_patterns)


def parse_version(full_name: str) -> VersionTuple:
	"""Parse the version's full name and return ``(library, version, extra)''.

	Extra is either `None`, or a str object.
	"""
	# Library name can not contain ':'.
	library, other = full_name.split(':', maxsplit=1)
	dash = '-'
	if dash in other:
		version, extra = other.split(dash, maxsplit=1)
	else:
		version = other
		extra = None
	return (library, version, extra)


def get_version(fname, read_lines='all', pattern='default') -> \
	Optional[VersionTuple]:
	"""Get a version from file. Return `None` when not found."""
	# Syntax at file: `# version:\s?(?P<library>...):(name[-extra])`
	if read_lines != 'all' and type(read_lines) is not int:
		raise NotImplementedError("Read only either `all` lines,"
			" or `N` lines")
	# if read_lines == 'all':
	# 	read_lines = -1

	pattern = pattern.lower()

	if pattern == 'default':
		pattern = DEFAULT_PATTERN
	elif pattern == 'basic':
		patern = BASIC_PATTERN
	else:
		try:
			pattern = re.compile(pattern)
		except:
			raise ValueError(
				"pattern should be one of default, basic and "
				"a compliable re pattern"
				)

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


# -- Test ---


def test(full_names: Iterable[str]) -> list[VersionTuple]:
	"""
	>>> test('lib:version-extra', 'lib:version')
	[('lib', 'version', 'extra'), ('lib', 'version', None)]
	"""
	return [parse_version(full_name)
			for full_name in full_names]


def test_1() -> NoReturn:
	obj = test([
		'lib:1.0-bot-basic',
		'aiogram:test'
	])
	print(*obj)

	print(get_version(__file__))


if __name__ == '__main__':
	test_1()
