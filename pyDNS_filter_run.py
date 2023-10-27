#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib import reload
import time, pyDNS_filter

server = pyDNS_filter.Server()
while True:
	try:
		server.run()
	except (KeyboardInterrupt, Exception) as e:
		if "Permission denied" in str(e):
			print("Probably need sudo for port below 1000 like DNS is..")
		print("\r\n--------------------------------------------------------\n "+\
			  "QUIT? ('y' to QUIT, or just hit ENTER to RELOAD)")
		x = input("[quit] ")
		if x.lower() == 'y' or x.lower() == 'yes':
			break
		else:
			server.running = False
			time.sleep(1)
			print("\r\n\r\n ******* SERVER RELOADING! ******* \r\n")
			reload(pyDNS_filter)
			old = server
			server = pyDNS_filter.Server()
			continue
server.running = False
