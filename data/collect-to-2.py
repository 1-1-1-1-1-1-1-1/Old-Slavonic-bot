# Use this script to collect data from _2' files to the single file, adding
# there extra info (date of logging, maybe etc.).


from os.path import join

import configparser


meta_filename = 'pre-2-meta.ini'

to_filename = 'pre-for-2.txt'


def main():
	c = configparser.ConfigParser()
	c.read(join('_2 col', 'meta', meta_filename))

	with open(to_filename, 'at', encoding='utf-8') as f:
		import datetime
		now = datetime.datetime.now
		f.write(f'\n[{now().strftime("%Y-%m-%dT%H:%M:%S")}] Logging this.\n\n')
		del datetime, now

	for i in eval(c['verified']['all']):
		with open(join('_2 col', 'files', 'init', str(i) + '.txt'),
			encoding='utf-8') as f:
			text = f.read().split('-'*7)[1].strip('\n')
		with open(to_filename, 'at', encoding='utf-8') as f:
			f.write('\n')
			f.write(text)
			f.write('\n'*2)

if __name__ == '__main__':
	main()
