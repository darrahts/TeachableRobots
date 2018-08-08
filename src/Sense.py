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

        #   args=self.currentRange means the currentRange gets passed to the function
        self.rangeProcess = Process(target=self.GetRangeContinuous, args=(self.currentRange,))
        self.rangeProcess.e = Event()
        #self.rangeProcess.daemon = True
        

    def GetRange(self):
        '''returns the current range value'''
        return self.currentRange.value

    def GetRangeContinuous(self, r):
        '''Continuously updates the currentRange (r) with an averaging grouped median'''
        while(not self.finished.value):
            self.lock.acquire()
            try:
                r.value = self.GetAvgRange()
            finally:
                self.lock.release()
        return

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

    def _GetRange(self):
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(.005)
        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(.000012)
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(.00006)

        start = time.time()
        timer = time.time()
        
        while(GPIO.input(ECHO) == 0 and time.time() - timer < .05):
            start = time.time()


        stop = time.time()
        timer = time.time()
        
        while(GPIO.input(ECHO) == 1 and time.time() - timer < .05):
            stop = time.time()

        total = stop - start
        dist = (total * 34300) / 2
        return dist

    def _getRange(self):
        '''the actual function to detect the range of an object.
            returns -1 if it takes too long (i.e. random error) '''
        pulseStart = time.time()
        pulseEnd = time.time()

        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(.1)

        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(.00001)
        GPIO.output(TRIG, GPIO.LOW)

        while(GPIO.input(ECHO) == 0):
            if(time.time() - pulseStart > .04):
                return -1
            pass

        pulseStart = time.time()

        while(GPIO.input(ECHO) == 1):
            if(time.time() - pulseStart > .04):
                return -1
            pass

        pulseEnd = time.time()

        duration = pulseEnd - pulseStart
        totalDistance = duration * 34300 #distance sound travels in cm per second
        objDistance = totalDistance / 2

##        duration = pulseStart + pulseEnd
##        totalDistance = duration / 34300
##        objDistance = totalDistance * 2

        return int(objDistance)

    def GetAvgRange(self, printAll=False):
        '''averages 4 "good" readings of the sonic range sensor
            using _getRange function'''
        total = 0.0
        #prevVal = -1
        i = 0
        rangeVals = [0,0,0,0,0]
        while(i < 5):
            val = self._GetRange()
            if(printAll):
                print(val)
            rangeVals[i] = val
            time.sleep(.06)
            i+=1

        if(printAll):
            print("______")
        print(rangeVals)
        return int(statistics.median_grouped(rangeVals))

    def CleanUp(self):
        HardwareCleanup()


##if (__name__ == "__main__"):
##    s = Sense()
##    time.sleep(2)
##    for i in range(0, 100):
##        print(s.GetAvgRange())
####    rangeVals = [0,0,0,0,0]
####    rangeVals[0] = s._GetRange()
####    for i in range(1, 31):
####        rangeVals[i%5] = s._GetRange()
####        if(i%5 == 0):
####            print(rangeVals)
####            print(": ", end= "")
####            print(int(statistics.median_grouped(rangeVals)))
####        
####        time.sleep(.1)
##    HardwareCleanup()
    

    
