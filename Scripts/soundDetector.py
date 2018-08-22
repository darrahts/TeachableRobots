import time
import RPi.GPIO as GPIO
import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server = ("192.168.1.90", 6789)

GPIO.setmode(GPIO.BOARD)

pin = 7

GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter = 0
clap = 0
played = False

t1 = time.time()
t2 = time.time()

def callback(pin):
    global counter, t1, t2, clap, played
    counter += 1
    if(GPIO.input(pin)):
        t2 = time.time()
        clap += 1
        print("detected event {}".format(counter))
        if(clap >= 2):
            print("clap!!")
            if(not played):
                socket.sendto(str.encode("clap"), server)
                played = True
    else:
        print("event detected but not registered.")
        
GPIO.add_event_detect(pin, GPIO.RISING, bouncetime=50)
GPIO.add_event_callback(pin, callback)

try:
    while(True):
        if(t2 - t1 > .6):
            clap = 0
            t1 = time.time()
            t2 = time.time()
        
except:
    pass

finally:
    GPIO.cleanup()