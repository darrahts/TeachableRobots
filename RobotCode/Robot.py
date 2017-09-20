
import os
from time import sleep
from threading import Thread

from Hardware import *
#from Vision import *
from Behavior import Behave
from Move import Move
from Sense import Sense
from Communicate import Communicate
import traceback
    

class Robot(object): #147
    def __init__(self):
        self.move = Move()
        self.behave = Behave()
        self.sense = Sense()
        #self.vision = Vision()
        self.stopRetrieving   = False
        self.communicate = Communicate()
        self.retrieveMessagesThread = Thread(target=self.retrieveMessages)
        self.startThread = Thread(target=self.waitToStart)
        #self.retrieveMessagesThread.start()
        
    def retrieveMessages(self):
        while not self.stopRetrieving:
            if len(self.communicate.inbox) > 0:
                self.behave.newMessage()
            sleep(5)


    def quit(self):
        hardwareCleanup()
        self.stopRetrieving = True
        if self.retrieveMessagesThread.isAlive():
            self.retrieveMessagesThread.join()
        return

    def waitToStart(self):
        while wait:
            self.behave.waiting()
            sleep(2)


robot = Robot()

direction = 0
turning = 0
commOpen = False
wait = True
cmd = ""
try:
    robot.startThread.start()
    while True:
        cmd = getKey()
        if cmd == "6":
            wait = False
            robot.startThread.join()
            robot.behave.success()
        if cmd == "q":
            break
        if cmd == "w":
            if direction <= 0:
                print("forward 25")
                robot.move.forward(25)
                direction = 1
                continue
            if direction == 1:
                print("forward 50")
                robot.move.forward(50)
                direction = 2
                continue
            if direction == 2:
                print("forward 75")
                robot.move.forward(75)
                direction = 3
                continue
            if direction == 3:
                print("forward 100")
                robot.move.forward(100)
                direction = 4
                continue
            if direction == 4:
                print("at max speed!")
                continue
            
        if cmd == "s":
            if direction >= 0:
                print("backward 25")
                robot.move.backward(25)
                direction = -1
                continue
            if direction == -1:
                print("backward 50")
                robot.move.backward(50)
                direction = -2
                continue
            if direction == -2:
                print("backward 75")
                robot.move.backward(75)
                direction = -3
                continue
            if direction == -3:
                print("backward 100")
                robot.move.backward(100)
                direction = -4
                continue
            if direction == -4:
                print("at max speed!")
                continue
            
        if cmd == "a":
            if turning <= 0:
                print("left 1")
                robot.move.turn(50, 55)
                turning = 1
                continue
            if turning == 1:
                print("left 2")
                robot.move.turn(60, 70)
                turning = 2
                continue
            if turning == 2:
                print("left 3")
                robot.move.turn(70, 85)
                turning = 3
                continue
            if turning == 3:
                print("left 4")
                robot.move.turn(80, 100)
                turning = 4
                continue
            if turning == 4:
                print("at max left turn!")
                continue

        if cmd == "1":
            robot.move.dimeLeft(50)
            continue

        if cmd == "3":
            robot.move.dimeRight(50)
            continue

        if cmd == "d":
            if turning >= 0:
                print("right 1")
                robot.move.turn(55, 50)
                turning = -1
                continue
            if turning == -1:
                print("right 2")
                robot.move.turn(70, 60)
                turning = -2
                continue
            if turning == -2:
                print("right 3")
                robot.move.turn(85, 70)
                turning = -3
                continue
            if turning == -3:
                print("right 4")
                robot.move.turn(100, 80)
                turning = -4
                continue
            if turning == -4:
                print("at max right turn!")
                continue    
   
        if cmd == "z":
            print("stop")
            robot.move.stop()
            direction = 0
            turning = 0
            continue
            
        if cmd == "u":
            print("tilt up")
            tilt("u")
            continue
        if cmd == "j":
            print("tilt down")
            tilt("d")
        if cmd == "m":
            print("tilt center")
            tilt("c")

        if cmd == "h":
            print("pan left")
            pan("l")
            continue
        if cmd == "k":
            print("pan right")
            pan("r")
        if cmd == "l":
            print("pan center")
            pan("c")

        if cmd == "x":
            print("opening camera preview")
           # robot.vision.preview()
            continue
        if cmd == "v":
            print("closing camera preview")
           # robot.vision.stopPreview()
            continue
        if cmd == "c":
            print("capturing image")
           # robot.vision.capture(-1)
            continue
        if cmd == "":
            path = input("Enter the folder path: ")
          #  robot.vision.setPath(path)
            continue

        if cmd == "i":
            robot.communicate = Communicate()
            robot.retrieveMessagesThread = Thread(target=robot.retrieveMessages)
            robot.retrieveMessagesThread.start()
            robot.stopRetrieving = False
            addr = input("enter the address to connect to or 0.0.0.0 if you are the server: ")
            if addr == "0.0.0.0":
                robot.communicate.setupLine("")
            else:
                robot.communicate.setupLine(addr)
            commOpen = True
            continue
        if cmd == "o":
            print("closing the connection...")
            robot.communicate.sendMessage("connection closed.")
            robot.communicate.closeConnection()
            print("connection closed.")
            commOpen = False
            robot.stopRetrieving = True
            robot.retrieveMessagesThread.join()
            del robot.communicate
            continue
        if cmd == "y" and commOpen:
            msg = input("enter the message to send: ")
            robot.communicate.sendMessage(msg)
            continue
        if cmd == "p" and commOpen:
            if len(robot.communicate.inbox) > 0:
                print(robot.communicate.inbox.pop())
            else:
                print("no messages!")
            continue

            
except Exception as e:
    print(e)
    traceback.print_exc()

finally:
    print(cmd)
    print("quitting")
    robot.quit()












