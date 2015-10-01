#!/usr/bin/env python

'''	

Crawl Switches

Purpose: Starting at one switch, gather all of the mgmt ip addresses of all of its neighboring switches (and their neighbors)
Put those switches into a address_list

Requirements: One starting switch's mgmt ip as well as the username and password

Author: Lisa Roach

Date: 9/17/2015

'''


import getpass
from device import Device
import xmltodict
import re


def crawl_switches(username, password):

	ip_address = raw_input("Please enter your starting IP address: ")
	#username  = raw_input("Hostname: ")
	#password = getpass.getpass("Password: ")

	address_list = [ip_address]

	for address in address_list:

		switch = Device(ip=ip_address, username=username, password=password)
		switch.open()	

		address_list = next_ip(switch, address_list)
		return address_list
	
	#for i in address_list:
	#	print i

def next_ip(sw, addresses):

	getdata = sw.show('show lldp neighbors')		
		
	formatted_data = xmltodict.parse(getdata[1])
		
	rows = formatted_data['ins_api']['outputs']['output']['body']['TABLE_nbor']['ROW_nbor']

	for i in range(0, len(rows)):
		new_address = rows[i]['mgmt_addr']

		if new_address not in addresses and not re.search('[a-zA-Z]', new_address):
			addresses.append(new_address)

	return addresses

