# -*- coding: utf-8 -*-

# Written at 2021-08-03

# This file is an utility to track, whether the files of versions, written to
# the root, are changed.
# Main idea: refer to meta/tracker-about.txt.

# Usage: start this code's execution and don't close.


if __name__ != '__main__':
    # Running in other places is not really required.
    raise SystemExit("Can run only in one thread, only in main.")


import tkinter
import tkinter.messagebox as mbox
from textwrap import dedent  # for code's readability
import datetime  # tracking time
from os.path import join  # join path
import warnings
from typing import NoReturn, Optional

import configparser  # To have an option to disable tracker
                     # while rewriting files manually.


TIME_FORMAT = '%d.%m.%YT%TZ'


config_filename = join("locals", 'tracker.ini')
del join


c = configparser.ConfigParser()
c.read(config_filename, encoding='utf-8')  # Maybe not required, optional.
if not c.has_section('main'):
    c.add_section('main')
c.set('main', 'requires_set_defaults', 'false')
with open(config_filename, 'w') as f:
    c.write(f)


files = [
    "worker.py",
    "config.py",
    "requirements.txt"
]


now = datetime.datetime.now


def set_defaults() -> NoReturn:
    global old_texts, firstly_edited, warns_info
    global started_at

    # Config some data

    old_texts = {
        fname: None for fname in files
    }

    firstly_edited = {
        fname: None for fname in files
    }

    warns_info = {
        fname: None for fname in files
    }

    # Config time of the track's beginning.
    # NOTE: This time changed when the tracker's code is "reloaded" via
    #       the worker function at `_write_files.py` or like that.
    started_at = now().strftime(TIME_FORMAT)


set_defaults()


w = tkinter.Tk()

# Config window
w.title("Tool to track changed files")

# Choose window type
window_type = [
    'common',
    '->common_window',  # same as 'common'
    'tool',
    'toolwindow',  # same as 'tool'
    'hidden'
]

# Should be changed when the respective changes at given types are done.
supported_types = {
    'common_window',
    'toolwindow',
    'hidden'
}

prefix = '->'

_possible_mode = filter(lambda item: item.startswith(prefix), window_type)
_possible_mode = list(_possible_mode)
if len(_possible_mode) == 1:
    mode = _possible_mode[0].lstrip(prefix)
elif not len(_possible_mode):
    raise SyntaxError("Choose at least one window type.")
else:
    raise SyntaxError("Choose not more than one window type.")

if mode == 'tool':
    mode = 'toolwindow'
elif mode == 'common':
    mode = 'common_window'

if mode not in supported_types:
    warnings.warn(
        "Unsupported mode of `window_type` passed. Treated as common."
    )

if mode == 'toolwindow':
    w.wm_attributes('-toolwindow', True)
    w.wm_attributes('-topmost', True)
elif mode == 'hidden':
    w.wm_attributes('-alpha', 0)
else:
    # Treated as mode 'common'.
    pass


# Buttons

buttons = {
    fname: None for fname in files
}

for fname in files:
    button_id = id(fname)
    fname = repr(fname)
    code = f"""
    text = "Tracking the file with name {fname}..."
    button_{button_id} = tkinter.Button(text=text)

    button = button_{button_id}

    def button_{button_id}_on_click():
        last_warned = warns_info[{fname}]
        
        if last_warned is None:
            msg = "File {fname} wasn't edited at root."
            info = msg
        else:
            f_edited = firstly_edited[{fname}]
            msg = r\"\"\"\
            f'''
            Firstly edited at {{f_edited}}. \\
            Last warned about the fact that \\
            "the file was edited" at {{last_warned}}.
            '''\"\"\"
            info = dedent(msg)
            info = eval(info).strip('\\n')

        detail = f"Started the track at {started_at}."
        mbox.showinfo("Edited info", info, detail=detail)

    command = lambda: button_{button_id}_on_click()
    button.config(command=command)
    button_{button_id}.pack()
    """
    code: str = dedent(code)
    exec(code, globals())
    del code  # It was quite big.

    fname = eval(fname)  # Go back from repr(...).

    s: tkinter.Button = eval(f"button_{button_id}")
    buttons[fname] = s


def _pre_script(fname) -> NoReturn:
    global old_texts, firstly_edited
    obj: Optional[tkinter.Button] = buttons[fname]

    old_text: Optional[bytes] = old_texts[fname]
    with open(fname, 'rb') as f:
        new_text: bytes = f.read()

    # Get variable value: of variable `requires_set_defaults`
    c.read(config_filename)
    try:
        requires_set_defaults: bool = c.getboolean('main', 'requires_set_defaults')
    except configparser.NoOptionError:
        requires_set_defaults = False

    if (
        # Means that `set_defaults()` is not required.
        not requires_set_defaults
        and
        # Means that this track of this file is *not* a first track.
        old_text is not None
        ):
        try:
            assert new_text == old_text
            old_texts[fname] = new_text
        except AssertionError:
            old_texts[fname] = new_text
            ctime = now()
            ptime = warns_info[fname]
            if ptime is None or \
            (ctime - ptime).total_seconds() > 60*5:
                warning_msg = \
                f"File {fname} has been just changed!"
                mbox.showwarning("Warning", warning_msg,
                    parent=obj  # optional
                )

                warns_info[fname] = ctime

            if firstly_edited[fname] is None:
                firstly_edited[fname] = ctime
    else:
        old_texts[fname] = new_text

    obj.after(100, lambda: _pre_script(fname))


_track = _pre_script


def _script() -> NoReturn:
    for fname in files:
        button_id = id(fname)
        code = f"""\
        func = lambda: _track({repr(fname)})
        button_{button_id}.after(0, func)
        """
        code: str = dedent(code)
        exec(code)


def _track_and_set_defaults() -> NoReturn:
    global requires_set_defaults
    global can_reload

    c.read(config_filename)
    if not c.has_section('main'):
        c.add_section('main')
    
    # Var. `can_reload` set.
    try:
        can_reload: bool = c.getboolean('main', 'can_reload')
    except configparser.NoOptionError:
        can_reload = False

    # Var. `requires_set_defaults` set and config.
    try:
        requires_set_defaults: bool = c.getboolean('main', 'requires_set_defaults')
    except configparser.NoOptionError:
        requires_set_defaults = False
        c.set('main', 'requires_set_defaults', 'false')
        with open(config_filename, 'w') as f:
            c.write(f)

    if requires_set_defaults and can_reload:
        set_defaults()
        requires_set_defaults = False

    w.after(100, _track_and_set_defaults)


# Set "cycles"
w.after(0, _script)
w.after(0, _track_and_set_defaults)

w.mainloop()
