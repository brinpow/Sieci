#!/bin/python3
import socket
import sys

HOST = "0.0.0.0"
PORT = 80
NUMBER_OF_CLIENTS = 10

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sockfd:
    try:
        sockfd.bind((HOST,PORT))
    except socket.error:
        print("Failed to bind")
        exit(1)

    sockfd.listen(NUMBER_OF_CLIENTS)

    while(True):
        conn,address = sockfd.accept()
        message = b'\r\n'.join(bytes("HTTP/1.1 200 OK","utf-8")).join(bytes("Server: nginx/1.18.0 (Ubuntu)","utf-8")).join(bytes("Date: Wed, 12 Jan 2022 13:57:49 GMT","utf-8")).join(bytes("Content-Type: text/plain; charset=utf-8","utf-8")).join(bytes("Content-Length: 57","utf-8")).join(bytes("Connection: keep-alive","utf-8")).join(b"\r\n").join(bytes("""path : 
            host : gutowscy.pl
            client : 20.52.34.131:34760""","utf-8"))
        conn.sendall(message)

    