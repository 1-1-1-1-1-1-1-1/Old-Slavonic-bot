import requests
from datetime import datetime  # logs


excs = []

def now(): return datetime.now()


def do_action(url):
    r = requests.get(url, proxies=proxy)  #!
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
            excs.append(i)
            # print(e)

if __name__ == '__main__':\
   # Tests... It can maybe help with opening the link with the allowed there IP.
    proxy = {
        "https": 'https://158.177.252.170:3128',
        "http": 'https://158.177.252.170:3128'
    }
    
    filename = '2.txt'
    def end_with():
        f.write("\n\nNumber of things where was an exception: "
                + str(excs)[1:-1] + "\n")
        f.write("Date of logging it: {} (by the time in UA).\n".format(
            now().strftime('%d.%m.%YT%H:%M:%S')))
    try:
        with open(filename, 'at', encoding='utf8') as f:
            # 22_500 is, maybe, an approximate number of a surely-max-number
            # word's ID on that page.
            f.write("\nDate of logging it: {} (by the time in UA).\n".format(
                now().strftime('%d.%m.%YT%H:%M:%S')))
            print('...!')  # test
            GO_TILL = 22_500
            for i in range(GO_TILL // 100 + 1):
                if i < 12:
                    continue
                f.write(f'[{100*i + 1}-{100*i + 100}]\n')
                main(range(100*i + 1, 100*i + 101), f)
                f.write('\n')
    except KeyboardInterrupt:
        None
    finally:
        end_with()
        raise SystemExit
