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


initialized = False
pid = -1

def StartProcess():
    try:
        proc = subprocess.Popen(["python3","/home/pi/teachablerobots/RobotCode/NetsbloxController.py"])
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

flag = False

while True:
    ready2 = select.select([serverSocket], [], [], .1)
    if(ready2[0]):
        data, adr = serverSocket.recvfrom(1024)
        msg = data.decode("ascii")
        if(msg == "start robot"):
            print("connected to netsblox")
            flag = True


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
        
    
