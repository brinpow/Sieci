#!/usr/bin/env python3

import socket
import threading

HOST = "0.0.0.0"
PORT = 8080
NUMBER_OF_CLIENTS = 10
BUFFOR_SIZE = 2048

def first_line(conn):
    mess = ""
    while(True):
        rec = conn.recv(BUFFOR_SIZE)
        mess += rec.decode('utf-8')

        index = mess.find("\r\n")
        if index==-1:
            continue
        else:
            first_line = mess[:index+2]
            mess = mess[index+2:]
            data = first_line.split(" ")
            try:
                host = data[1]
                port = int(data[2])
            except Exception:
                print("weird")
                exit(1)
            return (host,port),mess

def proxy_client(conn, client_addr):
    server_addr, mess = first_line(conn)
    
    sockfd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sockfd.connect(server_addr)

    thread_server = threading.Thread(target=proxy_server, args=(conn,sockfd))
    thread_server.start()

    if mess!="":
        sockfd.sendall(mess.encode("utf-8"))

    while(True):
        mess = conn.recv(BUFFOR_SIZE)
        print("Got mess to")

        if mess == b'':
            break
        
        sockfd.sendall(mess)

    print("End to")

def proxy_server(conn,sockfd):
    while(True):
        mess = sockfd.recv(BUFFOR_SIZE)
        print("Got mess from")

        if mess == b'':
            sockfd.shutdown(socket.SHUT_RDWR)
            conn.shutdown(socket.SHUT_RDWR)
            break
        conn.sendall(mess)
    sockfd.close()
    conn.close()
    print("End from")


if __name__ == '__main__':    
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sockfd:
        try:
            sockfd.bind((HOST,PORT))
        except socket.error:
            print("Failed to bind")
            exit(1)

        sockfd.listen(NUMBER_OF_CLIENTS)

        while(True):
            conn,address = sockfd.accept()
            print("server: got connection from",address[0])
            thread_client = threading.Thread(target=proxy_client, args=(conn,address))
            thread_client.start()
