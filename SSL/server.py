#!/usr/bin/env python3
import socket
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('/etc/letsencrypt/live/azure.marszalek.ninja/fullchain.pem', '/etc/letsencrypt/live/azure.marszalek.ninja/privkey.pem')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('', 8443))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        while True:
            conn, addr = ssock.accept()
            print("Got conn")
            conn.sendall(b'\r\n'.join([ bytes(line, 'utf-8') for line in [
                f'Hello World',
            ]]))
            conn.sendall(b"")
            print("Send message")
