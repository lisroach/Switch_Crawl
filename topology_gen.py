#!/usr/bin/env python

'''
Create a network topology file with LLDP and BGP information

Outputted file name: neighbors.txt
Outputted file format:
<LLDP>
current hostname:current mgmt_ip:local port:neighbor hostname:neighbor mgmt_ip:neighbor port

<BGP>
current mgmt_ip:AS:time up


Authors: Lisa Roach and Darius Carrier

'''

__author__= 'Lisa Roach <lisroach@cisco.com>'
__version__='2.0'

import get_lldp
import sys
import getpass
import l3_scrape
from sql_grab import sql_grab
import switch_crawl
from Crawler import Crawler


def topology_generator():
	
	username = raw_input("Username: ")
	password = getpass.getpass("Password: ")

	try:
			
		with open('neighbors.txt', 'w') as working_file:

			#this will grab the ip addresses from a SQL database
			#address_list = sql_grab(username, password)

			ip_address = raw_input("Please enter your starting IP address: ")

			crawler = Crawler(ip_address, username, password)

			for address in crawler.address_list:
				crawler.update_address(address)
				address_list = get_lldp.get_switch(crawler, working_file)
				l3_scrape.bgpcreation(crawler, working_file)

			print "\nScript complete! Check the 'neighbors.txt' file that has been generated.\n"

	except IOError, e:
		print e

	except (KeyboardInterrupt, SystemExit):
		raise
	
	
if __name__ == "__main__":
	topology_generator()