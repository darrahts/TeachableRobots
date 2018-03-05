# -*- coding: utf-8 -*-
import time
from Hardware import *

class Sense(object):
    def __init__(self):
        Setup()

    def _getRange(self):
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
        totalDistance = duration * 34300 #distance sound travels in cm per second
        objDistance = totalDistance / 2

        return objDistance

    def GetRange(self, printAll=False):
        total = 0.0
        prevVal = -1
        for i in range(0,4):
            val = self._getRange()
            if(printAll):
                print(val)
                
            if(val > 0):
                if(prevVal == -1 or abs(prevVal - val) < 20):
                    prevVal = val
                    total += val
                else:
                    i = i - 1
            else:
                i = i -1
            time.sleep(.075)

        if(printAll):
            print("______")
        return int(total / 4.0)


if (__name__ == "__main__"):
    s = Sense()
    time.sleep(2)
    print(s.GetRange(True))
    HardwareCleanup()
    

    
