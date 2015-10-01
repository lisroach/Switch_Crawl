#!/usr/bin/env python

'''
Call SQL SELECT statement to get the list of IPs from a database '''

import mysql.connector
from mysql.connector import errorcode
import getpass

def main():

	username = raw_input("Username: ")
	password = getpass.getpass("Password: ")
	try:
		cnx = mysql.connector.connect(host=<host ip>, database=<database>, user=username, password=password)
		cursor = cnx.cursor()

		query = ("SELECT <item> FROM <database>")

		cursor.execute(query)

		for ipv4_mgmt_net in cursor:
			print ipv4_mgmt_net

		cursor.close()
		cnx.close()

	except mysql.connector.Error as err:
  		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    			print("Something is wrong with your user name or password")

  		elif err.errno == errorcode.ER_BAD_DB_ERROR:
    			print("Database does not exist")

  		else:
    			print(err)
	else:
		cursor.close()
	  	cnx.close()

if __name__ == "__main__":
	main()
