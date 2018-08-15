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
        self.getRangeP = Process(target=self.GetRangeContinuous, args=(self.currentRange,))
        self.getRangeP.e = Event()
        #self.rangeProcess.daemon = True
        

    def GetRangeContinuous(self, r):
        '''Continuously updates the currentRange (r) with an averaging grouped median'''
        while(not self.finished.value):
            self.lock.acquire()
            try:
                r.value = self.GetAvgRange()
                #print(r.value)
            finally:
                self.lock.release()
        return


    def _GetRange(self):
        '''Gets range from sensor'''
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(.01)
        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(.000011)
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(.00003)

        start = time.time()
        timer = time.time()
        
        while(GPIO.input(ECHO) == 0 and time.time() - timer < .05):
            start = time.time()

        stop = time.time()
        timer = time.time()
        
        while(GPIO.input(ECHO) == 1 and time.time() - timer < .05):
            stop = time.time()

        duration = stop - start
        distanceTravelled = (duration * 34300)
        objectDistance = distanceTravelled / 2

        
        return int(objectDistance)


    def GetAvgRange(self, printAll=False):
        '''averages 5 readings of the sonic range sensor
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
        #print(rangeVals)
        return int(statistics.median_grouped(rangeVals))

    

    def Cleanup(self):
        HardwareCleanup()

        
##
##if (__name__ == "__main__"):
##    s = Sense()
##    for i in range(0, 10):
##        s.currentRange.value = s.GetAvgRange()
##        print(s.currentRange.value)

##if (__name__ == "__main__"):
##    s = Sense()
##    time.sleep(2)
##    for i in range(0, 1):
##        print(s._GetRange())
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
    

    
