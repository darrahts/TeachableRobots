import RPi.GPIO as GPIO
import smbus
import os
import sys
import termios
import tty
import time

#bus = smbus.SMBus(1)
#gyroAddress = 0x68

#buzzer = 13
#greenLED = 8
#green1LED = 37
#yellowLED = 40
#redLED = 10

panServo = 11
tiltServo = 7

ECHO = 31
TRIG = 33

ARDINT = 40
BUZZER = 18

TILT_DOWN_MAX = 160
TILT_CENTER = 135
TILT_UP_MAX = 70

PAN_LEFT_MAX = 180
PAN_CENTER = 145
PAN_RIGHT_MAX = 70

panPos = PAN_CENTER
tiltPos = TILT_CENTER


def Setup():
    GPIO.setmode(GPIO.BOARD)


    #GPIO.setup(buzzer, GPIO.OUT)
    #GPIO.setup(greenLED, GPIO.OUT)
    #GPIO.setup(green1LED, GPIO.OUT)
    #GPIO.setup(yellowLED, GPIO.OUT)
    #GPIO.setup(redLED, GPIO.OUT)

    GPIO.setup(panServo, GPIO.OUT)
    GPIO.setup(tiltServo, GPIO.OUT)

    GPIO.setup(ARDINT, GPIO.OUT)
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG, GPIO.LOW)
    GPIO.output(ARDINT, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)

    print(os.getcwd())
    os.chdir("../src")
    os.system("sudo ./ServoBlaster/user/servod")
    os.system("echo 0={} > /dev/servoblaster".format(TILT_CENTER))
    os.system("echo 1={} > /dev/servoblaster".format(PAN_CENTER))
    print("initialized.")
    os.chdir("../RobotCode")

    return


def TriggerInterrupt():
    GPIO.output(ARDINT, GPIO.HIGH)
    time.sleep(.1)
    GPIO.output(ARDINT, GPIO.LOW)
    return

def GetKey():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    k = None
    try:
        k = os.read(fd, 3)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    key = str(k)
    key = key.replace("b", "")
    key = key.replace("'", "")
    return key

def HardwareCleanup():
    GPIO.cleanup()
    os.system("sudo killall servod")
    return

def Tilt(direction):
    global tiltPos
    if direction == 1: #up
        os.system("echo 0=-1 > /dev/servoblaster")
        tiltPos -= 1
    elif direction == 0: #center
        os.system("echo 0={} > /dev/servoblaster".format(TILT_CENTER))
        tiltPos = TILT_CENTER
    elif direction == 2: #down
        os.system("echo 0=+1 > /dev/servoblaster")
        tiltPos += 1
    return

def Pan(direction):
    global panPos
    if direction == 3: #left
        os.system("echo 1=+1 > /dev/servoblaster")
        panPos += 1
    elif direction == 0: #center
        os.system("echo 1={} > /dev/servoblaster".format(PAN_CENTER))
        panPos = PAN_CENTER
    elif direction == 4: #right
        os.system("echo 1=-1 > /dev/servoblaster")
        panPos -= 1
    return

def PanPos():
    global panPos
    return panPos

def TiltPos():
    global tiltPos
    return tiltPos


def Buzz(msec, tone):
    period = 1.0 / int(tone)
    delay = period / 2
    cycles = int(.5 * int(tone))
    t1 = time.time()
    #for i in range(cycles):
    while(time.time()-t1 < (msec/1000)):
        GPIO.output(BUZZER, True)
        time.sleep(delay)
        GPIO.output(BUZZER, False)
        time.sleep(delay)
    return

