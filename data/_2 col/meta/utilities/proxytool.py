import re
from time import time

import requests


__all__ = [
# Imports:
're', 'time', 'requests',
# Other
'url', 'form_data', 'get_pre_proxies',
'filter_by', '_proxies',
'get_it', 'optimal_0', 'optimal'
]


url = "https://free-proxy-list.net/"


def form_data(line):
    _data = re.findall('<td.*?>(.*?)</td>', line)
    return _data


def get_pre_proxies(maxn=10, filter_by=None):
    r = requests.get(url)
    text = r.text
    pattern = r'tr((?:.|\n)*?)</tr>'
    items = re.findall(pattern, text)
    res = []
    while items and len(res) < maxn:
        item = items.pop(0)
        # print(item)
        if 'Ukraine' not in item:
            item_data = form_data(item)
            if not item_data:
                continue
            if filter_by:
                if not all(filter_by[i](item_data[i])
                       for i in range(len(item_data))
                       ):
                    continue
            res.append(item_data)

        '''

            ## .. item_data = form_data(item)
            if item_data:
                # if 'second' in item_data[-1]:
                    res.append(item_data)
            # if (sec := int(item_data[-1].split()[0])) <= 30: ...
        '''
        # return [item for item in items[:maxn] if 'Ukraine' not in item]
    return res


filter_by = [lambda _: True]*3 + [lambda s: s != 'Ukraine'] + [lambda _: True]*4

_proxies = lambda n: [tuple(item[:2]) for item in get_pre_proxies(n, filter_by)]


def get_it(skip_items=[]):
    tm = 0.3  # 0.7
    lst = _proxies(300)
    t = tm + 1
    while lst and t >= tm:
        item = lst.pop(0)
        if item in skip_items:
            continue
        proxy = {'http': 'http://{}:{}'.format(*item)}
        t0 = time()
        try:
            r = requests.get(url, proxies=proxy)
        except:
            continue
        if r.status_code != 200:
            continue
        t = time() - t0
        print(...)
    return item, t


# Deprecated?
def optimal_0():  
    res = []
    while True:
        try:
            res.append(get_it([item[0] for item in res]))
        except:
            break
    if not res:
        pass
    else:
        return sorted(res, key=lambda item: item[1])[0]

def optimal(tm, maxt, *, maxst=None):
    """Return a list of ((proxy_IP, proxy_PORT), seconds), sorted by
    seconds, where seconds <= maxt, not more than `maxt` such items.

    Note: this list is formed as a list of proxies, with which a prog.
    worked fast.

    maxst: !
    """
    lst = _proxies(300)
    res = []
    for item in lst:
        proxies = {'http': 'http://{}:{}'.format(*item)}
        t0 = time()
        try:
            r = requests.get(url, proxies=proxies)
        except:
            continue
        if r.status_code != 200:
            continue
        t = time() - t0
        if t <= tm and re.fullmatch(r'[\d\.]+', item[0]):
            res.append((item, t))
        if maxst and len(res) == maxst:
            break
    return sorted(res, key=lambda item: item[1])[:maxt]

if __name__ == '__main__':
    # main()
    print(optimal(0.7, 1)[0])
