#!/bin/python3
from timeit import default_timer as timer
import socket
import struct
import sys
import math
import random

IP = '20.52.34.131'
PORT = 6996
BUFFOR_SIZE = 512
ACK_OPCODE = 4
K = 4
ALPHA = 0.25
BETA = 0.125
MAX_SHORT = 65535

def tester(sockfd):
    mess, addr = 0 , 0
    i = -1
    while i<0 or random.randrange(0,3):
        i += 1
        (mess,addr) = sockfd.recvfrom(BUFFOR_SIZE)
        print(f"Lost: {i} packets from address {addr}")
    return mess,addr

def create_read_request(filename):
    message = bytearray()
    message.append(0)
    message.append(1)
    message += bytearray(filename,'utf8')
    message.append(0)
    message += bytearray('octet','utf8')
    message.append(0)
    return message

def create_read_blocksize(filename,val):
    message = create_read_request(filename)
    message += bytearray('blksize','utf8')
    message.append(0)
    message += bytearray(f'{val}','utf8')
    message.append(0)
    return message

def create_error():
    message = bytearray()
    message.append(0)
    message.append(5)
    message.append(0)
    message.append(0)
    message += bytearray('Wrong blocksize','utf8')
    message.append(0)
    return message

if __name__ == '__main__':
    if len(sys.argv)<3:
        print("Filename, blocksize needed")
        exit(1)
    filename = sys.argv[1]
    block_size = int(sys.argv[2])
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockfd:
        timeout = 1
        counter = 0
        first = True
        RTTVAR = 0
        SRTT = 0

        expected_block_nr =1
        message = 0

        if block_size!=BUFFOR_SIZE:
            message = create_read_blocksize(filename,block_size)
            expected_block_nr = 0
        else:
            message = create_read_request(filename)

        sockfd.sendto(message,(IP,PORT))
        start = timer()
        print(f"Start {start}")
        while True:
            if counter >= 10:
                print("To many timeouts, exited")
                exit(1)

            cur_time = timer()
            if start - cur_time >0:
                timeout = timeout -start + cur_time
            else:
                start = timer()
                print(f"Start {start}")
                counter += 1
                if counter%3==0 and counter>0:
                    timeout = 2 * timeout
                    print(f"Timeout up {timeout}")
            sockfd.settimeout(timeout)
            try:
                #(mess,addr) = sockfd.recvfrom(BUFFOR_SIZE)
                (mess, addr) = tester(sockfd)
                counter = 0
            except socket.timeout:
                print("Timeout occurred")
                counter += 1
                if counter%3==0 and counter>0:
                    timeout = 2*timeout
                    print(f"Timeout up {timeout}")
                start = timer()
                print(f"Start {start}")
                if expected_block_nr>1:
                    print(f"Send again ACK with number: {expected_block_nr-1}")
                    sockfd.sendto(struct.pack("!hh",ACK_OPCODE,(expected_block_nr-1)%MAX_SHORT),addr)
                else:
                    sockfd.sendto(message,(IP,PORT))
                continue
            end = timer()
            RTT = end - start
            print(f"RTT: {RTT}")

            opcode = int.from_bytes(mess[:2],"big")

            if opcode == 6:
                SRTT = RTT
                RTTVAR = RTT/2
                timeout = SRTT + K*RTTVAR
                first = False
                print("OACK received")

                BUFFOR_SIZE = str(mess[10:-1],"utf-8")
                error = False
                try:
                    BUFFOR_SIZE = int(BUFFOR_SIZE)
                except Exception:
                    print(f"Weird blocksize {BUFFOR_SIZE}")
                    error = True

                if not error and (BUFFOR_SIZE<=8 or BUFFOR_SIZE>block_size):
                    print(f"Weird blocksize {BUFFOR_SIZE}")
                    error = True

                if error:
                    message = create_error()
                    sockfd.sendto(message,addr)
                    exit(1)

                print(f"Blocksize {BUFFOR_SIZE}")
                expected_block_nr += 1
                sockfd.sendto(struct.pack("!hh",ACK_OPCODE,0),addr)
                start = timer()
                continue
            elif opcode==5:
                print("Error occurred!")
                sys.exit("Error")
            else:
                print("Data arrived!")
            block_nr = int.from_bytes(mess[2:4],"big")
            data = mess[4:]
            print(f"Received block: {block_nr}")
            if expected_block_nr % MAX_SHORT!= block_nr:
                print("Wrong block")
                continue

            if expected_block_nr>1:
                with open(filename,"a") as file:
                    file.write(data.decode("utf-8"))
            elif expected_block_nr==1:
                with open(filename,"w") as file:
                    file.write(data.decode("utf-8"))

            print(f"Data size: {len(mess)}")
            expected_block_nr += 1

            if(len(mess)<BUFFOR_SIZE):
                print(f"Send final ACK with number: {block_nr}")
                sockfd.sendto(struct.pack("!hh",ACK_OPCODE,block_nr),addr)
                break
            

            if first:
                SRTT = RTT
                RTTVAR = RTT/2
                timeout = SRTT + K*RTTVAR
            else:
                RTTVAR = (1-BETA)*RTTVAR + BETA*math.fabs(SRTT-RTT)
                SRTT = (1- ALPHA)*SRTT + ALPHA*RTT
                timeout = SRTT + K*RTTVAR
            print(f"Timeout: {timeout}")

            print(f"Send ACK with number: {block_nr}")
            sockfd.sendto(struct.pack("!hh",ACK_OPCODE,block_nr),addr)
            start = timer()
            print(f"Start {start}")
            first = False