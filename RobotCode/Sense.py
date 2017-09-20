import RPi.GPIO as GPIO
import time
from Hardware import *



class Sense:
  def __init__(self):
    self.ECHO = ECHO
    self.TRIG = TRIG
    
    self.ledA = redLED
    self.ledB = yellowLED

    self.pir = pir

    self.PhotoPin = PhotoPin

    self.PhotoPin2 = PhotoPin2

    
  def SonicRange(self):
    print ("Distance Measurement In Progress")
    print ("Allow Module to Settle")
    time.sleep(0.5)
    print ("Settled")
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
  
  def LED(self):
    i = 0
    GPIO.output(self.ledA, 1)
    GPIO.output(self.ledB,1)
    time.sleep(1)
    GPIO.output(self.ledA,0)
    GPIO.output(self.ledB,0)
    
  def PIR(self):
    status = True
    while status:
      i = GPIO.input(self.pir)
      if i == 0:
        print (" No intruders")
      elif i == 1:
        print ("Intruders")
        self.LED()
        status = False
        
  def PhotoRes(self):
    count = 0
    GPIO.output(self.PhotoPin,GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(self.PhotoPin,GPIO.IN)
    while (GPIO.input(self.PhotoPin) == GPIO.LOW):
      count+=1
    return count

  def PhotoRes2(self):
    count = 0
    GPIO.output(self.PhotoPin2,GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(self.PhotoPin2,GPIO.IN)
    while (GPIO.input(self.PhotoPin2) == GPIO.LOW):
      count+=1
    return count

def destroy():
  GPIO.cleanup()
    
def main():
  a = Sensors()
  try:
    print("Distance from object", a.SonicRange(), "cm")
    a.LED()
    a.PIR()
    print("Time to charge short Capacitor", a.PhotoRes(), "loops")
    print("Time to charge tall Capacitor", a.PhotoRes2(), "loops")
    
  except KeyboardInterrupt:
    destroy()
  finally:
    destroy()

