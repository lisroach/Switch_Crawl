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
from Crawler import Crawler


def topology_generator():
    '''Creates the Crawler object and calls all the functions to fill a file with the information.'''

    username = raw_input("Username: ")
    password = getpass.getpass("Password: ")

    try:
			
        with open('neighbors.txt', 'w') as working_file:
            ip_address = raw_input("Please enter your starting IP address: ")

            crawler = Crawler(ip_address, username, password)

            for address in crawler.address_list:
                crawler.update_address(address)
                err_flag = get_lldp.get_switch(crawler, working_file)
                if not err_flag:
                	l3_scrape.bgpcreation(crawler, working_file)

            print "\nScript complete! Check the 'neighbors.txt' file that has been generated.\n"

    except IOError, e:
        print e

    except (KeyboardInterrupt, SystemExit):
        raise

if __name__ == "__main__":
    topology_generator()
