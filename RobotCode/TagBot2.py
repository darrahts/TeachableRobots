
import os
import serial
from time import sleep
from threading import Thread

from Hardware import *
from Vision import *
from Behavior import Behave
from Move import Move
from Sense import Sense
from Communicate import Communicate
import traceback
    

class Robot(object, port): #147
    def __init__(self):
        self.move = Move()
        self.behave = Behave()
        self.sense = Sense()
        self.vision = Vision()
        self.wait = True
        self.stopRetrieving   = False
        self.communicate = Communicate()
        self.retrieveMessagesThread = Thread(target=self.retrieveMessages)
        self.startThread = Thread(target=self.waitToStart)
        self.arduino = serial.Serial(port, 9600)
        #self.retrieveMessagesThread.start()
        
    def retrieveMessages(self):
        while not self.stopRetrieving:
            if len(self.communicate.inbox) > 0:
                self.behave.newMessage()
            sleep(5)


    def quit(self):
        print("cleaning up hardware...")
        hardwareCleanup()
        print("ending threads...")
        self.stopRetrieving = True
        robot.wait = False
        if self.startThread.isAlive():
            self.startThread.join()
        if self.retrieveMessagesThread.isAlive():
            self.retrieveMessagesThread.join()
        return

    def waitToStart(self):
        while self.wait:
            self.behave.waiting()
            sleep(2)


robot = Robot("/dev/ttyACM0")

direction = 0
turning = 0
commOpen = False
cmd = ""
robot.startThread.start()
try:
    robot.communicate = Communicate()
    robot.retrieveMessagesThread = Thread(target=robot.retrieveMessages)
    robot.retrieveMessagesThread.start()
    robot.stopRetrieving = False
    addr = "0.0.0.0" #= input("enter the address to connect to or 0.0.0.0 if you are the server: ")
    if addr == "0.0.0.0":
        print("Setting up communications...")
        robot.communicate.setupLine("")
    else:
        robot.communicate.setupLine(addr)
    commOpen = True
    print("Connection established.")
    robot.wait = False
    robot.startThread.join()
    robot.behave.ready()
    while(commOpen):
        if len(robot.communicate.inbox) > 0:
            cmd = robot.communicate.inbox.pop()
            print("cmd: " + cmd)
            if(cmd == "abc123"):
                robot.communicate.sendMessage("it worked!")
            elif(cmd == "q"):
                print("closing the connection...")
                robot.communicate.sendMessage("connection closed.")
                robot.communicate.closeConnection()
                print("connection closed.")
                commOpen = False
                robot.communicate.closeConnection()
                robot.stopRetrieving = True
                robot.retrieveMessagesThread.join()
                break
            elif cmd == "w": #forward
                
            elif cmd == "s":
                    
            elif cmd == "a":
                
            elif cmd == "d":
                
            elif cmd == "z":
            
                
            elif cmd == "u":
                tilt("u")
                
            elif cmd == "j":
                tilt("d")
                
            elif cmd == "m":
                tilt("c")

            elif cmd == "h":
                pan("l")
                continue
            elif cmd == "k":
                pan("r")
            elif cmd == "l":
                pan("c")

            elif cmd == "x":
                print("opening camera preview")
                robot.vision.preview()
                continue
            elif cmd == "v":
                print("closing camera preview")
                robot.vision.stopPreview()
                continue
            elif cmd == "c":
                print("capturing image")
                robot.vision.capture(-1)
                continue
            elif cmd == "-":
                path = input("Enter the folder path or c to cancel: ")
                if(path == "c"):
                    continue
                else:
                    robot.vision.setPath(path)
                


except Exception as e:
    print(e)
    traceback.print_exc()

finally:
    
    print("quitting")
    robot.quit()
    












