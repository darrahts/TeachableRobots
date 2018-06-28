#######  IMPORTS   #######
import RPi.GPIO as GPIO
import time
import datetime
from EmailHandler import EmailSender
import picamera

#######   VARIABLES  ######
led = 7
sensor = 13
buzzer = 15
camera = picamera.PiCamera()


#######  SETUP   #######
GPIO.setmode(GPIO.BOARD) #this lets the pi know the numbering system for our variables
GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(led, GPIO.OUT) #our LED is an output
GPIO.output(led, GPIO.LOW) #make sure its off to start

mailMan = EmailSender("ecirlt2017@gmail.com")

#######  FUNCTIONS #######    

def buzz(tone):
    period = 1.0 / int(tone)
    delay = period / 2
    cycles = int(.25 * int(tone))
    for i in range(cycles):
        GPIO.output(buzzer, True)
        time.sleep(delay)
        GPIO.output(buzzer, False)
        time.sleep(delay)
    return

def alert(tone):
    buzz(tone)
    time.sleep(.20)
    GPIO.output(buzzer, GPIO.LOW)
    buzz(tone)
    time.sleep(.20)
    GPIO.output(buzzer, GPIO.LOW)
    buzz(tone)
    time.sleep(.20)
    GPIO.output(buzzer, GPIO.LOW)
    buzz(tone)
    time.sleep(.20)
    GPIO.output(buzzer, GPIO.LOW)
    buzz(tone)
    time.sleep(.20)
    GPIO.output(buzzer, GPIO.LOW)
    return


def capture():
	timeNow = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
	fileName = timeNow + ".jpg"
	camera.capture(fileName)
	return fileName


def detectIntruders():
    print("initializing...")
    time.sleep(3)
    print("initialized.")
    while(True):
        if(GPIO.input(13) == GPIO.HIGH):
            print("intruder detected.")
            evidence = capture()
            mailMan.AttachImage(evidence)
            mailMan.SetMessageData(destEmail="your_email@gmail.com", "subject here", "body here")
            mailMan.SendEmail(evidence, msg)
            GPIO.output(led, GPIO.HIGH)
            alert(1000)
            time.sleep(5)
        GPIO.output(led, GPIO.LOW)

#######   MAIN   #######
try:
    detectIntruders()
    
except KeyboardInterrupt: #when you press ctrl c 
    print("goodbye.")


GPIO.cleanup() #makes sure all the gpio pins are off









