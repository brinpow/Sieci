#!/bin/python3
from timeit import default_timer as timer
import socket
import struct
import math
import threading

IP = "0.0.0.0"
PORT = 6996
DATA_OPCODE = 3
K = 4
ALPHA = 0.25
BETA = 0.125
MAX_SHORT = 65535
BUFFOR_SIZE = 512

def create_block(file,block_nr,buffor_size):
    block = struct.pack("!hh",DATA_OPCODE,block_nr)
    mess = file.read(buffor_size)
    print(len(mess))
    if len(mess)==0:
        raise Exception("End")
    mess = bytearray(mess,"utf-8")
    block += mess
    return block

def create_error():
    message = bytearray()
    message.append(0)
    message.append(5)
    message.append(0)
    message.append(1)
    message += bytearray('Wrong path','utf8')
    message.append(0)
    return message

def create_oack(val):
    message = bytearray()
    if val> 65464 or val<8:
        print("Wrong range")
        message.append(0)
        message.append(5)
        message.append(0)
        message.append(0)
        message += bytearray('Wrong range','utf8')
        message.append(0)
        return message, True

    message.append(0)
    message.append(6)
    message += bytearray('blksize','utf8')
    message.append(0)
    message += bytearray(f'{val}','utf8')
    message.append(0)
    return message, False


def new_client_read(client_addr, filename, val=512):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockfd:
        timeout = 1
        counter = 0
        first = True
        RTTVAR = 0
        SRTT = 0
        expected_ack_nr = 1
        buffor_size = 512

        try:
            file = open(filename,"r")
        except Exception:
            print("Wrong path")
            message = create_error()
            sockfd.sendto(message,client_addr)
            return

        data = 0
        if val!=512:
            data, error = create_oack(val)
            expected_ack_nr = 0
            sockfd.sendto(data,client_addr)
            if error:
                exit(0)
            else:
                buffor_size = val
        else:
            data = create_block(file,1,buffor_size)
            sockfd.sendto(data,client_addr)
        start = timer()
        print(f"Start {start}")
        while True:
            if counter >= 6:
                print("Too many timeouts, exited")
                return

            cur_time = timer()
            if start - cur_time >0:
                timeout = timeout -start + cur_time
            else:
                start = timer()
                print(f"Start {start}")
                counter += 1
                if counter%2==0 and counter>0:
                    timeout = 2 * timeout
                    print(f"Timeout up {timeout}")
            sockfd.settimeout(timeout)
            try:
                (mess,addr) = sockfd.recvfrom(buffor_size)
                counter = 0
            except socket.timeout:
                print("Timeout occurred")
                counter += 1
                if counter%2==0 and counter>0:
                    timeout = 2*timeout
                    print(f"Timeout up {timeout}")

                start = timer()
                print(f"Start {start}")

                print(f"Send again DATA with number: {expected_ack_nr-1}")
                sockfd.sendto(data,client_addr)
                continue

            end = timer()
            RTT = end - start
            print(f"RTT: {RTT}")

            opcode = int.from_bytes(mess[:2],"big")
            if opcode==5:
                print("Error occurred!")
                sys.exit("Error")
            elif opcode==4:
                print("ACK arrived!")
            else:
                print("Weird opcode")
                continue

            ack_nr = int.from_bytes(mess[2:4],"big")
            print(f"Received ACK: {ack_nr}")

            if expected_ack_nr % MAX_SHORT != ack_nr:
                print("Wrong ACK, send last DATA again")
                sockfd.sendto(data,client_addr)
                continue

            expected_ack_nr += 1

            if first:
                SRTT = RTT
                RTTVAR = RTT/2
                timeout = SRTT + K*RTTVAR
            else:
                RTTVAR = (1-BETA)*RTTVAR + BETA*math.fabs(SRTT-RTT)
                SRTT = (1- ALPHA)*SRTT + ALPHA*RTT
                timeout = SRTT + K*RTTVAR
            print(f"Timeout: {timeout}")

            try: 
                data = create_block(file,expected_ack_nr%MAX_SHORT,buffor_size)
            except Exception:
                print("End")
                return

            print(f"Send DATA with number: {expected_ack_nr%MAX_SHORT}")
            sockfd.sendto(data,client_addr)

            start = timer()
            print(f"Start {start}")
            first = False

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.bind((IP,PORT))
        except:
            print("Failed to bind")
            exit(1)

        print("Server started")
        while True:
            req, addr = sock.recvfrom(BUFFOR_SIZE)

            try:
                opcode = int.from_bytes(req[:2],"big")
            except Exception:
                print("Weird")
                continue

            filename = bytearray()
            print(req[2:])
            for i in req[2:]:
                if i==0:
                    break
                filename.append(i)

            filename = str(filename,"utf-8")
            print(filename)

            val = 512
            if "blksize" in str(req[2:],"utf-8"):
                val = req[17+len(filename):-1]
                val = str(val,"utf-8")
                try:
                    val = int(val)
                    print(f"Blocksize: {val}")
                except Exception:
                    print(f"Weird size {val}")

            if opcode==1:
                print("Read request")
                thread = threading.Thread(target=new_client_read, args=(addr,filename,val))
                thread.start()
            elif opcode==2:
                print("Write request")
            else:
                print("Weird, error")
                continue
