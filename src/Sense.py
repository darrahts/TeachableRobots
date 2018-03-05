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




import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
