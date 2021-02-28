import re

import requests


'''
# url = "https://anagram.poncy.ru/mask.html?inword=%25%D0%B0%25&answer_type=4"
def _url(letter, n):
	return "https://anagram.poncy.ru/mask.html?inword=" + letter \
	     + (n-1)*"*" + "&answer_type=4"

n = 2
url = _url('a', n)
print(url)

import requests

r = requests.get(url)
print(r.text)
'''

url = "https://loopy.ru/?word=a**&def="
# print(requests.get(url).text.replace('', ''))

r = requests.get(url)
t = r.text

base = re.finditer(r'<div class="wd">(?:.|\n)+?</div>', t)
base = list(base)

item = base[1].group()

def word(item):  # general
    return re.search(r'<h3>.+?значение слова (\w+).+?</h3>', item).group(1)

def meanings(item):
	return re.findall(r'<p>(.+?)</p>', item)

# print(item);
print(word(item))
print(meanings(item))

# Some results here were such:
# аб
# ['вода по-арабски', 'месяц еврейского календаря', 'июль у иудеев', 'департамент во Франции']