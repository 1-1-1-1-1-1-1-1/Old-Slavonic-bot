# ~

import os
from os import path
import re


seps = '(?:' + os.sep + '|' + os.altsep + ')'

curdir = path.abspath(os.curdir)
curdir0 = curdir
splitted = re.split(seps, curdir)


def go_higher():
	try:
		global curdir
		# nonlocal curdir
	except BaseException:
		pass
	curdir = path.abspath(path.dirname(curdir))
	os.chdir(curdir)  #?

while 'tokens.py' not in os.listdir():
	go_higher()


with open('tokens.py', encoding='utf-8') as f:
	lines = f.read().split('\n')

for line in lines:
	if 'TOKEN_INIT' in line:
		TOKEN = line.split('=', maxsplit=1)[1].strip()
		TOKEN = eval(TOKEN)
		break
else:
	raise Exception("Token not found.")

os.chdir(curdir0)

del os, path, re


bot = __import__("telebot").TeleBot(TOKEN)


...


bot.polling()
