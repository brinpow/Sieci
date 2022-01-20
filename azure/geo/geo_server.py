#!/usr/bin/env python3
import socket
import threading
import subprocess

MYPORT = 3490
BUFFOR_SIZE = 1000

DISTANCES = dict()
MY_CORDS = (50.110924,8.682127)
SERVERS ={"149.156.75.213","40.115.99.99"}
QUERY = dict()

def send_mess(address,message,sockfd):
    numbytes = sockfd.sendto(message.encode('utf-8'),address)
    print("sent",numbytes,"bytes to",address[0])
    sockfd.close()

def ping_server(ip_add, address,sockfd):
    command = ['ping', "-c", '5', ip_add]
    try:
        output = subprocess.check_output(command).decode().strip()
        output = output.split("time=")
        result = output[1].split(' ')[0]
        send_mess(address,f"DISTANCE {ip_add} {result}",sockfd)
    except Exception:
        print("Server down")
    
def find_distance(ip_add,address,sockfd):
    for i in SERVERS:
        send_mess((i,MYPORT),"DISTANCE ",sockfd)



for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(None,MYPORT,socket.AF_UNSPEC,socket.SOCK_DGRAM):
    sockfd = socket.socket(family,type,proto)
    try:
        sockfd.bind(sockaddr)
    except socket.error:
        continue
    break

if sockfd is None:
    raise Exception("fail to bind")

print("server: waiting to recvfrom...")

while True:
    (message, address) = sockfd.recvfrom(BUFFOR_SIZE)
    mess = [ m.strip() for m in str(message, 'utf8').split() if m.strip() ]
    if mess[0]=="LOCATION" and len(mess)==1:
        thread = threading.Thread(target=send_mess, args=(address,"LOCATION "+str(MY_CORDS)[1:-1],sockfd))
        thread.start()
    elif mess[0]=="LOCATION" and len(mess)==2:
        location = mess[1].split(",")
        
    elif mess[0]=="DISTANCE" and len(mess)==2:
        thread = threading.Thread(target=ping_server, args=(mess[1],address,sockfd))
        thread.start()
    elif mess[0]=="DISTANCE" and len(mess)==3:
        if mess[1] in DISTANCES and float(mess[2].replace(',','.')) < float(DISTANCES[mess[1]][0]):
            DISTANCES[mess[1]] = (mess[2].replace(',','.'),address)
        elif mess[1] not in DISTANCES:
            DISTANCES[mess[1]] = (mess[2].replace(',','.'),address)
    elif mess[0]=="LOCATE" and len(mess)==2:
        QUERY[address]=mess[1]
        thread = threading.Thread(target=find_distance, args=(mess[1],address,sockfd))
        thread.start()
    elif mess[0]=="LOCATE" and len(mess)==3:
        print(".")
        

    print(DISTANCES)
    print("Packet from",address[0])
    print("Packet is",len(message),'bytes long')
    print("Packet contains ",message.decode('utf8'))
sockfd.close()
