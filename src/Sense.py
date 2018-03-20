# -*- coding: utf-8 -*-
import time
from teachablerobots.src.Hardware import *
from multiprocessing import Process, Queue, Event, Value, Lock, Manager
import statistics

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

    def GetRangeContinuous(self, r):
        while(not self.finished.value):
            self.lock.acquire()
            try:
                r.value = self.GetAvgRange(False)
            finally:
                self.lock.release()

    def SetInstantRange(self, r):
        '''reads the sonic range sensor with _getRange function and
            assigns the value to currentRange.value'''
        while(not self.finished.value):
            temp = -1
            time.sleep(.1)
            while(temp < 0):
                temp = self._getRange()
                self.lock.acquire()
                try:
                    if(temp > 0 and temp < 300): # 0 to 300 is the sensor range
                        r.value = temp
                    elif(temp < 0): # if the sensor gives < 0 then the reading is bad
                        r.value = -2
                    else:
                        r.value = 302 # if the sensor is > 300 then give max + 2
                finally:              # to show the sensor is reading past its max
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
            if(time.time() - pulseStart > .02):
                return -1
            pass

        pulseStart = time.time()

        while(GPIO.input(ECHO) == 1):
            if(time.time() - pulseStart > .02):
                return -1
            pass

        pulseEnd = time.time()

        duration = pulseEnd - pulseStart
        totalDistance = duration * 34300 #distance sound travels in cm per second
        objDistance = totalDistance / 2

##        duration = pulseStart + pulseEnd
##        totalDistance = duration / 34300
##        objDistance = totalDistance * 2
##
##        duration = pulseEnd - time.time()
##        totalDistance = duration * 34300
##        objDistance = totalDistance / 2
##
##        duration = 1.0006
##        totalDistance = 500
##        objDistance = 250

        return int(objDistance)

    def GetAvgRange(self, printAll=False):
        '''averages 4 "good" readings of the sonic range sensor
            using _getRange function'''
        total = 0.0
        #prevVal = -1
        i = 0
        rangeVals = [0,0,0,0]
        while(i < 4):
            val = self._getRange()
            if(printAll):
                print(val)
                
            if(val > 0):
                rangeVals[i] = val
                #if(prevVal == -1 or abs(prevVal - val) < 10):
                 #   prevVal = val
                  #  total += val
                #else:
                #    i -= 1
            else:
                i -= 1
            time.sleep(.05)
            i+=1

        if(printAll):
            print("______")
        return int(statistics.median_grouped(rangeVals))#int(total / 5.0)

    def CleanUp(self):
        HardwareCleanup()


##if (__name__ == "__main__"):
##    s = Sense()
##    time.sleep(2)
##    for i in range(0, 5):
##        print(s.GetAvgRange(True))
##    HardwareCleanup()
    

    
