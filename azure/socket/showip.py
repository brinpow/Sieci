#!/bin/python3

import sys
import socket

for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(sys.argv[1],None,socket.AF_UNSPEC,socket.SOCK_STREAM):
	print(family,': ',sockaddr)
