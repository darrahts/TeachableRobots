import socket
import uuid
import time
import numpy as np
import select
import random
import math
import serial
import threading
import sys
import traceback
from teachablerobots.src.Communicate import AppComm
from teachablerobots.src.Sense import Sense
from teachablerobots.src.Hardware import *
import ast
from multiprocessing import Process, Queue, Event, Value, Lock, Manager
from ctypes import c_char_p


##class NetsbloxController(object):
##    def __init__(self, port):
##        self.arduino = serial.Serial(port, 38400, timeout=.01)
##        
##        self.m = Manager()
##        self.input = self.m.Value(c_char_p, b"")
##        self.lock = Lock()
##        self.sensors = Sense()
##        
##        self.arduinoResponseThread = threading.Thread(target=self.GetArduinoResponse)
##        self.arduinoResponseThread.e = threading.Event()
##
##        self.moveCount = 0
##        self.dir = ""
##        self.location = (0,0)
##        self.finished = False
##
##
##    def GetArduinoResponse(self):
##        ardIn = b""
##        while(not self.finished):
##            ready = select.select([socket], [], [], .01)
##            if(ready[0]):
##                rcv = socket.recv(1024)
##                print(rcv)
            
        

timeNow = lambda: int(round(time.time() * 1000))
start = timeNow()

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.setblocking(0)

#server = ("52.73.65.98", 1973)

#server = ("localhost", 1973)
server = ("192.168.1.91", 1973)

mac = hex(uuid.getnode())[2:]

finished = False
arduino = object

def GetArduinoResponse(lock):
    lock.acquire()
    print("checking")
    lock.release()
    while(not finished):
        ready = select.select([arduino], [], [], 0)
        if(ready[0]):
            rcv = arduino.read()
            lock.acquire()
            print("received from arduino: ", end="")
            print(rcv)
            lock.release()


def GetRange():
    r = random.randint(5, 300)
    print(r)
    return(r)

def Buzz(msec, tone):
    print("buzzing at {} hz".format(tone))
    time.sleep(msec / 1000)
    return

def HeartBeat():
    while(not finished):
        t = (timeNow() - start).to_bytes(4, byteorder="little")
        #print(t)
        msg = bytearray.fromhex(mac)
        msg += t
        msg += b"\x49" # I for identification
        #print(msg)
        sent = socket.sendto(msg, server)
        time.sleep(.95)


#############################################################
try:
    arduino = serial.Serial("/dev/ttyACM0", 38400)
except Exception as e:
    try:
        arduino = serial.Serial("/dev/ttyACM1", 38400)
    except Exception as e:
        print("couldnt open arduino port.")
        sys.exit(1)

l = Lock()

arduinoResponse = Process(target=GetArduinoResponse, args=(l,))
arduinoResponse.e = Event()
arduinoResponse.start()

time.sleep(1)
arduino.write("mn".encode('ascii')) #mn to enter netsblox mode
time.sleep(1)
print(arduino)

T = threading.Thread(target=HeartBeat)
T.start()


buttonState = 0

#wheel speeds
left = 0
right = 0

#whiskers
#lWhisker = lambda: math.ceil(random.random() - .5)
#rWhisker = lambda: math.ceil(random.random() - .5)

lWhisker = 0
rWhisker = 0

try:
    while(True):
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
            rcv = socket.recv(1024)
            if(rcv == b'AA'):
                pass
                # something here, informs connection
                #print("YES")

            #print(int.from_bytes([rcv[1], rcv[2]], byteorder="little", signed=True))
            #print(int.from_bytes([rcv[2], rcv[1]], byteorder="little", signed=True))
            l.acquire()
            print("received from netsblox: ", end = "")
            print(rcv)
            #print("***")
            l.release()
            
            if(rcv[0] == 82): #R for send range
                msg = bytearray.fromhex(mac)
                msg += (timeNow() - start).to_bytes(4, byteorder="little")
                msg += b"\x52"
                msg += GetRange().to_bytes(2, byteorder="little")
               # print(list(msg))
                socket.sendto(msg, server)

            elif(rcv[0] == 83): #S for set speed
                left = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
                right = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
                #TODO - incorporate drive and turns based off wheel speed

            elif(rcv[0] == 100): #d for drive
               # print("drive")
                cmd = ("%d %d n" % (rcv[1], rcv[2]))
               # print(cmd)
                #arduino.write("1 6 n".encode('ascii'))
                arduino.write(cmd.encode('ascii'))

            elif(rcv[0] == 116): #t for turn
              #  print("turn")
                cmd = ("%d %d %d n" % (rcv[1], rcv[2], rcv[3]))
              #  print(cmd)
                arduino.write(cmd.encode('ascii'))

            elif(rcv[0] == 115): #s for stop
              #  print("stop")
                arduino.write("5 n".encode('ascii'))
                
            elif(rcv[0] == 87): #W for send whisker status
                msg = bytearray.fromhex(mac)
                msg += (timeNow() - start).to_bytes(4, byteorder="little")
                msg += b"\x57"
                msg += lWhisker().to_bytes(1, byteorder="little")
                msg += rWhisker().to_bytes(1, byteorder="little")
             #   print(list(msg))
                socket.sendto(msg, server)

            elif(rcv[0] == 66): #B for buzz
                msec = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
                tone = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
                Buzz(msec, tone)
                
except KeyboardInterrupt:
    finished = True
    arduinoResponse.e.set()
    arduinoResponse.join()
    T.join()
    print("done!")
        
        



