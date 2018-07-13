#!/usr/bin/python3

import socket
import psutil
import subprocess
import os
import uuid
import time
import select

#Robot as server for gui app
UDP_ADR = ""
UDP_PORT = 6789
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((UDP_ADR, UDP_PORT))
print(serverSocket)


#robot as client for netsblox
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.setblocking(0)
server = ("192.168.1.91", 1973)
mac = hex(uuid.getnode())[2:]

timeNow = lambda: int(round(time.time() * 1000))
start = timeNow()


initialized = False
pid = -1

def StartProcess():
    try:
        proc = subprocess.Popen(["python3","/home/pi/teachablerobots/RobotCode/MyRobot.py"])
        initialized = True
        return proc.pid
    except Exception as e:
        print(e.message())


def CheckProcess():
    try:
        p = psutil.Process(pid)
        print(p.name)
        print(p.cmdline())
        if(p.cmdline()[1] == []):
            return 1
        else:
            print("process is running.")
            return 0
    except Exception as e:
        print("process is not running.")
        return 1

bool flag = False

while True:
    t = (timeNow() - start).to_bytes(4, byteorder="little")
    #print(t)
    msg = bytearray.fromhex(mac)
    msg += t
    msg += b"\x49" # I for identification
    #print(msg)
    sent = socket.sendto(msg, server)
    time.sleep(.95)
    
    ready = select.select([socket], [], [], .1)
    if(ready[0]):
        response = socket.recv(1024)
        if(response == b'AA'):
            print("connected to netsblox")
            flag = True
            serverSocket.close()

    data, adr = serverSocket.recvfrom(1024)
    msg = data.decode("ascii")
    if(msg == "start robot"):
        print("connected to gui")
        flag = True
        socket.close()

    if(flag):
        if(not initialized and pid == -1):
            pid = StartProcess()
            print(pid)
            print(os.getpid())
        else:
            if(CheckProcess() == 1):
                pid = StartProcess()
        print("message: ", msg)
        flag = False
        
    
