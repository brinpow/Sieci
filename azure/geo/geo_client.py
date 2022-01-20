#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

import argparse
import logging
import selectors
import socket
import sys
import time

HOST = 'localhost'
PORT = 3490
TIMEOUT = 10
RETRIES = 3
QUERIES = []
parser = argparse.ArgumentParser(description='IP Geographic Localization Client.')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show more info')
parser.add_argument('-d', '--debug', action='store_true', default=False, help='show debug info')
parser.add_argument('--host', help='server hostname to use')
parser.add_argument('--port', type=int, help='server PORT to use')
parser.add_argument('--timeout', type=float, help='set TIMEOUT for each query')
parser.add_argument('--retries', type=int, help='set number of RETRIES for each query')
parser.add_argument('--distance', action='store_true', default=False, help='query for distance instead of location')
parser.add_argument('queries', type=str, metavar='query', nargs='+', help='add QUERY')
args = parser.parse_args()
level=logging.WARNING
if args.debug:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbose:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)
HOST = args.host or HOST
PORT = args.port or PORT
TIMEOUT = args.timeout or TIMEOUT
RETRIES = args.retries or RETRIES
QUERIES = set((args.queries or []) + QUERIES)

socks = dict()
sockaddrs = set()
client_socket = None
server_location = None
with selectors.DefaultSelector() as selector:
    for retry in range(RETRIES):
        if server_location:
            break
        try:
            for family, type, proto, canonname, sockaddr in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_DGRAM):
                if (family, type, proto) not in socks:
                    client_socket = socket.socket(family, type, proto)
                    client_socket.setblocking(False)
                    selector.register(client_socket, selectors.EVENT_READ)
                    socks[(family, type, proto)] = client_socket
                else:
                    client_socket = socks[(family, type, proto)]
                sockaddrs.add(sockaddr)
                logging.info(f'Querying location of {sockaddr}')
                client_socket.sendto(bytes(f'LOCATION', 'utf8'), sockaddr)
            deadline = time.monotonic() + TIMEOUT
            while True:
                timeout = deadline - time.monotonic()
                if timeout <= 0:
                    break
                for key, mask in selector.select(timeout=timeout):
                    client_socket = key.fileobj
                    msg, addr = client_socket.recvfrom(2048)
                    msg = [ m.strip() for m in str(msg, 'utf8').split() if m.strip() ]
                    logging.debug(f'Received message {msg} from {addr}')
                    if addr in sockaddrs and len(msg) == 2 and msg[0] == 'LOCATION':
                        server_location = msg[1]
                        sockaddrs = set([addr])
                        for sock in socks.values():
                            if sock != client_socket:
                                sock.close()
                        socks = dict()
                        logging.info(f'Accepted server location for {addr} (@{server_location})')
                        break
                if server_location:
                    break
        except socket.error:
            continue

if not server_location:
    logging.warning(f'Failed to communicate with {HOST}:{PORT}')
    sys.exit(1)

with selectors.DefaultSelector() as selector:
    selector.register(client_socket, selectors.EVENT_READ)
    for retry in range(RETRIES):
        if not len(QUERIES):
            break
        try:
            for query in QUERIES:
                logging.info(f'Querying {sockaddr} (@{server_location}) for {query}')
                if args.distance:
                    client_socket.sendto(bytes(f'DISTANCE {query}', 'utf8'), sockaddr)
                else:
                    client_socket.sendto(bytes(f'LOCATE {query}', 'utf8'), sockaddr)
            deadline = time.monotonic() + TIMEOUT
            while True:
                timeout = deadline - time.monotonic()
                if timeout <= 0:
                    break
                for key, mask in selector.select(timeout=timeout):
                    client_socket = key.fileobj
                    msg, addr = client_socket.recvfrom(2048)
                    msg = [ m.strip() for m in str(msg, 'utf8').split() if m.strip() ]
                    logging.debug(f'Received message {msg} from {addr}')
                    if addr in sockaddrs and not args.distance and len(msg) == 3 and msg[0] == 'LOCATE' and msg[1] in QUERIES:
                        query = msg[1]
                        location = msg[2]
                        print(f'Location for {query} is {location}')
                        QUERIES.remove(query)
                    if addr in sockaddrs and args.distance and len(msg) == 3 and msg[0] == 'DISTANCE' and msg[1] in QUERIES:
                        query = msg[1]
                        distance = msg[2]
                        print(f'Distance for {query} is {distance}')
                        QUERIES.remove(query)
                if not len(QUERIES):
                    break
        except socket.error:
            continue