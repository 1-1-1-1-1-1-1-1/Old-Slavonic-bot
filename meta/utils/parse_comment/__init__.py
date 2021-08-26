import os
import re
from pathlib import Path
from datetime import datetime


# Determine root folder of that file.    
try:  # Parse after read env file (e. g. via dotenv.load_dotenv)
    # Get root from env.; sample.
    do_some_stuff()
except (AssertionError, Exception):
    utility_root = os.path.split(__file__)[0]

utility_root = Path(utility_root)


if __name__ == '__main__':  # Be careful.
    # Set dir to appropriate folder.
    os.chdir(utility_root)


# Default comments source / storage.
fname = utility_root / 'comments.py'


def _mkpattern(c_type: str) -> str:
    # Pattern at file:
    # 
    # <comment>:c_type
    # ...  # <- This is comment.
    # ...  # It can be a multline comment.
    # </comment>:c_type

    pattern = (
        r'<comment>:' + c_type  # Tag opened.
        + r'\n'  # Newline.
        + '(.+)'  # Comment.
        + r'\n</comment>:' + c_type  # Tag closed.
    )
    return pattern


def load_comments(comments_names: list[str] = ['general'],
                  /, fname=fname) -> dict[str, str]:
    """Load comments from the file.
    
    :param comments_names: A list of str, each item is a name of comment.
    :param fname: A file to open. Comments are loaded from that file.
    
    :return: A dictionary of ``(comment_name: str, comment: str)'' for all
             comment_name in ``comment_names''.
    """
    comments = {}
    with open(fname, encoding='utf-8') as f:
        text = f.read()
        for c_type in comments_names:
            pattern = _mkpattern(c_type)
            match = re.search(pattern, text, re.DOTALL)
            comment = match.group(1).strip('\n')
            comment += '\n'  # Newline at the end of comment.
            comments[c_type] = comment

    return comments


# --- Tests ---


def test(*args):
    """
    >>> test(set{['general']})  # doctest: +ELLIPSIS
    {'general': ...}
    """
    func = load_comments
    result = func(*args)
    return result


if __name__ == '__main__':
    text_com: dict[str, str] = test()
    with open(os.path.splitext(fname)[0] + '-!private-test.txt', 'w',
              encoding='utf-8') as f:
        f.write(text_com['general'])
