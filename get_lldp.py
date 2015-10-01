#!/usr/bin/env python

'''
Get the device relationships and add them to a file.

Filename: neighbors.txt (file will be rewritten everytime script runs)
File format: current hostname:current mgmt_ip:local port:neighbor hostname:neighbor mgmt_ip:neighbor port

'''

import xmltodict
import json
import sys
from device import Device
import paramiko
import re
from time import sleep
from Crawler import Crawler


__author__ = "Lisa Roach <lisroach@cisco.com>"
__version__ = '3.0'


def show_lldp_neigh(sw, crawler, f):
    '''Add lldp neighbors information to file'''

    try:
        getdata = sw.show('show lldp neighbors')	
        formatted_data = xmltodict.parse(getdata[1])

        new_address_list = []
        rows = formatted_data['ins_api']['outputs']['output']['body']['TABLE_nbor']['ROW_nbor']

        for i in range(0, len(rows)):
            new_address = rows[i]['mgmt_addr']
            if str(new_address) != "not advertised":
                f.write(crawler.hostname + ':' + sw.ip + ':')
                f.write(rows[i]['l_port_id'] + ':')
                f.write(rows[i]['chassis_id'] + ':')
                f.write(rows[i]['mgmt_addr'] + ':')
                f.write(rows[i]['port_id'] + '  \n')
                if not re.search('[a-zA-Z]', new_address):
                    new_address_list.append(rows[i]['mgmt_addr'])

        f.write('\n')
        crawler.extend_ips(new_address_list)

    except KeyError, e:
        print "There was an error with switch " + crawler.hostname + "Error: " + e


def get_switch(crawler, f):
    '''Open the switch, grab the hostname, and run show_lldp_neigh'''

    try:
        switch = Device(ip=crawler.current_address, username=crawler.username,
                        password=crawler.password)
        switch.open()

        print crawler.current_address
        xmlHostname = switch.show('show hostname')
        dictHostname = xmltodict.parse(xmlHostname[1])
        crawler.update_hostname(dictHostname['ins_api']['outputs']['output']['body']['hostname'])     

        show_lldp_neigh(switch, crawler, f)	

    except Exception, e:
        print "Could not connect using NXAPI, trying a screenscrape..."
        screen_scrape(crawler, f)


def screen_scrape(crawler, f):
    '''Open the scraper and call functions to write output to file.'''

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(crawler.current_address, 22, crawler.username, crawler.password, look_for_keys=False)

    except (paramiko.transport.socket.error,
            paramiko.transport.SSHException,
            paramiko.transport.socket.timeout,
            paramiko.auth_handler.AuthenticationException,
            paramiko.util.log_to_file("filename.log")):
        print 'Error connecting to SSH on %s' % crawler.current_address
        return None

    shell = ssh.invoke_shell(height=3000)
    shell.settimeout(3)

    print "Scraping..."

    lldp_output = scraper(shell, '\nshow lldp neighbors detail\n')

    hostname_output = scraper(shell, '\nshow hostname\n')
    hostname =  hostname_output.split('\n')
    crawler.update_hostname(hostname[1].strip())

    write_to_file(lldp_output, f, crawler)


def scraper(shell, command):

    try:
        shell.send(command.strip() + '\n')
        sleep(3)
        output = ''
        stop = False

        while (shell.recv_ready() and not re.search(r'(Total entries displayed:)', output)):
            output += shell.recv(1024)

        return output

    except (KeyboardInterrupt, SystemExit):
        raise

def write_to_file(output, f, crawler):

    try:

        data = []

        for line in output.split('\n'):
            if len(data) is 3:               
                new_string = data[0].strip() + ":" + data[1].strip() + ":" + data[2].strip()
                if "not advertised" not in new_string.strip():
                    f.write(crawler.hostname + ':' + crawler.current_address + ":")
                    f.write(new_string)
                    f.write('\n')
                del data[:]

            res = re.match(r'(^Local Port id:\s(.*))', line)
            if res:
                data.insert(0, res.group(2))          

            res = re.match(r'(^System Name:\s(.*))', line)
            if res:
                data.insert(1, res.group(2))

            res = re.match(r'(^Port id:\s(.*))', line)
            if res:
                data.insert(2, res.group(2))

            res = re.match(r'(^Managment IP:\s(.*))', line)
            if res and str(res.group(2).strip()) != "not advertised":
                crawler.extend_ips(list(res))

        f.write('\n')

    except Exception, e:
        print "You experienced the following exception when writing to file: ", e
        sys.exit()
