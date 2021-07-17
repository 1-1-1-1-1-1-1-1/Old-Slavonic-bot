# -*- coding: utf-8 -*-
# Tool to write files of the exact version to the root.
# Requires `argparse`. Can install via `pip install argparse` on Windows.


import os

import argparse


filename = os.path.split(__file__)[-1]


def _script(v_name=None, files=[]):
    assert files
    if not v_name:
        help_message = f"""Usage:
One of
    '{filename} library',
    'python {filename} library'

Writes files {', '.join(files)} to the root folder.
    """
        parser = argparse.ArgumentParser(description=help_message)
        parser.add_argument('v_name', type=str, help='Name of library')
        args = parser.parse_args()
        v_name = args.v_name

    print(f"Writing with version: {v_name}")
    
    path_0 = os.path.abspath(os.curdir)
    folder = os.path.join('meta', 'versions-controll')
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
    os.chdir(path_0); del path_0
    for file in files:
        name, ext = os.path.splitext(file)
        mod_file = name + '-' + v_name + ext
        with open(os.path.join(path, mod_file), encoding='utf-8') as f:
            data = f.read()
        with open(file, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"\tWrote file {file} at root")

    current_version_fname = 'current-version.txt'  # CURRENT_VERSION
    with open(current_version_fname, encoding='utf-8') as f:
        started = False
        lines: list = []  # of integer numbers
        # `lines` is a list of possible lines (here: =their indexes) to change
        i = 0
        while True:
            line = f.readline()
            if line.startswith(".. version"):
                started = True  # Search started
            elif line.lstrip('\t\f ') != line or not line.rstrip('\n'):
                lines.append(i)
            elif started:
                break
            i += 1
    with open(current_version_fname, encoding='utf-8') as f:
        data = f.readlines()

    # Open just written file, find version's full name
    with open('worker.py', encoding='utf-8') as f:
        index = 0
        while index < 3:
            line = f.readline()
            part = '# version:'
            if line.startswith(part):
                full_name = line.split(part)[1].strip()
                break
            index += 1
        else:
            full_name = ':'.join(
                (
                    v_name,
                    "undefined"
                    )
                )

    library = v_name

    with open('meta/versions-about.py', encoding='utf-8') as f:
        exec(f.read(), globals())
        name = '-'.join(filter(lambda i: i, parse_version(full_name)[1:]))
 
    for i in lines:
        if (str_ := ':type:') in data[i]:
            j = data[i].index(str_) + len(str_)
            data[i] = data[i][:j] + ' at ' + library
            data[i] += '\n'
        elif (str_ := ':name:') in data[i]:
            j = data[i].index(str_) + len(str_)
            data[i] = data[i][:j] + ' ' + name
            data[i] += '\n'
    
    with open(current_version_fname, 'w', encoding='utf-8') as f:
        f.write(''.join(data))
        print(f"Wrote to file {current_version_fname}.")

    print("Ready")


if __name__ == '__main__':
    files = [
        "config.py",
        "worker.py",
        "requirements.txt"
    ]
    _script("aiogram", files)
    raise SystemExit
    _script(None, files)
