import socket
import uuid
import time
import numpy as np
import select
import random
import math

def GetRange():
    r = random.randint(5, 300)
    print(r)
    return(r)

def Buzz(msec, tone):
    print("buzzing at {} hz".format(tone))
    time.sleep(msec / 1000)
    return


#############################################################


buttonState = 0

#wheel speeds
left = 0
right = 0

#whiskers
#lWhisker = lambda: math.ceil(random.random() - .5)
#rWhisker = lambda: math.ceil(random.random() - .5)

lWhisker = 0
rWhisker = 0

timeNow = lambda: int(round(time.time() * 1000))
start = timeNow()

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.setblocking(0)

#server = ("52.73.65.98", 1973)

server = ("localhost", 1973)

mac = hex(uuid.getnode())[2:]

for i in range(0, 300):
    t = (timeNow() - start).to_bytes(4, byteorder="little")
    #print(t)
    msg = bytearray.fromhex(mac)
    msg += t
    msg += b"\x49" # I for identification
    #print(msg)
    sent = socket.sendto(msg, server)
    time.sleep(.9)


    if lWhisker == 1 or rWhisker == 1:
        msg = bytearray.fromhex(mac)
        msg += (timeNow() - start).to_bytes(4, byteorder="little")
        msg += b"\x57"
        status = ((lWhisker << 1) | rWhisker).to_bytes(1, byteorder="little")
        msg += status
        print(list(msg))
        socket.sendto(msg, server)
        lWhisker = int(bool(not lWhisker))
        rWhisker = int(bool(not rWhisker))

        


    ready = select.select([socket], [], [], .1)
    if(ready[0]):
        response = socket.recv(1024)
        print(response)
        if(response == b'AA'):
            print("YES")

        rcv = list(response)
        #print(int.from_bytes([rcv[1], rcv[2]], byteorder="little", signed=True))
        #print(int.from_bytes([rcv[2], rcv[1]], byteorder="little", signed=True))
        print(rcv)

        if(rcv[0] == 82): #send range
            msg = bytearray.fromhex(mac)
            msg += (timeNow() - start).to_bytes(4, byteorder="little")
            msg += b"\x52"
            msg += GetRange().to_bytes(2, byteorder="little")
            print(list(msg))
            socket.sendto(msg, server)
        
        elif(rcv[0] == 83): #set speed
            left = int.from_bytes([rcv[1], rcv[2]], byteorder="little", signed=True)
            right = int.from_bytes([rcv[3], rcv[4]], byteorder="little", signed=True)
            if(left == right):
                pass
            print(left)
            print(right)

        elif(rcv[0] == 87): #send whisker status
            msg = bytearray.fromhex(mac)
            msg += (timeNow() - start).to_bytes(4, byteorder="little")
            msg += b"\x57"
            msg += lWhisker().to_bytes(1, byteorder="little")
            msg += rWhisker().to_bytes(1, byteorder="little")
            print(list(msg))
            socket.sendto(msg, server)

        elif(rcv[0] == 66): #buzz
            msec = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
            tone = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
            Buzz(msec, tone)

        
        
        



