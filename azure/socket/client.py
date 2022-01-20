#!/bin/python3

import socket
import sys

PORT = 3490
BUFFOR_SIZE = 1000

if len(sys.argv)!=2:
    print("usage: talker hostname")
    exit(1)

for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(sys.argv[1],PORT,socket.AF_UNSPEC,socket.SOCK_STREAM):
	sockfd = socket.socket(family,type,proto)
	if sockfd is None:
		continue
	address = sockaddr
	break

if sockfd is None:
    raise Exception("client: failed to create socket")

sockfd.connect(address)
print(sockfd.recv(BUFFOR_SIZE).decode('utf-8'))
sockfd.close()
