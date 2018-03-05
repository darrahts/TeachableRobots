import RPi.GPIO as GPIO
import smbus
import os
import sys
import termios
import tty

#bus = smbus.SMBus(1)
#gyroAddress = 0x68

#buzzer = 13
#greenLED = 8
#green1LED = 37
#yellowLED = 40
#redLED = 10

#panServo = 11
#tiltServo = 7

ECHO = 22
TRIG = 16




GPIO.setmode(GPIO.BOARD)


#GPIO.setup(buzzer, GPIO.OUT)
#GPIO.setup(greenLED, GPIO.OUT)
#GPIO.setup(green1LED, GPIO.OUT)
#GPIO.setup(yellowLED, GPIO.OUT)
#GPIO.setup(redLED, GPIO.OUT)

#GPIO.setup(panServo, GPIO.OUT)
#GPIO.setup(tiltServo, GPIO.OUT)

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)



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
    return

def Tilt(direction):
    if direction == "u":
        os.system("echo 0=-1 > /dev/servoblaster")
    elif direction == "c":
        os.system("echo 0=130 > /dev/servoblaster")
    elif direction == "d":
        os.system("echo 0=+1 > /dev/servoblaster")
    return

def Pan(direction):
    if direction == "l":
        os.system("echo 1=+1 > /dev/servoblaster")
    elif direction == "c":
        os.system("echo 1=150 > /dev/servoblaster")
    elif direction == "r":
        os.system("echo 1=-1 > /dev/servoblaster")
    return

#os.system("sudo ./ServoBlaster/user/servod")
#os.system("echo 0=135 > /dev/servoblaster")
#os.system("echo 1=150 > /dev/servoblaster")

#print("done")

#os.system("sudo killall servod")

'''
try:
    while(True):
        direction = GetKey()
        
        if direction == "u":
            os.system("echo 0=-1 > /dev/servoblaster")
        elif direction == "j":
            os.system("echo 0=130 > /dev/servoblaster")
        elif direction == "m":
            os.system("echo 0=+1 > /dev/servoblaster")
            
        if direction == "h":
            os.system("echo 1=+1 > /dev/servoblaster")
        elif direction == "k":
            os.system("echo 1=150 > /dev/servoblaster")
        elif direction == "l":
            os.system("echo 1=-1 > /dev/servoblaster")

except KeyboardInterrupt:
    GPIO.cleanup()
'''
