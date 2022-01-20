#!/bin/python3
import socket
import sys
import threading

HOST = "0.0.0.0"
PORT = 80
NUMBER_OF_CLIENTS = 10

def response(conn):
    pass

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sockfd:
    try:
        sockfd.bind((HOST,PORT))
    except socket.error:
        print("Failed to bind")
        exit(1)

    sockfd.listen(NUMBER_OF_CLIENTS)

    while(True):
        conn,address = sockfd.accept()
        thread = threading.
        conn.sendall(message)

    