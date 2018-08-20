import socket
import uuid
import time
import numpy as np
import select
import random
import math
import serial
import sys
sys.path.append("/home/pi/")
#print(sys.path)
import traceback
from teachablerobots.src.Sense import Sense
from teachablerobots.src.Hardware import *
import ast
from multiprocessing import Process, Queue, Event, Value, Lock, Manager
from ctypes import c_char_p, c_bool



class NetsbloxController(object):
    def __init__(self, arduinoPort):
        #Setup() #hardware
        self.arduino = serial.Serial(arduinoPort, 38400)
        
        self.m = Manager()
        self.input = self.m.Value(c_char_p, b"")
        self.finished = self.m.Value('c_bool', False)
        self.voltage = self.m.Value('d', 0.0)
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
        self.panPos = lambda: PanPos() #PAN_CENTER # right = <145 left = >145
        self.tiltPos = lambda: TiltPos()# TILT_CENTER # up = <135 left = >135
        
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
            #self.sprint(r.value)
            if(r.value == prevRange or r.value < 8): #bad readings give 7 or 6
                #self.sprint("bad reading")
                continue
            else:
                prevRange = r.value
                msg = self.MessageBase()
                msg += b"\x52"
                msg += (r.value).to_bytes(2, byteorder="little")
                self.netsbloxSocket.sendto(msg, self.netsbloxServer)
                #self.sprint(r.value)
            if(not triggered and r.value > 8 and r.value < 15):
                TriggerInterrupt() #hardware
                triggered = True
                msg = self.MessageBase()
                msg += b"\x4D" # M for message
                msg += b"\x54\x43" #TC for too close
                self.netsbloxSocket.sendto(msg, self.netsbloxServer)
                self.sprint("Too Close!")
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
                if(rcv == b'~'):
                    #print("voltage: ")
                    time.sleep(.01)
                    self.voltage.value = float(self.arduino.readline())
                    #self.sprint(self.voltage.value)


                    
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

    def MessageBase(self):
        msg = bytearray.fromhex(self.mac)
        msg += (self.timeNow() - self.start).to_bytes(4, byteorder="little")
        return msg
        


    def Run(self):
        self.arduinoResponseP.start()
        self.heartBeatP.start()
        self.sensors.getRangeP.start()
        self.rangeP.start()
        print("PTU POS: {}:{}".format(self.panPos(), self.tiltPos()))
        try:
            while(not self.finished.value):
                if(self.lWhisker == 1 or self.rWhisker == 1):
                    msg = MessageBase()
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
                    #self.sprint(rcv.decode('ISO-8859-1'))
                    
                    if(rcv[0] == 82): #R for send range
                        msg = bytearray.fromhex(self.mac)
                        msg += (self.timeNow() - self.start).to_bytes(4, byteorder="little")
                        msg += b"\x52"
                        msg += self.sensors.currentRange.value.to_bytes(2, byteorder="little")
                        self.netsbloxSocket.sendto(msg, self.netsbloxServer)

                    elif(rcv[0] == 83): #S for set speed
                        left = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
                        right = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
                        #TODO - incorporate drive and turns based off wheel speed

                    elif(rcv[0] == 100): #d for drive
                        cmd = ("%d %d n" % (rcv[1], rcv[2]))
                        self.arduino.write(cmd.encode('ascii'))

                    elif(rcv[0] == 116): # t for turn
                        cmd = ("%d %d %d n" % (rcv[1], rcv[2], rcv[3]))
                        self.arduino.write(cmd.encode('ascii'))

                    elif(rcv[0] == 115): # s for stop
                        self.arduino.write("5 n".encode('ascii'))
                        
                    elif(rcv[0] == 87): # W for send whisker status
                        msg = bytearray.fromhex(self.mac)
                        msg += (timeNow() - self.start).to_bytes(4, byteorder="little")
                        msg += b"\x57"
                        msg += lWhisker().to_bytes(1, byteorder="little")
                        msg += rWhisker().to_bytes(1, byteorder="little")
                        self.netsbloxSocket.sendto(msg, self.netsbloxServer)

                    elif(rcv[0] == 66): # B for buzz
                        msec = int.from_bytes([rcv[1], rcv[2]], byteorder="little")
                        tone = int.from_bytes([rcv[3], rcv[4]], byteorder="little")
                        Buzz(msec, tone)

                    elif(rcv[0] == 81): # Q for quit
                        self.sprint("quitting...")
                        self.Quit()

                    elif(rcv[0] == 86): # V for get voltage
                        self.sprint("checking voltage...")
                        self.arduino.write("6 n".encode('ascii'))
                        time.sleep(.1)
                        msg = self.MessageBase()
                        msg += b"\x56"
                        v = str(self.voltage.value).split('.')
                        msg += int(v[1]).to_bytes(1, byteorder="little")
                        msg += int(v[0]).to_bytes(1, byteorder="little")
                        self.netsbloxSocket.sendto(msg, self.netsbloxServer)

                    elif(rcv[0] == 119):# w for pan
                        curPos = self.panPos()
                        if(rcv[1] == 3):
                            newPos = curPos + rcv[2]
                            if(newPos > PAN_LEFT_MAX):
                                self.sprint("panning left out of range.")
                                continue
                            else:
                                self.sprint("panning left")
                                for i in range(curPos, newPos):
                                    Pan(3)
                        if(rcv[1] == 4):
                            newPos = curPos - rcv[2]
                            if(newPos < PAN_RIGHT_MAX):
                                self.sprint("panning right out of range.")
                                continue
                            else:
                                for i in range(curPos, newPos, -1):
                                    Pan(4)
                        
                        

                    elif(rcv[0] == 101):# e for tilt
                        self.sprint("tilting")
                        
                        
        except KeyboardInterrupt:
            self.Quit()


    def Quit(self):
        self.finished.value = True
        self.sensors.finished.value = True
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
        self.sensors.getRangeP.e.set()
        self.sensors.getRangeP.join()
        self.sensors.Cleanup()
        print("done!")
        sys.exit(0)




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





