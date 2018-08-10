import socket
import uuid
import time
import numpy as np
import select
import random
import math
import serial
import sys
import traceback
from teachablerobots.src.Sense import Sense
from teachablerobots.src.Hardware import *
import ast
from multiprocessing import Process, Queue, Event, Value, Lock, Manager
from ctypes import c_char_p, c_bool



class NetsbloxController(object):
    def __init__(self, arduinoPort):
        Setup() #hardware
        self.arduino = serial.Serial(arduinoPort, 38400)
        
        self.m = Manager()
        self.input = self.m.Value(c_char_p, b"")
        self.finished = self.m.Value('c_bool', False)
        self.lock = Lock()
        self.sensors = Sense()

        #   arduino communication
        self.arduinoResponseP = Process(target=self.GetArduinoResponse)
        self.arduinoResponseP.e = Event()

        #   heartbeat for netsblox (i.e. keepalive)
        self.heartBeatP = Process(target=self.HeartBeat)
        self.heartBeatP.e = Event()

        #   monitors the range sensor
        self.rangeP = Process(target=self.WatchRange, args=(self.sensors.currentRange,))
        self.rangeP.e = Event()       

        self.lWheelSpeed = 0
        self.rWheelSpeed = 0
        self.lWhisker = 0
        self.rWhisker = 0

        self.buttonState = 0
        
        self.moveCount = 0
        self.dir = ""
        self.location = (0,0)

        self.timeNow = lambda: int(round(time.time() * 1000))
        self.start = self.timeNow()

        self.netsbloxSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.netsbloxServer = ("192.168.1.91", 1973)

        self.mac = hex(uuid.getnode())[2:]



    def WatchRange(self, r):
        '''monitors the robot's range and stops it if necessary'''
        time.sleep(2)
        triggered = False
        prevRange = 0
        self.sprint("monitoring range...")
        while(not self.finished.value):
            time.sleep(.25)
            sprint(r.value)
            if(r.value == prevRange or r.value < 8): #bad readings give 7 or 6
                continue
            else:
                prevRange = r.value
                msg = self.MessageBase(self)
                msg += b"\x52"
                msg += (r.value).to_bytes(2, byteorder="little")
                self.netsbloxSocket.sendto(msg, self.netsbloxServer)
                self.sprint(r.value)
            if(not triggered and r.value > 8 and r.value < 15):
                TriggerInterrupt() #hardware
                triggered = True
                msg = self.MessageBase(self)
                msg += b"\x4D" # M for message
                msg += b"\x54\x43" #TC for too close
                self.netsbloxSocket.sendto(msg, self.netsbloxServer)
                #print("Too Close!")
            if(triggered and r.value > 15):
                triggered = False

                

    def sprint(self, msg):
        self.lock.acquire()
        print(msg)
        self.lock.release()
        return


    def GetArduinoResponse(self):
        while(not self.finished.value):
            ready = select.select([self.arduino], [], [], .001)
            if(ready[0]):
                rcv = self.arduino.read()
                self.sprint("received from arduino: ")
                self.sprint(rcv)

    def HeartBeat(self):
        while(not self.finished.value):
            t = (self.timeNow() - self.start).to_bytes(4, byteorder="little")
            #print(t)
            msg = bytearray.fromhex(self.mac)
            msg += t
            msg += b"\x49" # I for identification
            #sprint(l,msg)
            self.netsbloxSocket.sendto(msg, self.netsbloxServer)
            #sprint(l, sent)
            time.sleep(.96)

    def MessageBase():
        msg = bytearray.fromhex(self.mac)
        msg += (self.timeNow() - self.start).to_bytes(4, byteorder="little")
        return msg
        


    def Run(self):
        self.arduinoResponseP.start()
        self.heartBeatP.start()
        self.rangeP.start()
        
        try:
            while(not self.finished.value):
                if(self.lWhisker == 1 or self.rWhisker == 1):
                    msg = bytearray.fromhex(self.mac)
                    msg += (self.timeNow() - self.start).to_bytes(4, byteorder="little")
                    msg += b"\x57"
                    status = ((self.lWhisker << 1) | self.rWhisker).to_bytes(1, byteorder="little")
                    msg += status
                    self.netsbloxSocket.sendto(msg, self.netsbloxServer)
                    

                ready = select.select([self.netsbloxSocket], [], [], .1)
                if(ready[0]):
                    rcv = self.netsbloxSocket.recv(1024)
                    if(rcv == b'AA'):
                        pass
                        # something here, informs connection
                        #print("YES")

                    self.sprint("received from netsblox: ")
                    self.sprint(rcv)
                    
                    if(rcv[0] == 82): #R for send range
                        msg = bytearray.fromhex(self.mac)
                        msg += (self.timeNow() - self.start).to_bytes(4, byteorder="little")
                        msg += b"\x52"
                        msg += GetRange().to_bytes(2, byteorder="little")
                       # print(list(msg))
                        self.netsbloxSocket.sendto(msg, self.netsbloxServer)

                    elif(rcv[0] == 83): #S for set speed
                        left = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
                        right = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
                        #TODO - incorporate drive and turns based off wheel speed

                    elif(rcv[0] == 100): #d for drive
                       # print("drive")
                        cmd = ("%d %d n" % (rcv[1], rcv[2]))
                       # print(cmd)
                        #arduino.write("1 6 n".encode('ascii'))
                        self.arduino.write(cmd.encode('ascii'))

                    elif(rcv[0] == 116): #t for turn
                      #  print("turn")
                        cmd = ("%d %d %d n" % (rcv[1], rcv[2], rcv[3]))
                      #  print(cmd)
                        self.arduino.write(cmd.encode('ascii'))

                    elif(rcv[0] == 115): #s for stop
                      #  print("stop")
                        self.arduino.write("5 n".encode('ascii'))
                        
                    elif(rcv[0] == 87): #W for send whisker status
                        msg = bytearray.fromhex(self.mac)
                        msg += (timeNow() - self.start).to_bytes(4, byteorder="little")
                        msg += b"\x57"
                        msg += lWhisker().to_bytes(1, byteorder="little")
                        msg += rWhisker().to_bytes(1, byteorder="little")
                     #   print(list(msg))
                        self.netsbloxSocket.sendto(msg, self.netsbloxServer)

                    elif(rcv[0] == 66): #B for buzz
                        msec = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
                        tone = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
                        #Buzz(l, msec, tone)

                    elif(rcv[0] == 81): #Q for quit
                        self.sprint("quitting...")
                        self.Quit()
                        
                        
        except KeyboardInterrupt:
            self.Quit()


    def Quit(self):
        self.finished.value = True
        self.arduinoResponseP.e.set()
        self.arduinoResponseP.join()
        self.sprint("arduino process done")
        self.arduino.close()
        self.sprint("arduino closed")
        self.heartBeatP.e.set()
        self.heartBeatP.join()
        self.netsbloxSocket.close()
        print("socket closed")
        self.rangeP.e.set()
        self.rangeP.join()
        self.sensors.Cleanup()
        print("done!")
        sys.exit(0)



#m = Manager()
#finished = m.Value('c_bool', False)

#timeNow = lambda: int(round(time.time() * 1000))
#start = timeNow()

#socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#socket.setblocking(0)

#server = ("52.73.65.98", 1973)

#server = ("localhost", 1973)
#server = ("192.168.1.91", 1973)

#mac = hex(uuid.getnode())[2:]

##arduino = object

#l = Lock()

    

##def GetArduinoResponse(lock):
##    while(not finished.value):
##        ready = select.select([arduino], [], [], .001)
##        if(ready[0]):
##            rcv = arduino.read()
##            lock.acquire()
##            flag.value = True
##            lock.release()
##            lock.acquire()
##            print("received from arduino: ", end="")
##            print(rcv)
##            lock.release()


##def GetRange(l):
##    r = random.randint(5, 300)
##    sprint(l, r)
##    return(r)
##
##def Buzz(l, msec, tone):
##    sprint(l, "buzzing at {} hz".format(tone))
##    time.sleep(msec / 1000)
##    return

##def HeartBeat():
##    while(not finished.value):
##        t = (timeNow() - start).to_bytes(4, byteorder="little")
##        #print(t)
##        msg = bytearray.fromhex(mac)
##        msg += t
##        msg += b"\x49" # I for identification
##        #sprint(l,msg)
##        sent = socket.sendto(msg, server)
##        #sprint(l, sent)
##        time.sleep(.95)


##def Quit(l):
##    l.acquire()
##    finished.value = True
##    print("finished = true")
##    l.release()
##    arduinoResponse.e.set()
##    arduinoResponse.join()
##    l.acquire()
##    print("arduino process done")
##    arduino.close()
##    print("arduino closed")
##    heartBeat.e.set()
##    heartBeat.join()
##    socket.close()
##    print("socket closed")
##    print("done!")
##    l.release()
##    sys.exit(0)

###############################################################

if(__name__ == "__main__"):
    try:
        c = NetsbloxController("/dev/ttyACM0")
    except Exception as e:
        print(e)
        try:
            c = NetsbloxController("/dev/ttyACM1")
        except Exception as f:
            print("***")
            print(f)
            print("couldnt open arduino port.")
            sys.exit(1)
    c.Run()

    

##sprint(l, "starting arduino process...")
##arduinoResponse = Process(target=GetArduinoResponse, args=(l,))
##arduinoResponse.e = Event()
##arduinoResponse.start()



##sprint(l, "started netsblox mode...")

##sprint(l, arduino)

##sprint(l, "starting heartbeat...")
##heartBeat = Process(target=HeartBeat)
##heartBeat.e = Event()
##heartBeat.start()


##buttonState = 0

###wheel speeds
##left = 0
##right = 0

###whiskers
##lWhisker = lambda: math.ceil(random.random() - .5)
##rWhisker = lambda: math.ceil(random.random() - .5)

##lWhisker = 0
##rWhisker = 0


##sprint(l, "entering main...")
##try:
##    while(not finished.value):
##        if lWhisker == 1 or rWhisker == 1:
##            msg = bytearray.fromhex(mac)
##            msg += (timeNow() - start).to_bytes(4, byteorder="little")
##            msg += b"\x57"
##            status = ((lWhisker << 1) | rWhisker).to_bytes(1, byteorder="little")
##            msg += status
##            #print(list(msg))
##            socket.sendto(msg, server)
##            lWhisker = int(bool(not lWhisker))
##            rWhisker = int(bool(not rWhisker))
##
##
##        ready = select.select([socket], [], [], .1)
##        if(ready[0]):
##            rcv = socket.recv(1024)
##            if(rcv == b'AA'):
##                pass
##                # something here, informs connection
##                #print("YES")
##
##            #print(int.from_bytes([rcv[1], rcv[2]], byteorder="little", signed=True))
##            #print(int.from_bytes([rcv[2], rcv[1]], byteorder="little", signed=True))
##            l.acquire()
##            print("received from netsblox: ", end = "")
##            print(rcv)
##            #print("***")
##            l.release()
##            
##            if(rcv[0] == 82): #R for send range
##                msg = bytearray.fromhex(mac)
##                msg += (timeNow() - start).to_bytes(4, byteorder="little")
##                msg += b"\x52"
##                msg += GetRange().to_bytes(2, byteorder="little")
##               # print(list(msg))
##                socket.sendto(msg, server)
##
##            elif(rcv[0] == 83): #S for set speed
##                left = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
##                right = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
##                #TODO - incorporate drive and turns based off wheel speed
##
##            elif(rcv[0] == 100): #d for drive
##               # print("drive")
##                cmd = ("%d %d n" % (rcv[1], rcv[2]))
##               # print(cmd)
##                #arduino.write("1 6 n".encode('ascii'))
##                arduino.write(cmd.encode('ascii'))
##
##            elif(rcv[0] == 116): #t for turn
##              #  print("turn")
##                cmd = ("%d %d %d n" % (rcv[1], rcv[2], rcv[3]))
##              #  print(cmd)
##                arduino.write(cmd.encode('ascii'))
##
##            elif(rcv[0] == 115): #s for stop
##              #  print("stop")
##                arduino.write("5 n".encode('ascii'))
##                
##            elif(rcv[0] == 87): #W for send whisker status
##                msg = bytearray.fromhex(mac)
##                msg += (timeNow() - start).to_bytes(4, byteorder="little")
##                msg += b"\x57"
##                msg += lWhisker().to_bytes(1, byteorder="little")
##                msg += rWhisker().to_bytes(1, byteorder="little")
##             #   print(list(msg))
##                socket.sendto(msg, server)
##
##            elif(rcv[0] == 66): #B for buzz
##                msec = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
##                tone = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
##                Buzz(l, msec, tone)
##
##            elif(rcv[0] == 81): #Q for quit
##                sprint(l, "quitting...")
##                Quit(l)
##                
##                
##except KeyboardInterrupt:
##    Quit(l)
        
        



