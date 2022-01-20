#!/bin/python3
from timeit import default_timer as timer
import socket
import struct
import sys
import math

IP = '20.52.34.131'
PORT = 6996
BUFFOR_SIZE = 512
ACK_OPCODE = 4
K = 4
ALPHA = 0.25
BETA = 0.125
WINSIZE = 16
MAX_SHORT = 65535

def create_winsize_request(filename):
    message = create_read_request(filename)
    message += bytearray('windowsize','utf8')
    message.append(0)
    message += bytearray(str(WINSIZE),'utf8')
    message.append(0)
    return message

def create_read_request(filename):
    message = bytearray()
    message.append(0)
    message.append(1)
    message += bytearray(filename,'utf8')
    message.append(0)
    message += bytearray('octet','utf8')
    message.append(0)
    return message


if __name__ == '__main__':
    if len(sys.argv)<2:
        print("Filename needed")
        exit(1)
    filename = sys.argv[1]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockfd:
        timeout = 1
        counter = 0
        RTTVAR = 0
        SRTT = 0
        LAST_ACK = 0
        message = create_winsize_request(filename)
        expected_block_nr = 1
        print(message)

        sockfd.sendto(message,(IP,PORT))
        start = timer()

        while True:
            cur_time = timer()
            if start - cur_time >0:
                timeout = timeout -start + cur_time
            else:
                timeout = 2 * timeout
            sockfd.settimeout(timeout)
            try:
                counter = 0
                (mess,addr) = sockfd.recvfrom(BUFFOR_SIZE)
            except socket.timeout:
                print("Timeout occurred")
                counter += 1
                timeout = 2*timeout
                start = timer()
                if expected_block_nr>1:
                    LAST_ACK = (expected_block_nr-1)%MAX_SHORT
                    sockfd.sendto(struct.pack("!hh",ACK_OPCODE,LAST_ACK),addr)
                else:
                    sockfd.sendto(message,(IP,PORT))
                continue
            end = timer()
            RTT = end - start

            opcode = int.from_bytes(mess[:2],"big")
            if opcode == 6:
                SRTT = RTT
                RTTVAR = RTT/2
                timeout = SRTT + K*RTTVAR
                print("OACK received")
                WINSIZE = int.from_bytes(mess[8:])
                if WINSIZE<=0 and WINSIZE>16:
                    print("Error")
                    exit(1)
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

            with open(filename,"a") as file:
                file.write(data.decode("utf-8"))

            print(f"Data size: {len(mess)}")

            if(len(mess)<512):
                sockfd.sendto(struct.pack("!hh",ACK_OPCODE,block_nr),addr)
                break
            
            if expected_block_nr%MAX_SHORT == LAST_ACK + WINSIZE:
                RTTVAR = (1-BETA)*RTTVAR + BETA*math.fabs(SRTT-RTT)
                SRTT = (1- ALPHA)*SRTT + ALPHA*RTT
                timeout = SRTT + K*RTTVAR
                print(timeout)

                LAST_ACK = LAST_ACK + WINSIZE
                sockfd.sendto(struct.pack("!hh",ACK_OPCODE,block_nr),addr)
                start = timer()

            expected_block_nr += 1
            if counter >= 6:
                exit(1)