#!/bin/python3
import socket
import sys

PORT = 3490

for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(None,PORT,socket.AF_UNSPEC,socket.SOCK_STREAM):
    sockfd = socket.socket(family,type,proto)
    try:
        sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockfd.bind(sockaddr)
    except socket.error:
        if sockfd != None:
            sockfd.close()
        continue
    break

if sockfd == None:
    raise Exception("fail to bind")

sockfd.listen(10)
print("server: waiting for connections...")

while True:
    conn,address = sockfd.accept()
    print("server: got connection from",address[0])
    conn.send("Hello world!".encode('utf-8'))
    conn.close()

sockfd.close()

    