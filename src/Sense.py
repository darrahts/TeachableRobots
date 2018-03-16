# -*- coding: utf-8 -*-
import time
from teachablerobots.src.Hardware import *
from multiprocessing import Process, Queue, Event, Value, Lock, Manager


class Sense(object):
    def __init__(self):
        Setup()
        self.m = Manager()
        self.lock = Lock()
        self.currentRange = self.m.Value('i',0)
        self.finished = self.m.Value('i',0)
        self.finished.value = False

        self.rangeProcess = Process(target=self.SetInstantRange, args=(self.currentRange,))
        self.rangeProcess.e = Event()
        #self.rangeProcess.daemon = True
        

    def GetRange(self):
        '''returns the current range value'''
        return self.currentRange.value
            

    def SetInstantRange(self, r):
        '''reads the sonic range sensor with _getRange function and
            assigns the value to currentRange.value'''
        temp = -1
        while(not self.finished.value):
            time.sleep(.1)
            while(temp < 0):
                temp = self._getRange()
            if(temp > 8 and temp < 200):
                if(self.currentRange.value == 0 or abs(self.currentRange.value - temp) < 20):
                    self.lock.acquire()
                    try:
                        r.value = temp
                    finally:
                        self.lock.release()

        return

    def _getRange(self):
        '''the actual function to detect the range of an object.
            returns -1 if it takes too long (i.e. random error) '''
        pulseStart = time.time()
        pulseEnd = time.time()

        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(.00002)
        GPIO.output(TRIG, GPIO.LOW)

        while(GPIO.input(ECHO) == 0):
            if(time.time() - pulseStart > .05):
                return -1
            pass

        pulseStart = time.time()

        while(GPIO.input(ECHO) == 1):
            if(time.time() - pulseStart > .05):
                return -1
            pass

        pulseEnd = time.time()

        duration = pulseEnd - pulseStart
        totalDistance = duration * 34300 #distance sound travels in cm per second
        objDistance = totalDistance / 2

        return int(objDistance)

    def GetAvgRange(self, printAll=False):
        '''averages 5 "good" readings of the sonic range sensor
            using _getRange function'''
        total = 0.0
        prevVal = -1
        i = 0
        while(i < 5):
            val = self._getRange()
            if(printAll):
                print(val)
                
            if(val > 0):
                if(prevVal == -1 or abs(prevVal - val) < 10):
                    prevVal = val
                    total += val
                else:
                    i -= 1
            else:
                i -= 1
            time.sleep(.075)
            i+=1

        if(printAll):
            print("______")
        return int(total / 4.0)

    def CleanUp(self):
        HardwareCleanup()


##if (__name__ == "__main__"):
##    s = Sense()
##    time.sleep(2)
##    print(s.GetAvgRange(True))
##    HardwareCleanup()
##    

    
