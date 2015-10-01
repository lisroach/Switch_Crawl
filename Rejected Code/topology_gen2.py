#!/usr/bin/env python

'''
Create a network topology with LLDP and BGP information

There are three different ways to run it: 
	1. Start with a file of all your mgmtIPs
	2. Grab the mgmtIPs from a SQL database
	3. Give a starting switch and crawl for all mgmt IPs from its neighbors
Just uncomment the section you want to use and comment the ones you do not. 

Authors: Lisa Roach and Darius Carrier

'''

__author__= 'Lisa Roach <lisroach@cisco.com'
__version__='2.0'

import get_lldp
import sys
import getpass
import l3_scrape
from sql_grab import sql_grab
import switch_crawl


def main():
	
	username = raw_input("Username: ")
	password = getpass.getpass("Password: ")

	
	#This will grab the ip addresses from a file
	'''try:
		read_file = "mgmt_ips.txt"
		working_file = open('neighbors.txt', 'w')
		with open(read_file, 'r') as fp:	#with will close file
			for address in fp:
				address = address.rstrip()
				address = address.replace("'", "")
				if address:
					get_lldp.get_switch(str(address), username, password, working_file)
					l3_scrape.bgpcreation(username, password, working_file, address)
	
	except IOError, e:
		print e

	'''
	try:
			
		with open('neighbors.txt', 'w') as working_file:

			#this will grab the ip addresses from a SQL database
			#address_list = sql_grab(username, password)

			ip_address = raw_input("Please enter your starting IP address: ")

			address_list = [ip_address]
			new_addresses = []

			for address in address_list:
				address_list = get_lldp.get_switch(address, username, password, working_file, 
					address_list)
				l3_scrape.bgpcreation(username, password, working_file, address)
				print address_list


			print "\nScript complete! Check the 'neighbors.txt' file that has been generated.\n"

	except IOError, e:
		print e

	except (KeyboardInterrupt, SystemExit):
		raise
	
	
if __name__ == "__main__":
	main()