# -*- coding: utf-8 -*-
import time
from Hardware import *

class Sense(object):
    def __init__(self):
        Setup()
        self.r1 = 0.0
        self.r2 = 0.0
        self.r3 = 0.0


    def GetRange(self):
        pulseStart = time.time()
        pulseEnd = time.time()

        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(.00001)
        GPIO.output(TRIG, GPIO.LOW)

        while(GPIO.input(ECHO) == 0):
            if(time.time() - pulseStart > .5):
                return -1
            pass

        pulseStart = time.time()

        while(GPIO.input(ECHO) == 1):
            if(time.time() - pulseStart > .5):
                return -1
            pass

        pulseEnd = time.time()

        duration = pulseEnd - pulseStart
        totalDistance = duration * 34326 #distance sound travels in cm per second
        objDistance = totalDistance / 2

        
        return objDistance


if (__name__ == "__main__"):
    s = Sense()
    time.sleep(2)
    for i in range(0,4):
        val = s.GetRange()
        if(val > 0):
            print(val)
        else:
            i = i -1
        time.sleep(.075)

    HardwareCleanup()
    

    
