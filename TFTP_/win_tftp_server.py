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
    mess = bytearray(mess,"utf-8")
    block += mess
    return block

def create_path_error():
    message = bytearray()
    message.append(0)
    message.append(5)
    message.append(0)
    message.append(1)
    message += bytearray('Wrong path','utf8')
    message.append(0)
    return message

def create_opt_error():
    message = bytearray()
    message.append(0)
    message.append(5)
    message.append(0)
    message.append(0)
    message += bytearray('Wrong winsize/blksize options','utf8')
    message.append(0)
    return message

def create_oack(blk_size,win_size):
    message = bytearray()
    message.append(0)
    message.append(6)
    if blk_size!=512:
        if blk_size> 65464 or blk_size<8:
            print("Wrong range")
            message = create_opt_error()
            return message, True

        message += bytearray('blksize','utf8')
        message.append(0)
        message += bytearray(f'{blk_size}','utf8')
        message.append(0)
    if win_size!=1:
        if win_size> 65535 or win_size<=0:
            print("Wrong range")
            message = create_opt_error()
            return message, True

        message += bytearray('windowsize','utf8')
        message.append(0)
        message += bytearray(f'{win_size}','utf8')
        message.append(0)

    return message, False


def new_client_read(client_addr, filename, blk_size=512, win_size=1):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockfd:
        timeout = 1
        counter = 0
        first = True
        RTTVAR = 0
        SRTT = 0
        expected_ack_nr = 1
        buffor_size = 512
        window_size = 1
        LAST_DATA = 1
        mess = 0

        try:
            file = open(filename,"r")
        except Exception:
            print("Wrong path")
            message = create_path_error()
            sockfd.sendto(message,client_addr)
            return

        if blk_size!=512 or win_size!=1:
            mess, error = create_oack(blk_size,win_size)
            expected_ack_nr = 0
            sockfd.sendto(mess,client_addr)
            if error:
                exit(0)
            else:
                buffor_size = blk_size
                window_size = win_size
        else:
            mess = create_block(file,1,buffor_size)
            sockfd.sendto(mess,client_addr)
        
        data = [0]*window_size
        data[0] = mess

        print(f"Windowsize: {window_size}")
        print(f"Block size: {buffor_size}")

        start = timer()
        print(f"Start {start}")
        while True:
            is_end = False
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

                if expected_ack_nr==0:
                    print(f"Send again OACK with number: {expected_ack_nr-1}")
                    sockfd.sendto(data[0],client_addr)
                else:
                    for i in range(window_size):
                        if(len(data[i])>4):
                            print(f"Send again DATA with number__: {(expected_ack_nr-window_size + i+1)%MAX_SHORT}")
                            sockfd.sendto(data[i],client_addr)
                continue

            end = timer()
            RTT = end - start
            print(f"RTT: {RTT}")

            opcode = int.from_bytes(mess[:2],"big")
            if opcode==5:
                print("Error occurred!")
                exit(1)
            elif opcode==4:
                print("ACK arrived!")
            else:
                print("Weird opcode")
                continue

            ack_nr = int.from_bytes(mess[2:4],"big")
            print(f"Received ACK: {ack_nr}")

            if expected_ack_nr % MAX_SHORT != ack_nr:
                in_range = False
                if expected_ack_nr%MAX_SHORT - ack_nr<=window_size:
                    dif = expected_ack_nr%MAX_SHORT - ack_nr
                    in_range = True
                elif(expected_ack_nr%MAX_SHORT-ack_nr+MAX_SHORT)%MAX_SHORT<=window_size:
                    dif = (expected_ack_nr%MAX_SHORT-ack_nr+MAX_SHORT)%MAX_SHORT
                    in_range = True
                if in_range:
                    print("Wrong ACK, send last DATA again")
                    data = data[window_size - dif:]
                    is_end=False
                    for i in range(window_size - dif):
                        data.append(create_block(file,(LAST_DATA+i)%MAX_SHORT,buffor_size))
                    for i in range(window_size):
                        if(len(data[i])>4):
                            print(f"Send DATA again with number*: {(LAST_DATA-win_size+dif+i)%MAX_SHORT}")
                            sockfd.sendto(data[i],client_addr)
                        else:
                            if i==0:
                                print("End")
                                return
                            expected_ack_nr = expected_ack_nr -dif + i
                            LAST_DATA = LAST_DATA - dif + i
                            is_end = True
                            break
                    if not is_end:
                        expected_ack_nr = expected_ack_nr + window_size - dif
                        LAST_DATA = LAST_DATA + window_size - dif
                    print(f"Expected ack: {expected_ack_nr}")
                    print(f"Last data: {LAST_DATA}")
                continue

            if first:
                SRTT = RTT
                RTTVAR = RTT/2
                timeout = SRTT + K*RTTVAR
            else:
                RTTVAR = (1-BETA)*RTTVAR + BETA*math.fabs(SRTT-RTT)
                SRTT = (1- ALPHA)*SRTT + ALPHA*RTT
                timeout = SRTT + K*RTTVAR
            print(f"Timeout: {timeout}")

            for i in range(window_size):
                data[i] = create_block(file,(LAST_DATA+i)%MAX_SHORT,buffor_size)

            for i in range(window_size):
                if(len(data[i])>4):
                    print(f"Send DATA with number: {(LAST_DATA+i)%MAX_SHORT} and size {len(data[i])}")
                    sockfd.sendto(data[i],client_addr)
                else:
                    if i==0:
                        print("End")
                        return
                    expected_ack_nr = LAST_DATA + i
                    LAST_DATA = LAST_DATA + i
                    end = True
                    break

            print(f"End {end}")
            if not is_end:
                LAST_DATA += window_size
                expected_ack_nr += window_size

            print(f"Last Data: {LAST_DATA}")
            print(f"Expected ACK: {expected_ack_nr}")
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
                message = create_path_error()
                sock.sendto(message,addr)
                continue

            filename = bytearray()
            print(req[2:])
            for i in req[2:]:
                if i==0:
                    break
                filename.append(i)

            filename = str(filename,"utf-8")
            print(filename)

            blk_size = 512
            win_size = 1
            req = req[9+len(filename):]
            if "blksize" in str(req,"utf-8"):
                bsize = bytearray()
                for i in req[8:]:
                    if i==0:
                        break
                    bsize.append(i)
                
                bsize = str(bsize,"utf-8")
                req = req[9+len(bsize):]
                try:
                    blk_size = int(bsize)
                except Exception:
                    print(f"Weird blocksize {bsize}")
                    message = create_opt_error()
                    sock.sendto(message,addr)
                    continue

            if "windowsize" in str(req,"utf-8"):
                wsize = bytearray()
                for i in req[11:]:
                    if i==0:
                        break
                    wsize.append(i)
                wsize = str(wsize,"utf-8")

                try:
                    win_size = int(wsize)
                except Exception:
                    print(f"Weird winsize {wsize}")
                    message = create_opt_error()
                    sock.sendto(message,addr)
                    continue

            print(f"Windowsize: {win_size}")
            print(f"Block size: {blk_size}")

            if opcode==1:
                print("Read request")
                thread = threading.Thread(target=new_client_read, args=(addr,filename,blk_size,win_size))
                thread.start()
            elif opcode==2:
                print("Write request")
            else:
                print("Weird, error")
                continue
