#!/usr/bin/env python

'''
Call SQL SELECT statement to get the list of IPs from a database '''

__author__= "Lisa Roach <lisroach@cisco.com>"
__version__ ='1.0'

import mysql.connector
from mysql.connector import errorcode
import getpass

def sql_grab(username, password):

	#username = raw_input("Username: ")
	#password = getpass.getpass("Password: ")
	try:
		cnx = mysql.connector.connect(host='10.200.96.4', database='lab_ip_address', user='dba', password='dba')
		cursor = cnx.cursor()

		query = ("SELECT ipv4_mgmt_net FROM lab_ip_address.ip_address_list")

		cursor.execute(query)

		mgmt_list = [] 

		for ipv4_mgmt_net in cursor:
			s = str(ipv4_mgmt_net)
			new_s = s.replace("(u'", '')
			new_s = new_s.replace("',)", '')
			mgmt_list.append(new_s)

		return mgmt_list

		cursor.close()
		cnx.close()

	except mysql.connector.Error as err:
  		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    			print("Something is wrong with your database user name or password")

  		elif err.errno == errorcode.ER_BAD_DB_ERROR:
    			print("Database does not exist")

  		else:
    			print(err)
	else:
		cursor.close()
	  	cnx.close()