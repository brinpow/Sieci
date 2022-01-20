#!/bin/python3

import socket
import sys

SERVERPORT = 3490

if len(sys.argv)>5:
    print("usage: talker hostname message")
    exit(1)


for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(sys.argv[1],SERVERPORT,socket.AF_UNSPEC,socket.SOCK_DGRAM):
    sockfd = socket.socket(family,type,proto)
    if sockfd is None:
        continue
    address = sockaddr
    break

if sockfd is None:
    raise Exception("talker: failed to create socket")
    
if len(sys.argv)==4:
    numbytes = sockfd.sendto(f"{sys.argv[2]} {sys.argv[3]}".encode('utf-8'),address)
elif len(sys.argv)==3:
    numbytes = sockfd.sendto(f"{sys.argv[2]}".encode('utf-8'),address)
elif len(sys.argv)==5:
    numbytes = sockfd.sendto(f"{sys.argv[2]} {sys.argv[3]} {sys.argv[4]}".encode('utf-8'),address)
print("talker: sent",numbytes,"bytes to",sys.argv[1])

#print(sockfd.recvfrom(1000))
sockfd.close()