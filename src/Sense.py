
 

import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
 
#set GPIO Pins
GPIO_TRIGGER = 13
GPIO_ECHO = 22
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():

 
    StartTime = time.time()
    StopTime = time.time()

    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        pass

    StartTime = time.time()
    
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        pass

    StopTime = time.time()

        
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        time.sleep(2)
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(.5)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
