#!/bin/python3

import socket
import sys

MYPORT = 4950
BUFFOR_SIZE = 1000


for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(None,MYPORT,socket.AF_UNSPEC,socket.SOCK_DGRAM):
    sockfd = socket.socket(family,type,proto)
    try:
        sockfd.bind(sockaddr)
    except socket.error:
        continue

    break

if sockfd == None:
    raise Exception("fail to bind")

print("listener: waiting to recvfrom...")

while True:
    rtuple = sockfd.recvfrom(BUFFOR_SIZE)
    print("Packet from",rtuple[1])
    print("Packet is",len(rtuple[0]),'bytes long')
    print("Packet contains ",rtuple[0].decode("utf-8"))

sockfd.close()