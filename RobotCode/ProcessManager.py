#!/usr/bin/python3

import socket
import psutil
import subprocess
import os
import uuid
import time
import select



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
        #print(p.name)
        #print(p.cmdline())
        if(p.cmdline()[1] == []):
            return 1
        else:
            #print("process is running.")
            return 0
    except Exception as e:
        #print("process is not running.")
        return 1


while True:
    if(not initialized and pid == -1):
        pid = StartProcess()
        print(pid)
        print(os.getpid())
    else:
        if(CheckProcess() == 1):
            pid = StartProcess()     
    
