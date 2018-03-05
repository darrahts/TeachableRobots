import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(40, GPIO.OUT)

GPIO.output(40, GPIO.LOW)

for i in range(0,1):
    GPIO.output(40, GPIO.HIGH)
    time.sleep(.1)
    GPIO.output(40, GPIO.LOW)
    time.sleep(.1)


GPIO.cleanup()
