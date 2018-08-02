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
from ctypes import c_char_p, c_bool


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


m = Manager()
finished = m.Value('c_bool', False)
flag = m.Value('c_bool', False)

timeNow = lambda: int(round(time.time() * 1000))
start = timeNow()

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.setblocking(0)

#server = ("52.73.65.98", 1973)

#server = ("localhost", 1973)
server = ("192.168.1.91", 1973)

mac = hex(uuid.getnode())[2:]

arduino = object

l = Lock()

def sprint(lock, msg):
    lock.acquire()
    print(msg)
    lock.release()
    return
    

def GetArduinoResponse(lock):
    while(not finished.value):
        ready = select.select([arduino], [], [], .001)
        if(ready[0]):
            rcv = arduino.read()
            lock.acquire()
            flag.value = True
            lock.release()
            lock.acquire()
            print("received from arduino: ", end="")
            print(rcv)
            lock.release()


def GetRange(l):
    r = random.randint(5, 300)
    sprint(l, r)
    return(r)

def Buzz(l, msec, tone):
    sprint(l, "buzzing at {} hz".format(tone))
    time.sleep(msec / 1000)
    return

def HeartBeat():
    while(not finished.value):
        t = (timeNow() - start).to_bytes(4, byteorder="little")
        #print(t)
        msg = bytearray.fromhex(mac)
        msg += t
        msg += b"\x49" # I for identification
        #sprint(l,msg)
        sent = socket.sendto(msg, server)
        #sprint(l, sent)
        time.sleep(.95)


def Quit(l):
    l.acquire()
    finished.value = True
    print("finished = true")
    l.release()
    arduinoResponse.e.set()
    arduinoResponse.join()
    l.acquire()
    print("arduino process done")
    arduino.close()
    print("arduino closed")
    heartBeat.e.set()
    heartBeat.join()
    socket.close()
    print("socket closed")
    print("done!")
    l.release()
    sys.exit(0)

#############################################################
while(True):
    try:
        sprint(l, "opening arduino...")
        arduino = serial.Serial("/dev/ttyACM0", 38400)
    except Exception as e:
        try:
            arduino = serial.Serial("/dev/ttyACM1", 38400)
        except Exception as e:
            print("couldnt open arduino port.")
            sys.exit(1)
    

sprint(l, "starting arduino process...")
arduinoResponse = Process(target=GetArduinoResponse, args=(l,))
arduinoResponse.e = Event()
arduinoResponse.start()



sprint(l, "started netsblox mode...")

sprint(l, arduino)

sprint(l, "starting heartbeat...")
heartBeat = Process(target=HeartBeat)
heartBeat.e = Event()
heartBeat.start()


buttonState = 0

#wheel speeds
left = 0
right = 0

#whiskers
#lWhisker = lambda: math.ceil(random.random() - .5)
#rWhisker = lambda: math.ceil(random.random() - .5)

lWhisker = 0
rWhisker = 0


sprint(l, "entering main...")
try:
    while(not finished.value):
        if lWhisker == 1 or rWhisker == 1:
            msg = bytearray.fromhex(mac)
            msg += (timeNow() - start).to_bytes(4, byteorder="little")
            msg += b"\x57"
            status = ((lWhisker << 1) | rWhisker).to_bytes(1, byteorder="little")
            msg += status
            #print(list(msg))
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
                Buzz(l, msec, tone)

            elif(rcv[0] == 81): #Q for quit
                sprint(l, "quitting...")
                Quit(l)
                
                
except KeyboardInterrupt:
    Quit(l)
        
        



