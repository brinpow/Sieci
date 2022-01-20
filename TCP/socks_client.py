#!/usr/bin/env python3

import socket

SOCKS = ('localhost', 8080, 'gutowski')

HOST = 'gutowscy.pl'
PORT = 80

def connect_command(host, port):
    return b'CONNECT ' + b' '.join([
        bytes(host, 'utf8'),
        bytes(str(port), 'utf8'),
        bytes(SOCKS[2], 'utf8'),
        ]) + b'\r\n'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SOCKS[0], SOCKS[1]))

print('WRITE', connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
sock.sendall(connect_command('localhost', SOCKS[1]))
print('WRITE', connect_command(HOST, PORT))
sock.sendall(connect_command(HOST, PORT))

req = b'\r\n'.join([
    b'GET / HTTP/1.0',
    b'Host: ' + bytes(HOST, 'utf8'),
    b'Connection: close',
    b'',
    b''
    ])

print('WRITE', req)
sock.sendall(req)
response = b''
while True:
    part = sock.recv(8192)
    if part == b'':
        break
    response += part
print('READ ', response)
sock.close()