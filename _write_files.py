# -*- coding: utf-8 -*-
# Tool to write files of the exact version to the root.
#
# Running as a tool at cmd line, requires `argparse`; that thing is not at Python
# stdlib. Can install it via `pip install argparse` on Windows.


allow_run_as_script = True
# *Note*: To run as a script, do not choose versions at `version`.


import os
import re
import warnings
import typing
from typing import Optional, Union, NoReturn, Literal
from pathlib import Path
import configparser  # See the tracker of files changes made.
                     # That is a file _changed_tracker.py or like it.
import time
from copy import copy

import argparse

from globalconfig import INITIAL_FILE
from meta.utils.parse_comment import load_comments 
from meta.utils.versions_about import parse_version


_VERSION_NAME_TYPE = Optional[Union[re.Pattern, str]]
DEFAULT_ALL_FILES = [
    INITIAL_FILE,
    "config.py",
    "requirements.txt"
]


current_version_source = Path("meta") / "versions-controll" / "cversion.txt"
try:
    with open(current_version_source,
              encoding='utf-8') as f:
        _version_to_choose_pattern = f.read().strip()
    version_to_choose_pattern = eval(_version_to_choose_pattern)
except:
    version_to_choose_pattern = None


filename = os.path.split(__file__)[-1]
version_to_choose: _VERSION_NAME_TYPE = version_to_choose_pattern

# Whether warning about versions' difference is enabled.
warn_about_v_difference_enabled = True


version = [
    "aiogram",
    "->telethon",
    "telebot"
]


def choose_version(v_name: _VERSION_NAME_TYPE = None) \
    -> NoReturn:
    """A utility to choose version.

    Usage: pass a pattern, applying to the start of searched version,
    at the v_name. Only one version should match that pattern.
    Pass None to choose nothing.
    """
    global version
    if not v_name:
        return
    regexp = v_name
    _index = [item for item in version if re.match(regexp, item.lstrip('->'))]
    if not _index:
        msg = (
            "Index to change chosen version not found. "
            "Doing nothing."
            )
        warnings.warn(msg)
        return
    elif len(_index) > 1:
        warnings.warn(
            "Multiple versions to change the choice found. "
            "Doing nothing."
            )
        return
    indexed: str = _index[0].lstrip('->')
    for i, name in enumerate(version):
        name = name.lstrip("->")
        if name == indexed:
            name = '->' + name
        version[i] = name


choose_version(version_to_choose)
# Syntax to choose an item: change "item" to "->item".
candidates = [item for item in version if item.startswith('->')]
if len(candidates) > 1:
    raise SystemExit("Can't choose 2 versions simultaneously.")
elif not candidates:
    version = None
else:
    version = candidates[0].lstrip('->').strip()


# === configparser meta-utils =================================================


c = configparser.ConfigParser()
tracker_config_filename = os.path.join("locals", 'tracker.ini')
c.read(tracker_config_filename, encoding='utf-8')


def _disable_tracker():
    """Disable tracker, see the _changed_tracker.py or like that."""
    if not c.has_section('main'):
        return
    c['main']['requires_set_defaults'] = 'true'
    c['main']['can_reload'] = 'false'
    with open(tracker_config_filename, 'w') as f:
        c.write(f)


def _allow_reload_tracker_defaults():
    """Allow the tracker being reloaded.
    See _changed_tracker.py or like that.
    """
    if not c.has_section('main'):
        return
    c['main']['requires_set_defaults'] = 'true'
    with open(tracker_config_filename, 'w') as f:
        c.write(f)


# === Main function ===========================================================


def main(v_name=None, files=[], *,
         encoding='utf-8'):
    """Write files `files` to the root, doing additional stuff.

    Additional stuff
    ----------------
    Update content of current-version.txt and ensure that versions
    at `files` do correspond to versions at `INITIAL_FILE`; if not,
    make a corresponding mark / note.

    On success print corresponding messages to the buffer/stream.
    While doing all, disable tracker; enabled at the end.
    """
    #
    # Do some preliminary stuff.
    #

    assert files

    if encoding in {'basic', 'utf-8'}:
        encoding = 'utf-8'
    else:
        exc_message = "encoding undefined"
        raise TypeError(exc_message)

    # Do stuff is v_name is not given. Get it via the CLI.
    if not v_name:
        help_message = f"""Usage:
    {filename} library

Writes files {', '.join(files)} to the root folder.
    """
        parser = argparse.ArgumentParser(description=help_message)
        parser.add_argument('v_name', type=str, help='Name of library')
        args = parser.parse_args()
        v_name = args.v_name
 
    print(
        "🛑Disabling tracker of version files, written to the root..."
        )
    _disable_tracker()
    time.sleep(0.5)  # Prevent some strange behaviour.

    print(f"Writing with version: {v_name}")
    
    root = os.path.abspath(os.curdir)
    folder = Path(root) / 'meta' / 'versions-controll'

    exact_name = None
    for name in os.listdir(folder):
        if v_name.lower() in name.lower():
            exact_name = name
            break
    if exact_name:
        os.chdir(folder)
        os.chdir(exact_name)
        path = os.path.abspath(os.curdir)
    else:
        er_msg = f"undefined folder's name: of version {v_name}. Sure?"
        raise TypeError(
                er_msg
            )
    os.chdir(root); del root

    #
    # Writing files to the root
    #

    comments = load_comments()
    for fname in files:
        name, ext = os.path.splitext(fname)
        mod_fname = name + '-' + v_name + ext
        with open(os.path.join(path, mod_fname), encoding=encoding) as f:
            data = f.readlines()
        for index, line in enumerate(data):  # Set comments.
            match = re.fullmatch(r'#+\s+<comment:(\w+):(\w+)>' + r'\n',
                                 line,
                                 re.IGNORECASE)
            if not match:
                continue
            c_type, lib_name_local = match.groups()
            comment = comments[c_type]
            data[index] = comment
        data = ''.join(data)
        with open(fname, 'w', encoding=encoding) as f:
            f.write(data)
        print(f"\t🖊️Wrote file {fname} to root")
        
    # Detect the main file.
    if INITIAL_FILE in files:
        main_file = INITIAL_FILE
    else:
        main_file = files[0]

    # Open just written file, find version's full name.
    version_is_undefined = False
    with open(main_file, encoding=encoding) as f:
        index = 0
        while index < 3:
            line = f.readline()
            part = '# version:'
            if line.startswith(part):
                full_name = line.split(part)[1].strip()
                break
            index += 1
        else:
            version_is_undefined = True
            full_name = ':'.join(
                    (
                        v_name,
                        "undefined"
                    )
                )
    print(
        "📚Read version full name from {0}. ".format(main_file)
        + "Name of version: {0}".format(full_name)
        )
    library = v_name

    # Get version info as a tuple.
    v_info: tuple[str, Optional[str]] = parse_version(full_name)[1:]
    name = '-'.join(filter(lambda i: i,
                    v_info))
    version_number: str = v_info[0]

    pattern = r'(.+)\+'

    def assert_form(s: str) -> bool:
        _result = re.fullmatch(pattern, s)
        return bool(_result)

    if assert_form(version_number):
        msg = (
            "version number at {0} is not strict, ".format(main_file)
            + "be careful"
        )
        warnings.warn(msg)

    # Warn about the version difference, if required.
    if not version_is_undefined and warn_about_v_difference_enabled:
        def another_version_marked_exists() -> Optional[Literal[0]]:
            # Whether file, marked with another version, exists.
            # Return 0 if the answer is yes, None otherwise.

            nonlocal pattern
            for fname in set(files) - {main_file}:
                with open(fname, encoding=encoding) as f:
                    lines_: list[str] = f.readlines()
                    part = '# version:'

                    # Find the version if given, do stuff if another version
                    # found.
                    for line in lines_:
                        if line.startswith(part):
                            full_name_local = line.split(part)[1].strip()
                            v_number_local = parse_version(full_name_local)[1]
                            match = re.fullmatch(pattern, v_number_local)
                            if match:
                                # Ignore match failure when v_number_local
                                # ends with '+' end it's a "<v_local_>+",
                                # v_local_ >= version_number.

                                v_number_local_ = match.group(1)
                                
                                # Check whether version_number and same local
                                # do match '[0-9]+\.[0-9]+\.(?:[0-9]+)?'.

                                pattern = r'[0-9]+\.[0-9]+\.(?:[0-9]+)?'

                                if assert_form(version_number) \
                                and assert_form(v_number_local_):
                                    tuple_initial = version_number.split('.')
                                    tuple_initial = tuple(map(int,
                                                              tuple_initial))
                                    tuple_local = v_number_local_.split('.')
                                    tuple_local = tuple(map(int,
                                                            tuple_local))
                                    if tuple_initial >= tuple_local:
                                        continue
                                    else:
                                        return 0
                                else:
                                    # At least one of that strings
                                    # does not match pattern.
                                    pass

                            # Now v_number_local doesn't end with '+'.
                            if full_name_local != full_name:
                                return 0
        
        _do_warn_about_version_difference = another_version_marked_exists()
        
        if _do_warn_about_version_difference == 0:
            msg = (
                "❗ Versions at files may be inappropriate "
                "with each other, be careful"
            )
            warnings.warn(msg)
        else:
            print("✓ No imcompatible versions at version files found.")
            
    current_version_fname = 'current-version.txt'

    #
    # Do some stuff with this file.
    #

    # Get `data` and `lines`.
    with open(current_version_fname, encoding=encoding) as f:
        data: list[str] = f.readlines()
        data_copy = copy(data)

        started = False
        lines = []  # List of integer numbers.
        # `lines` is a list of possible lines' indexes to change.
        i = 0
        while data_copy:
            line = data_copy.pop(0)
            if line.startswith(".. version"):
                # Mark that the search started.
                started = True
            elif line.lstrip('\t\f ') != line or not line.rstrip('\n'):
                lines.append(i)
            elif started:
                break
            i += 1

    # Change some "lines", if required.
    for i in lines:
        if (str_ := ':type:') in data[i]:
            j = data[i].index(str_) + len(str_)
            data[i] = data[i][:j] + ' at ' + library
            data[i] += '\n'
        elif (str_ := ':name:') in data[i]:
            j = data[i].index(str_) + len(str_)
            data[i] = data[i][:j] + ' ' + name
            data[i] += '\n'
    
    # Update content at file current_version_fname.    
    with open(current_version_fname, 'w', encoding=encoding) as f:
        f.write(''.join(data))
        print(f"📔Updated the content of file {current_version_fname}.")

    #
    # Allow tracker being reloaded. After doing it all is considered done.
    #

    _allow_reload_tracker_defaults()
    print("✅Allowed the tracked being worked further, "
        "reloading variables. All is done.")


if __name__ == '__main__':
    files = DEFAULT_ALL_FILES
    main(version, files)
