__author__ = "Darius Carrier"
#Credit: https://thepacketgeek.com/monitor-your-bgp-advertised-routes-with-paramiko/

import paramiko
import re
from time import sleep

def bgpcreation(crawler, f):
	### Please Enter the First Switch MGMT IP ###
	#switchIP= raw_input("Please Enter The First Switch MGMT IP: ")
	#Create the shell object
	#print "Made it to BGP"
	createtheGoods(crawler,f)

def createtheGoods(crawler, f):
	ssh= paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		ssh.connect(crawler.current_address, 22, crawler.username, crawler.password, 
			look_for_keys=False)
	except (paramiko.transport.socket.error,
        paramiko.transport.SSHException,
        paramiko.transport.socket.timeout,
        paramiko.auth_handler.AuthenticationException,
        paramiko.util.log_to_file("filename.log")):
		print 'Error connecting to SSH on %s' % crawler.current_address
		return None
	#print "I connected"
	shell = ssh.invoke_shell()
	shell.settimeout(3)
	bgpoutput = getL3(shell, '\nshow ip bgp summ | b Neigh\n')

	peer_ips = []
	test=[]
	for line in bgpoutput.split('\n'):
		#print line
		test= line.split()

	
	non_estab_states = 'neighbor|idle|active|Connect|OpenSent|OpenConfirm'
	for line in bgpoutput.split('\n'):
	    if bool(re.search(non_estab_states, line, re.IGNORECASE)):
	        continue
	    else:
	        ip_regex = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
	        peer_ips.extend(re.findall(ip_regex, line))
	#print peer_ips
	#if peer_ips:
		#f.write('[BGP]')
		#f.write('\n')
	for n in peer_ips:
		for line in bgpoutput.split('\n'):
			test= line.split()
			if test[0] == n:
				writetoFile(f,test)
	f.write('\n')	

def getL3(shell, command):
	shell.send(command.strip() + '\n')
	sleep(3)
 
	output = ''
	while (shell.recv_ready()):
		output += shell.recv(255)
 
	return output

def writetoFile(f,test):
	f.write(test[0]+":"+test[2]+":"+test[8])
	f.write('\n')