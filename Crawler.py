#!/usr/bin/env python

__author__ = "Lisa Roach <lisroach@cisco.com>"
__version__ = '1.0'


class Crawler():
    '''Holds all the properties of the switch crawler'''

    def __init__(self, current_address, username, password):
        self.current_address = current_address
        self.username = username
        self.password = password
        self.address_list = [current_address]
        self.hostname = "None"

    def extend_ips(self, new_addresses):
        self.address_list.extend(x for x in new_addresses if x not in self.address_list)

    def update_address(self, address):
        self.current_address = address

    def update_hostname(self, new_hostname):
        self.hostname = new_hostname
