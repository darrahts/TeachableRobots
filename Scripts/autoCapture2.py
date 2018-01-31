#!/usr/bin/python3 -*- coding: utf-8 -*-

#####     IMPORTS     #####
import termios
import datetime
import tty
import sys
import os
import picamera
import time


#####     VARIABLES #####
today = datetime.date.today()
folderPath = "/home/pi/timelapse"
timeNow = ""
dateNow = ""
fileName = ""
intervalTime = time.time()
checkTime = time.time()

##########    CONTROLS CLASS      ##########
class Controls():
    #####     GET KEY     #####
    def getKey():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, new)
        k = None
        try:
            k = os.read(fd, 3)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old)
        key = str(k)
        key = key.replace("b", "")
        key = key.replace("'", "")
        return key
    

    def start(self):
        os.system("stty -echo")
       #camera.start_preview(fullscreen=False, window=(10, 24, 640, 480))
        return
        
    def run(self):
        user_input = ""
        try:
            while(1):
                user_input = Controls.getKey()
                if user_input == "q":
                    break
                
                if user_input == "c":
                    dateNow = str(datetime.date.today())
                    timeNow = str(datetime.datetime.now().strftime("%H:%M:%S"))
                    fileName = dateNow + "_" + timeNow
                    camera.capture(folderPath + "/" + fileName + ".jpg")
  
        finally:
            camera.stop_preview()
            os.system("stty echo")

def assertDirectory():
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

def capture(folderPath):
    dateNow = str(datetime.date.today())
    timeNow = str(datetime.datetime.now().strftime("%H:%M:%S"))
    fileName = dateNow + "_" + timeNow
    camera.capture(folderPath + "/" + fileName + ".jpg")
    #print(fileName)
        
        
try:
    camera = picamera.PiCamera()
    assertDirectory()
    while(True):
        time.sleep(300) #300 / 60sec = 5min
        checkTime = time.time()
        if(checkTime - intervalTime > 1800): #1800 / 60sec = 30
            capture(folderPath)
            intervalTime = checkTime
        
finally:
    os.system("stty echo")
