#!/usr/bin/env python3
import socket
import threading
import subprocess
import time

MYPORT = 3490
SERVER_PORT = 3490
BUFFOR_SIZE = 1000

DISTANCES = dict()
MY_CORDS = "50.110924,8.682127"
SERVERS ={"149.156.75.213","40.115.99.99","20.37.4.83","20.210.99.69","20.80.184.104","102.37.99.114",
"52.229.90.41","20.203.9.197","138.91.24.213","20.212.81.166","20.206.103.71","52.159.107.25","20.196.208.139",
"52.140.113.216","20.111.13.219","20.203.217.128","51.145.88.111","20.104.121.194","104.208.74.233","20.102.55.23",
"20.38.172.18","51.13.111.13","52.172.51.219","20.92.74.30","40.115.67.130","104.43.234.16","137.135.140.136",
"52.186.150.95","20.212.57.107","52.229.101.225","20.91.137.213","51.141.9.29","20.52.34.131"}
MYIP = "0.0.0.0"

def send_mess(address,message,sockfd):
    numbytes = sockfd.sendto(message.encode('utf-8'),address)
    print("sent",numbytes,"bytes to",address[0])

def ping_server(ip_add, address,sockfd):
    command = ['ping', "-c", '5', ip_add]
    try:
        output = subprocess.check_output(command).decode().strip()
        output = output.split("time=")
        result = output[1].split(' ')[0]
        send_mess(address,f"DISTANCE {ip_add} {result.replace(',','.')}",sockfd)
    except Exception:
        print("Server down")
    
def server_dist(address,message,store_adddress, ip_add):
    for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(MYIP,MYPORT,socket.AF_INET,socket.SOCK_DGRAM):
        sockfd = socket.socket(family,type,proto)
        try:
            sockfd.bind(sockaddr)
        except socket.error:
            continue

    if sockfd is None:
        print("fail to bind")
        return

    send_mess(address,message,sockfd)

    (message, address) = sockfd.recvfrom(BUFFOR_SIZE)
    mess = [ m.strip() for m in str(message, 'utf8').split() if m.strip() ]

    if mess[0]=="DISTANCE" and len(mess)==3:
        result = float(mess[2])
        DISTANCES[(ip_add,store_adddress)].append((result,address))

    sockfd.close()
    


def find_distance(ip_add,address):
    DISTANCES[(ip_add,address)] = []
    for i in SERVERS:
        thread = threading.Thread(target=server_dist, args=((i,SERVER_PORT),f"DISTANCE {ip_add}",address,ip_add))
        thread.start()

    time.sleep(20)

    result_list = DISTANCES[(ip_add,address)]

    minn = -1
    min_address = (MYIP,MYPORT)
    for dist, addr in result_list:
        if minn==-1 or dist < minn:
            minn = dist
            min_address = addr


    for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(MYIP,MYPORT,socket.AF_INET,socket.SOCK_DGRAM):
        sockfd = socket.socket(family,type,proto)
        try:
            sockfd.bind(sockaddr)
        except socket.error:
            continue

    if sockfd is None:
        print("fail to bind")
        return

    send_mess(min_address,"LOCATION",sockfd)

    (message, a) = sockfd.recvfrom(BUFFOR_SIZE)
    mess = [ m.strip() for m in str(message, 'utf8').split() if m.strip() ]

    if mess[0]=="LOCATION" and len(mess)==2:
        location = mess[1]

    send_mess(address,f"LOCATE {ip_add} {location}",sockfd)
    sockfd.close()



for family,type,proto,cannonname,sockaddr in socket.getaddrinfo(MYIP,MYPORT,socket.AF_INET,socket.SOCK_DGRAM):
    sockfd = socket.socket(family,type,proto)
    try:
        sockfd.bind(sockaddr)
    except socket.error:
        continue

if sockfd is None:
    raise Exception("fail to bind")

print("server: waiting to recvfrom...")

while True:
    (message, address) = sockfd.recvfrom(BUFFOR_SIZE)
    mess = [ m.strip() for m in str(message, 'utf8').split() if m.strip() ]
    if mess[0]=="LOCATION" and len(mess)==1:
        thread = threading.Thread(target=send_mess, args=(address,f"LOCATION {MY_CORDS}",sockfd))
        thread.start()
    elif mess[0]=="LOCATION" and len(mess)==2:
        location = mess[1].split(",")   
    elif mess[0]=="DISTANCE" and len(mess)==2:
        thread = threading.Thread(target=ping_server, args=(mess[1],address,sockfd))
        thread.start()
    elif mess[0]=="LOCATE" and len(mess)==2:
        thread = threading.Thread(target=find_distance, args=(mess[1],address))
        thread.start()
        

    print("Packet from",address[0])
    print("Packet is",len(message),'bytes long')
    print("Packet contains ",message.decode('utf8'))
sockfd.close()
