#!/usr/bin/env python3
import socket
import ssl

hostname = 'azure.marszalek.ninja'
context = ssl.create_default_context()

with socket.create_connection((hostname, 8443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.cipher())
        print(ssock.getpeercert())
        ssock.sendall(b'\r\n'.join([ bytes(line, 'utf-8') for line in [
            f'GET / HTTP/1.1',
            f'Host: {hostname}',
            f'Connection: close',
            f'',
            f'',
        ]]))
        response=b''
        while True:
            buf = ssock.recv()
            print(buf)
            response += buf
            if buf == b'':
                break
        print(response)
