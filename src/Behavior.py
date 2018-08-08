######    IMPORTS    ######
import time
from time import time, sleep
import multiprocessing
from Hardware import *
import os


#test
#waiting
#happy
#tryAgain
#lowBattery
#newMessage
#success
#ready
#hint
#refuse


class Behave(object):
    ######     SETUP     ######
    #this initializes the board and output pins
    def __init__(self):
        Setup()
        self.buzzer = BUZZER
        #self.green = greenLED
        #self.green1 = green1LED
        #self.yellow = yellowLED
        #self.red = redLED

    ######     TEST     ######
    #this moves the servo, buzzes, and illumantes all the leds
    def test(self):
        print("test")
        GPIO.output(self.green1, GPIO.HIGH)
        sleep(.25)
        GPIO.output(self.green1, GPIO.LOW)
        sleep(1)
        GPIO.output(self.red, GPIO.HIGH)
        sleep(.25)
        GPIO.output(self.red, GPIO.LOW)
        sleep(1)
        GPIO.output(self.yellow, GPIO.HIGH)
        sleep(.25)
        GPIO.output(self.yellow, GPIO.LOW)
        sleep(1)
        GPIO.output(self.green, GPIO.HIGH)
        sleep(.25)
        GPIO.output(self.green, GPIO.LOW)
        for i in range(0,5):
            self.buzz(200)
            sleep(.15)
        return


    ######     WAITING     ######
    #this behavior signifies the robot is waiting for something external to happen
    def waiting(self):
        print("waiting")
        GPIO.output(self.red, GPIO.HIGH)
        self.buzz(400)
        sleep(.07)
        GPIO.output(self.red, GPIO.LOW)
        sleep(.07)
        GPIO.output(self.red, GPIO.HIGH)
        self.buzz(200)
        sleep(.07)
        GPIO.output(self.red, GPIO.LOW)
        sleep(.07)
        return

    ######     HAPPY     ######
    #this signifies the robot was pleased with something external or your input
    def happy(self):
        print("happy")
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(1000)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.green1, GPIO.HIGH)
        self.buzz(600)
        GPIO.output(self.green1, GPIO.LOW)
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(1400)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.green1, GPIO.HIGH)
        self.buzz(1100)
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(1600)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.green1, GPIO.LOW)
        return


    def moveServo(self, cmd):
        os.system(cmd)
        return

    ######     TRY AGAIN     ######
    #this behavior signifies you are trying to do something wrong or are not
    #providing the correct input
    def tryAgain(self):
        print("try again")
        GPIO.output(self.red, GPIO.HIGH)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=130 > /dev/servoblaster",))
        p.start()
        #os.system("echo 2=130 > /dev/servoblaster")
        self.buzz(400)
        #sleep(.04)
        GPIO.output(self.red, GPIO.LOW)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=170 > /dev/servoblaster",))
        p.start()
        #os.system("echo 2=170 > /dev/servoblaster")
        #sleep(.04)
        GPIO.output(self.yellow, GPIO.HIGH)
        self.buzz(400)
        #sleep(.07)
        GPIO.output(self.yellow, GPIO.LOW)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=150 > /dev/servoblaster",))
        p.start()
        #os.system("echo 2=150 > /dev/servoblaster")
        sleep(.1)
        del p
        return

    ######     BATTERY LOW     ######
    #if the battery is below a predefined threshold this behavior will execute
    def lowBattery(self):
        print("low battery")
        GPIO.output(self.red, GPIO.HIGH)
        self.buzz(1200)
        self.buzz(900)
        GPIO.output(self.red, GPIO.LOW)
        sleep(.03)
        GPIO.output(self.red, GPIO.HIGH)
        self.buzz(600)
        GPIO.output(self.red, GPIO.LOW)
        sleep(.03)

    def newMessage(self):
        print("new message")
        GPIO.output(self.yellow, GPIO.HIGH)
        self.buzz(1200)
        self.buzz(900)
        GPIO.output(self.yellow, GPIO.LOW)
        sleep(.03)
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(600)
        GPIO.output(self.green, GPIO.LOW)
        sleep(.03)


    ######     READY     ######
    #this behavior signifies the robot is ready to begin its task
    def success(self):
        print("success")
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(700)
        sleep(.01)
        GPIO.output(self.green1, GPIO.HIGH)
        self.buzz(900)
        sleep(.01)
        GPIO.output(self.green, GPIO.LOW)
        self.buzz(900)
        sleep(.01)
        GPIO.output(self.green1, GPIO.LOW)
        self.buzz(1200)
        sleep(.01)
        GPIO.output(self.green, GPIO.HIGH)
        GPIO.output(self.green1, GPIO.HIGH)
        self.buzz(1000)
        sleep(.01)
        GPIO.output(self.green1, GPIO.LOW)
        GPIO.output(self.green, GPIO.LOW)
        self.buzz(1400)
        
        return


    ######     SUCCESS     ######
    #this signifies a task was successfully completed 
    def ready(self):
        print("ready")
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(300)
        GPIO.output(self.green, GPIO.LOW)
        #sleep(.015)
        GPIO.output(self.green1, GPIO.HIGH)
        self.buzz(700)
        #sleep(.015)
        GPIO.output(self.green1, GPIO.LOW)
        GPIO.output(self.green, GPIO.HIGH)
        self.buzz(1400)
        
        GPIO.output(self.green, GPIO.LOW)
        sleep(.2)
        GPIO.output(self.green1, GPIO.HIGH)
        self.buzz(1400)
        #sleep(.1)
        GPIO.output(self.green1, GPIO.LOW)
        return

    ######     HINT     ######
    #this behavior signifies the robot is trying to tell you something
    #####NEED TO CHANGE TO THE TILT SERVO WHEN INSTALLED
    def hint(self):
        print("hint")
        GPIO.output(self.green, GPIO.HIGH)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=135 > /dev/servoblaster",))
        p.start()
        self.buzz(800)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.yellow, GPIO.HIGH)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=150 > /dev/servoblaster",))
        p.start()
        self.buzz(400)
        GPIO.output(self.yellow, GPIO.LOW)
        GPIO.output(self.green, GPIO.HIGH)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=135 > /dev/servoblaster",))
        p.start()
        self.buzz(800)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.yellow, GPIO.HIGH)
        p = multiprocessing.Process(target=self.moveServo, args=("echo 2=150 > /dev/servoblaster",))
        p.start()
        sleep(.1)
        self.buzz(400)
        GPIO.output(self.yellow, GPIO.LOW)
        del p
        return

        ######     REFUSE     ######
    #this behavior signifies the robot will not comply with your directives
    def refuse(self):
        print("not doing it")
        
    def buzz(self, msec, tone):
        period = 1.0 / int(tone)
        delay = period / 2
        cycles = int(.5 * int(tone))
        t1 = time.time()
        #for i in range(cycles):
        while(time.time()-t1 < (msec/1000)):
            GPIO.output(self.buzzer, True)
            sleep(delay)
            GPIO.output(self.buzzer, False)
            sleep(delay)
        return




b = Behave()
b.buzz(125, 400)
sleep(.1)
b.buzz(250, 800)

GPIO.cleanup()





