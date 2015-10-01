Project: Neighbors
=======
Purpose:
-------
Discover all layer 1 (with LLDP) and Layer 3 (with BGP) neighbors in a topology.
Requirements: Starting management IP. 


Result:
---------
A file named "neighbors.txt" containing all LLDP and BGP neighbors

<LLDP>

current hostname:current mgmt_ip:local port:neighbor hostname:neighbor mgmt_ip:neighbor port

<BGP>

current mgmt_ip:AS:time up


Authors: 
--------
Darius Carrier & Lisa Roach


How to run: 
---------
python topology.py

You will be required to enter the username and password for your switches, as well as your initial switch mgmt ip address. 
It is assumed the username and password are consistent in the environment, but the script will crawl through all of your switches to find the connected management IP addresses. 

Contact info: 
----------
dacarrie@cisco.com

lisroach@cisco.com
