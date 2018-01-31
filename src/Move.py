from Hardware import *
from time import sleep

class Move:
    def __init__(self):
        self.p1 = pwm1
        self.p2 = pwm2 
        self.vel = 0
        self.dir = 0
        
        
    #************* STOP ***************
    def stop(self):
        if self.vel is not 0:
            mina = int(self.vel/4)
            maxa = int(self.vel) 
            step = int(mina)
            for x in range(maxa, mina-step, -step):
                self.p1.ChangeDutyCycle(x)
                self.p2.ChangeDutyCycle(x)
                #print(x)
                sleep(.25) 
        #self.p1.stop()
        #self.p2.stop()
        GPIO.output(Motor1A,GPIO.LOW)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A,GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        self.vel = 0
        self.dir = 0
        return

        
    #************* FORWARD ***************
    def forward(self, speed):
        mina = int(speed/4)
        maxa = int(speed) 
        step = int(mina)
        GPIO.output(Motor1A,GPIO.HIGH)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A,GPIO.HIGH)
        GPIO.output(Motor2B, GPIO.LOW)
        if self.dir is -1:
            self.stop()
        self.p1.start(10)
        self.p2.start(10)
        for x in range(self.vel, (maxa+5), step):
            self.p1.ChangeDutyCycle(x)
            self.p2.ChangeDutyCycle(x)
            #print(x)
            sleep(.25)
        self.vel = speed
        #self.p1.start(self.vel)
        #self.p2.start(self.vel)
        self.dir = 1
        return
       

    #*********** BACKWARDS **************
    def backward(self, speed):
        mina = int(speed/4)
        maxa = int(speed) 
        step = int(mina)
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor1B,GPIO.HIGH)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor2B,GPIO.HIGH)
        if self.dir is 1:
            self.stop()
        self.p1.start(10)
        self.p2.start(10)
        for x in range(self.vel, (maxa+5), step):
            self.p1.ChangeDutyCycle(x)
            self.p2.ChangeDutyCycle(x)
            #print(x)
            sleep(.25)
        self.vel = speed
        #self.p1.start(self.vel)
        #self.p2.start(self.vel)
        self.dir = -1
        return
       

    #************* TURN ***************
    def turn(self, leftWheelSpeed, rightWheelSpeed):
        la = leftWheelSpeed / 4
        ra = rightWheelSpeed /4
        lStep = la
        rStep = ra
        GPIO.output(Motor1A,GPIO.HIGH)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A,GPIO.HIGH)
        GPIO.output(Motor2B, GPIO.LOW)
        if self.vel is 0:
            self.p1.start(10)
            self.p2.start(10)
            for x in range(0, 4):
                self.p1.ChangeDutyCycle(lStep)
                self.p2.ChangeDutyCycle(rStep)
                #print(x)
                lStep += la
                rStep += ra
                sleep(.25)
        else:
            self.p1.start(leftWheelSpeed)
            self.p2.start(rightWheelSpeed)
        #self.p1.start(leftWheelSpeed)
        #self.p2.start(rightWheelSpeed)
        self.vel = int(max(lStep, rStep))
        self.dir = 1
        return

    #************ DIME LEFT **************
    def dimeLeft(self, speed):
        #print("dimeLeft")
        GPIO.output(Motor1A,GPIO.HIGH)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A,GPIO.LOW)
        GPIO.output(Motor2B, GPIO.HIGH)
        self.p1.start(speed)
        self.p2.start(speed)
        return
        
    #************ DIME RIGHT **************
    def dimeRight(self, speed):
        #print("dimeRight")
        GPIO.output(Motor1A,GPIO.LOW)
        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor2A,GPIO.HIGH)
        GPIO.output(Motor2B, GPIO.LOW)
        self.p1.start(speed)
        self.p2.start(speed)
        return
    



##move = Move()
##sleep(1)
##print("ready left")
##move.dimeLeft(80)
##sleep(.5)
##move.stop()
##sleep(1)
##print("ready right")
##move.dimeRight(80)
##sleep(.5)
##move.stop()
##GPIO.cleanup()




