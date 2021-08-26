"""A utility to escape ... Styles: ..."""


from .escape_markdown import escape as escape_markdown
from .escape_markdown_v2 import escape as escape_markdown_v2


__all__ = ['escape']


def escape(s: str, version='v2') -> str:
	"""Escape the string, using either Markdown syntax, or Markdown_V2 syntax.
	Version: either 'v2', or ''.
	"""
	suffix = '_v2' if version == 'v2' else ''
	_escape = eval('escape' + '_markdown' + suffix)
	return _escape(s)
