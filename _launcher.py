# Util to help the bot being launched.
# ============================================================================
# Required:
#  - Tk/tcl (tkinter),
#  - bot.env with APP_NAME=<APP_NAME> (insert name at the place of <APP_NAME>).


from datetime import datetime, timedelta
try:
    import tkinter
except ImportError:
    raise SystemExit("""No `tkinter` module found. Exiting.
------------------------------------------------------------------------------
NOTE: Consider this error may be caused by the impossibility of this module's
existing in the Python's lib on your OS.  This code may work partially still
without the tkinter module, only with limited responsibilities.  Try commenting
some lines/code parts (required the `tkinter`) and launch the app again.""")
import os
import re
import json
from typing import NoReturn
import subprocess
from tkinter import Tk, Button, Checkbutton, Frame, Label
from tkinter import BooleanVar
import tkinter.messagebox as mbox

import configparser

from globalconfig import load_env, get


load_env('bot')


DATA = os.path.join("locals", "_launcher.ini")
RUN = "worker.py"
APP_NAME = get('APP_NAME')
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


WORKTIME_SCHEDULE = {
    'Mon': ('8:30', '22:00'),
    'Thu': ('10:00', '22:00'),
    'Sun': ('10:00', '22:00'),
    'Sat': ('18:00', '21:00')
}


c = configparser.ConfigParser()
c.read(DATA)


def set_defaults(section='meta') -> NoReturn:
    if section == 'meta':
        c.set('meta', 'dyno', '')
        c.set('meta', 'time',
            datetime(1, 1, 1, 0, 0, 0).strftime(TIME_FORMAT))
    else:
        NotImplemented
    with open(DATA, 'w') as f:
        c.write(f)


if not c.has_section('meta') or not c.has_option('section', 'dyno'):
    if not c.has_section('meta'):
        c.add_section('meta')
    set_defaults()
if not c.has_section('dynos'):
    c.add_section('dynos')
if not c.has_option('dynos', 'init'):
    c.set('dynos', 'init', '[]')
with open(DATA, 'w') as f:
    c.write(f)


def stop_prev(dyno: str) -> NoReturn:
    """Run command to stop previous dyno, return None."""
    if not dyno:
        return
    cmd = f"heroku stop {dyno} -a {APP_NAME}"
    os.system(cmd)


def get_p(command) -> subprocess.Popen:
    p = subprocess.Popen(
        command, universal_newlines=True, 
        shell=True, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    return p


def info_json() -> dict:
    """Return the info about app, from data in json."""
    command = f"heroku apps:info {APP_NAME} --json"

    p = get_p(command)
    text = p.stdout.read()

    if not text:
        # Output is empty.
        data = {}
        return data
    
    text_data = json.loads(text)

    return text_data


def prev_data() -> dict:
    assert c.has_section('meta')
    dyno: str = c['meta']['dyno']
    time: str = c.get('meta', 'time')
    time: datetime = datetime.strptime(time, TIME_FORMAT)
    result = {
        'dyno': dyno,
        'time': time
    }
    return result


def update(case=None, space=None) -> dict:
    if case is None:
        case = "all_dynos[-1] != name"
    delta = datetime.now() - datetime.utcnow()
    data = info_json().get('dynos')
    if data:
        data = data[0]
        t0_string: str = data["created_at"]
        t0: datetime = datetime.strptime(t0_string, TIME_FORMAT)
        t0 += delta
        name = data['name']
    else:
        d = prev_data()
        t0, name = d['time'], d['dyno']  # set_defaults()
    d = {
        'time': t0,
        'dyno': name
    }

    c['meta']['dyno'] = name
    c['meta']['time'] = t0.strftime(TIME_FORMAT)
    all_dynos = eval(c['dynos']['init'])
    add_space = space if space else {}
    space = locals()
    space.update(add_space)
    if name and eval(case, None, space):
        all_dynos.append(name)
        c['dynos']['init'] = str(all_dynos)

    with open(DATA, 'w') as f:
        c.write(f)

    return d


def launch(stop=True) -> subprocess.Popen:
    """Launch the app via cmd, stopping previous is required."""
    if stop:
        dyno = prev_data()['dyno']
        stop_prev(dyno)
    cmd = f"heroku run:detached python {RUN} -a {APP_NAME}"
    p = get_p(cmd)
    return p


def work() -> NoReturn:
    pdata = prev_data()
    dyno = pdata['dyno']
    t0 = pdata['time']
    now = datetime.now()
    print('[', now.isoformat(), '] ', sep='', end='')  # Test
    delta = now - t0
    delta = delta.total_seconds()

    def is_at_worktime(obj: datetime) -> bool:
        schedule = WORKTIME_SCHEDULE
        for k in schedule:
            schedule[k] = tuple(map(int, schedule[k].split(':')))
        for k in ('Tue', 'Wed', 'Fri'):
            schedule[k] = schedule['Mon']
        day = obj.strftime('%a')
        time = schedule[day]
        current_time = tuple(map(int, obj.strftime("%H:%M").split(':')))
        return time[0] <= current_time <= time[1]
    
    if dyno and t0 >= now + timedelta(hours=2):
        cases: tuple = (
            delta > 22 * 3600,
            is_atworktime(t0 + timedelta(days=1, hours=-2)),
            is_atworktime(t0 + timedelta(hours=2))
        )
        if not all(cases):
            stop_prev(dyno)

    p_launched = launch(stop=False)
    retcode = p_launched.wait()
    print(retcode)  # Test
    update(case="retcode == 0", space={'retcode': retcode})


# =============
# --- window


window = Tk()
window.title(f'Launcher for the bot: app {APP_NAME}')

field_1 = Frame(window)
field_1.pack()

button = Button(field_1, text="Launch", width=27, height=1)
button.pack(side='left')

v1 = BooleanVar(value=False)

qo_stop_prev = Checkbutton(
    field_1, text='Останавливать предыдущего '
    'dyno перед запуском кнопкой',
    variable=v1
)
qo_stop_prev.pack(side='left')

other = Frame(window)
other.pack()

label = Label(other, text="")


def config_label(repeat=True) -> NoReturn:
    dyno = update()['dyno']
    if not dyno: dyno = repr(None)
    wait_for = 120  # seconds
    label['text'] = f"Последний работавший dyno \
(обновление внесено не более чем {wait_for} сек. назад): {dyno}"
    if repeat:
        label.after(wait_for*1_000, config_label)


config_label()
label.pack()


def relaunch() -> NoReturn:
    value = v1.get()
    p = launch(stop=value)
    a = "not touched" if not value else "stopped"
    c = str(p.wait())
    update()
    config_label(repeat=False)
    
    mbox.showinfo("info", f"RESULT UPDATED (to check). Launched \
(previous dyno: {a}). \
Status code: {c}.")


button['command'] = relaunch


def loop_launcher() -> NoReturn:
    work()
    config_label(repeat=False)
    _ms = datetime.now() - prev_data()['time']
    ms = 3_600_000 - _ms.total_seconds()
    ms = max(0, int(ms))
    window.after(ms, loop_launcher)


window.after(0, loop_launcher)

extra = Frame(window)
extra.pack()

quit_button = Button(extra, text="Quit (выход)", command=window.destroy)
quit_button.pack()

window.mainloop()
