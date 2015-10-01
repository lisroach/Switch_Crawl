#!/usr/bin/env python

'''

Get the device relationships and add them to a file

Filename: neighbors.txt (file will be rewritten everytime script runs)
File format: <current_port> <hostname_neighbor> <neighbors_port>

'''
import xmltodict
import json
import sys
from device import Device
import paramiko
import re
from time import sleep


__author__ = "Lisa Roach <lisroach@cisco.com>"
__version__ = '2.0'


def show_lldp_neigh(sw, identity, f, ip):
    '''Add lldp neighbors information to file'''


    try:
        getdata = sw.show('show lldp neighbors')		
		
        formatted_data = xmltodict.parse(getdata[1])

        #print json.dumps(formatted_data, indent=2)
        rows = formatted_data['ins_api']['outputs']['output']['body']['TABLE_nbor']['ROW_nbor']

        f.write('\n----------------------------------------------\nSwitch: ' + 
            str(identity) + ' | MgmtIP: '+ ip + 
            '\n----------------------------------------------\n'+ '[LLDP]\n')
		
        for i in range(0, len(rows)):
			if str(rows[i]['mgmt_addr']) != "not advertised":
				f.write(rows[i]['l_port_id'] + ':')
				f.write(rows[i]['chassis_id'] + ':')
				f.write(rows[i]['port_id'] + '  \n')		
        #end of for loop 
        f.write('\n')

    except KeyError: #failed lookup
        print "There was an error with switch " + identity

def get_switch(ip_address, username, password, f):
    '''Open the switch, grab the hostname, and run show_lldp_neigh'''


    try:
        switch = Device(ip=ip_address, username=username, password=password)
        switch.open()	

        print ip_address
        xmlHostname = switch.show('show hostname')
        dictHostname = xmltodict.parse(xmlHostname[1])      
        hostname = dictHostname['ins_api']['outputs']['output']['body']['hostname']

        show_lldp_neigh(switch, hostname, f, ip_address)			

    except Exception: 
        print "Could not connect using NXAPI, trying a screenscrape..."
        screen_scrape(ip_address, username, password, f)


def screen_scrape(ip_address, username, password, f):


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip_address, 22, username, password, look_for_keys=False)

    except (paramiko.transport.socket.error,
        paramiko.transport.SSHException,
        paramiko.transport.socket.timeout,
        paramiko.auth_handler.AuthenticationException,
        paramiko.util.log_to_file("filename.log")):
        print 'Error connecting to SSH on %s' % ip_address
        return None
    
    shell = ssh.invoke_shell()
    shell.settimeout(3)

    print "Scraping...\n"

    lldp_output = scraper(shell, '\nshow lldp neighbor\n')
    hostname = scraper(shell, '\nshow hostname')

    write_to_file(lldp_output, f, ip_address, hostname)   


def scraper(shell, command):

    try:
        shell.send(command.strip() + '\n')
        sleep(3)

        output = ''
        stop = False

        while (shell.recv_ready()):
            output += shell.recv(255)

        return output

    except (KeyboardInterrupt, SystemExit):
        raise

def write_to_file(output, f, ip_address, hostname):

    counter = 0

    hostname =  hostname.split('\n')
    
    f.write('\n----------------------------------------------\nSwitch: ' 
        + hostname[1].rstrip() + ' | MgmtIP: ' + 
        ip_address + '\n----------------------------------------------\n' + 
        '[LLDP] \n')

    counter = 0

    for line in output.split('\n'):
        counter = counter + 1
        line = line.split()
        if counter >= 26 and len(line) == 5:
            new_string = line[1] + ":" + line[0] + ":" + line[4]
            f.write(new_string)     
            f.write('\n')
    f.write('\n')
