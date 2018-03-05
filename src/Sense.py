import RPi.GPIO as GPIO
import time
from Hardware import *



class Sense:
  def __init__(self):
    self.ECHO = ECHO
    self.TRIG = TRIG

    
  def SonicRange(self):
    GPIO.output(self.TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(self.TRIG, GPIO.LOW)

    pulseStart = time.time()
    pulseEnd = time.time()
    timeout = time.time()

    
    while(GPIO.input(self.ECHO) == 0):# and time.time() - timeout < .55):
      pulseStart = time.time()

    #timeout = time.time()
    
    while(GPIO.input(self.ECHO) == 1):# and time.time() - timeout < .55):
      pulsEnd = time.time()
      
    pulseDuration = pulseEnd - pulseStart
    roundTripDistance = pulseDuration * 34326
    oneWayDistance = roundTripDistance / 2
    
    return oneWayDistance
  
s = Sense()

try:
  print("starting")
  time.sleep(2)
  while(True):
    print(s.SonicRange());
    print("____")
    time.sleep(.5)

except KeyboardInterrupt:
  GPIO.cleanup()
