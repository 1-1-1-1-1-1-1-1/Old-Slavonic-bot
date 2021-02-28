"""That's a script for collecting words from `url` at the file."""

import configparser
import requests
from datetime import datetime  # logs
from os.path import join

from tkinter.messagebox import showerror, showinfo


# --- Section `helpers`
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'  # For logging


meta_c = configparser.ConfigParser()

metaconfig = join('meta', 'metaconfig.ini')
meta_c.read(metaconfig)

WRITE_TO_FOLDER = eval(meta_c['init']['WRITE_TO_FOLDER'])

# IP, PORT = '46.21.153.16', '3128'  #
# IP, PORT = '158.140.167.148', '53281'  # On the clock: 2:59.
# Can try:
# IP, PORT = '34.101.171.117', '80'

#? IP, PORT = "158.177.252.170", "3128"
# IP, PORT = '62.23.15.92', '3128'

IP, PORT = (
    '150.239.65.206', '3128'
    )


from time import time


if not meta_c.has_section('proxy'):
    meta_c.add_section('proxy')

c = meta_c  #~

'''
try:
    assert c.getfloat('proxy', 'last_update') <= time() + 60*3  #~
    _proxies = eval(meta_c.get('proxy', 'current'))
    assert _proxies
    proxies = _proxies.pop(0)
    c['proxy']['current'] = str(_proxies)

except (AssertionError, Exception):
#     assert not c.has_option('proxy', 'last_update') or \
# (c.has_option('proxy', 'last_update') \
# and )

    from meta.utilities.proxytool import optimal

    tm_default = 0.3
    if c.has_option('proxy', 'tm'):
        tm = c.getfloat('proxy', 'tm')
    else:
        tm = tm_default
    delta_plus = 0.1
    delta_minus = 0.01
    maxt = 3
    __proxies = optimal(tm, maxt)
    if not __proxies:
        raise Exception("Fatal error")
    proxies = __proxies.pop(0)
    c['proxy']['current'] = str(__proxies)
    # _proxies = c['proxy']['current']
    meta_c.set('proxy', 'last_update', str(time()))
    if len(__proxies) >= min(maxt - 1, 7):
        tm = max(tm_default, tm - delta_minus)
    else:
        tm += delta_plus
    c['proxy']['tm'] = str(tm)
    

with open(metaconfig, 'w', encoding='utf-8') as f:
    c.write(f)

del c; IP, PORT = proxies[0]  #~
print(IP, PORT, type(IP))  # t
'''

# It can maybe help with opening the link with the allowed there IP.

# use_proxy = meta_c.getboolean('init', 'use_proxy')
try:
    use_proxy = meta_c.getboolean('proxy', 'use_proxy')
except:
    use_proxy = False

proxy = {
    'http': 'http://{}:{}'.format(IP, PORT)
} if use_proxy else {}

excs = []


def now(): return datetime.now()


# --- Section `functions`

def do_action(url):
    r = requests.get(url, proxies=proxy)
    if (s := r.status_code) != 200:  #! See:
        print(s); showerror("Error", "s: " + str(s))
        raise SystemExit
    lines = r.text.splitlines()
    del r
    i = 0
    while 'Перевод:' not in lines[i]:
    	i += 1
    t1 = lines[i+1]
    t1 = t1[:t1.index('<')].strip()
    while 'Транскрипция:' not in lines[i]:
    	i += 1
    t2 = lines[i+1]
    t2 = t2[:t2.index('<')].strip()
    return t1, t2


# Internal.
# def is_lower(s): return s.lower() == s

def main(iterable, f):
    global excs
    for i in iterable:
        url = 'http://www.orthodic.org/word/{}'.format(i)
        # Mind the newlines here!
        try:
            translation, word = do_action(url)
            translation = translation.replace("&quot;", '"')
            
            f.write("{word} --- {translation}\n".format(word=word,
                                                        translation=translation))
        except Exception as e:
            print(e)
            excs.append(i)
            raise SystemExit


if __name__ == '__main__':
    c = configparser.ConfigParser()
    
    # file_logs = 'pre-2-logs.txt'
    file_metadata = join("meta", "pre-2-meta.ini")
    # folder = "."
    folder = WRITE_TO_FOLDER

    c.read(file_metadata)
    
    # 22_500 is, maybe, an approximate number of a surely-max-number
    # word's ID on that page.
    GO_TILL = 22_500

    def write_config():
        with open(file_metadata, 'w', encoding='utf-8') as g:
            c.write(g)

    def start_writing():
        c[section]["logging_started"] = logging_started
        write_config()

    logging_ended = None  # time: either `None` or str.
    def end_with():
        f.write('\n\n-------')
        f.write("\nNumber of things where an exception was: "
                + str(excs)[1:-1] + "\n")
        f.write("Date of logging it: {} (by the time in UA).\n".format(
            logging_ended))
        c[section]["logging_ended"] = str(logging_ended)

    def ctime(): return now().strftime(DATE_FORMAT)

    for i in range(GO_TILL // 100 + 2):
        if i in [221, 222]:  #tmp
            continue
        if c.has_section('verified') and i in eval(c.get('verified', 'all')):
            print(f"[{ctime()}] Skipping `i={i}`, already at the file.")
            continue
        print(f"[{ctime()}] Starting the action with `i={i}`.")

        section = str(i)
        if not c.has_section(section):
            c.add_section(section)

        filename = '{}.txt'.format(i)

        with open(join(folder, filename), 'w', encoding='utf8') as f:
            try:
                logging_started = ctime()
                start_writing()
                f.write("Date of logging it: {} (by the time in UA).\n".format(
                    logging_started))
                f.write('-------\n')  # Pre-data (same as `introduction`)

                f.write(f'[{100*i + 1}-{100*i + 100}]\n')  # header

                main(range(100*i + 1, 100*i + 101), f)

                logging_ended = ctime()
                end_with()
                c[section]["logging_ended"] = logging_ended
                c[section]["excs"] = str(excs)

                if not c.has_section('verified'):
                    c.add_section('verified')
                if not c.has_option('verified', 'all'):
                    c['verified']['all'] = '[]'
                iterable = c['verified']['all']
                iterable = list(eval(iterable))
                iterable.append(i)
                iterable.sort()
                iterable = str(iterable).replace(' ', '\n')
                iterable = iterable.replace('[', '[\n')
                iterable = iterable.replace(']', '\n]')
                c['verified']['all'] = iterable
                write_config()
                print(f"[{ctime()}] Ended writing to file with i={i}. Verified.")

                excs = []

            except KeyboardInterrupt:
                end_with()
                print(f"[{ctime()}] Interrupted. i: " + str(i) + '.')
                raise SystemExit
    
    print(f"[{ctime()}] Done with all!")

    showinfo("Done", "Parsed all requested.")

    # NOTES: to <= 5 : ?
    # FURTHER NOTES: and after 5 till ~150 : ?
