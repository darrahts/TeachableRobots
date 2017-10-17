import RPi.GPIO as GPIO
import time
from Hardware import *



class Sense:
  def __init__(self):
    self.ECHO = ECHO
    self.TRIG = TRIG

    
  def SonicRange(self):
    time.sleep(0.5)
    GPIO.output(self.TRIG, True)
    time.sleep(0.00001)
    GPIO.output(self.TRIG,False)
    pulse_start = time.time()
    while GPIO.input(self.ECHO)==0:
      pulse_start = time.time()
    while GPIO.input(self.ECHO)==1:
      pulse_end = time.time()
    pulse_duration = pulse_end-pulse_start
    distance = pulse_duration*17150
    return distance
  
s = Sense()

try:
  while(True):
    print(s.SonicRange());
    time.sleep(.5)

except KeyboardInterrupt:
  GPIO.cleanup()
