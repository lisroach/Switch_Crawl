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


def show_lldp_neigh(sw, identity, f, ip, addresses):
    '''Add lldp neighbors information to file'''

    try:
        getdata = sw.show('show lldp neighbors')		
		
        formatted_data = xmltodict.parse(getdata[1])

        #print json.dumps(formatted_data, indent=2)
        rows = formatted_data['ins_api']['outputs']['output']['body']['TABLE_nbor']['ROW_nbor']
        f.write('[Switch: ' + str(identity) + ' | MgmtIP: '+ ip + '] \n' + '[LLDP] \n')

        for i in range(0, len(rows)):
            if str(rows[i]['mgmt_addr']) != "not advertised":
                f.write(rows[i]['l_port_id'] + ':')
                f.write(rows[i]['chassis_id'] + ':')
                f.write(rows[i]['port_id'] + '  \n')
                new_address = rows[i]['mgmt_addr']
                if new_address not in addresses and not re.search('[a-zA-Z]', new_address):
                    addresses.append(new_address)
        #end of for loop 
        f.write('\n')

        return addresses

    except KeyError: #failed lookup
        print "There was an error with switch " + identity

def get_switch(ip_address, username, password, f, addresses):
    '''Open the switch, grab the hostname, and run show_lldp_neigh'''
    
    #ip_address = '10.200.96.32'

    try:
        switch = Device(ip=ip_address, username=username, password=password)
        switch.open()	

        #print ip_address
        xmlHostname = switch.show('show hostname')
        dictHostname = xmltodict.parse(xmlHostname[1])      
        hostname = dictHostname['ins_api']['outputs']['output']['body']['hostname']

        addresses = show_lldp_neigh(switch, hostname, f, ip_address, addresses)			
        return addresses

    except Exception: 
        print "Could not connect using NXAPI, trying a screenscrape..."
        addresses = screen_scrape(ip_address, username, password, f, addresses)
        return addresses


def screen_scrape(ip_address, username, password, f, addresses):


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
    
    shell = ssh.invoke_shell(height=3000)
    shell.settimeout(3)

    print "Scraping...\n"

    lldp_output = scraper(shell, '\nshow lldp neighbors detail\n')

    mgmt_ip = write_to_file(lldp_output, f, ip_address)   
    return mgmt_ip

def scraper(shell, command):

    try:
        shell.send(command.strip() + '\n')
        sleep(3)

        output = ''
        stop = False

        while (shell.recv_ready() and not re.search(r'(Total entries displayed:)', output)):
            output += shell.recv(1024)
            #shell.send('\n')
            #sleep(0.5)

        #print output

        return output

    except (KeyboardInterrupt, SystemExit):
        raise

def write_to_file(output, f, ip_address):

    
    f.write('\n[Switch: ' + ' | MgmtIP: ' + ip_address + '] \n' + '[LLDP] \n')
    data = []

    for line in output.split('\n'):
        #print line 

        if len(data) is 3:               
            new_string = data[0].rstrip() + ":" +  data[1].rstrip() + ":" + data[2].rstrip()
            if "not adverstised" not in new_string:
                f.write(new_string)
                f.write('\n')
            del data[:]

        res = re.match(r'(^Local Port id:\s(.*))', line)
        if res and str(res.group(2)) != "not advertised":
            data.insert(0, res.group(2))            

        res = re.match(r'(^System Name:\s(.*))', line)
        if res and str(res.group(2)) != "not advertised":
            data.insert(1, res.group(2))

        res = re.match(r'(^Port id:\s(.*))', line)
        if res and str(res.group(2)) != "not advertised":
            data.insert(2, res.group(2))

        res = re.match(r'(^Managment IP:\s(.*))', line)
        if res and str(res.group(2)) != "not advertised":
            return res
