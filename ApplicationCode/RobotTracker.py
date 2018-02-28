# -*- coding: utf-8 -*-

from teachablerobots.src.Communicate import SocketComm
from teachablerobots.src.GridSpace import *
import math
from time import sleep
#import threading
import ast
from multiprocessing import Process, Queue, Event, Value, Lock, Manager
from ctypes import c_char_p



class Robot():
    ''' 

    Attributes:

        lowColor: The minimum HSV value of the robot to track

        highColor: The maximum HSV value of the robot to track

        robot: An (x, y, w, h) tuple that describes the robots location
            and dimensions

        contour: The contour of the robot

        ellipse: an ((x,y),(w,l), a) tuple where (x,y) is the center,
            (w,l) is the width and length, and a is the angle of rotation.
            Used to track the robots angle.

        heading: The robots relative angle

        dir: the direction the robot is moving, "fwd", "bk"

    Functions:

        SetGoal(self, goal)

        Run(self)

        FindRobot(self, frame)

        FrameOverlay(self, frame)

        LocationToCoordinates(self, location)

        CoordinatesToLocation(self, coordinates)
        
        GetHeading(self, frame)

        DrawGoal(self, goal)

        DrawLine(self, point1, point2)
        
    def DrawPolygon(self, startPoint, sideLength, numberOfSides)
    
'''
    
    def __init__(self, gridSpace, color="green"):

        if(color == "green"):
            self.low = (48, 52, 149)
            self.high = (89, 325, 340)

        if(color == "pink"):
            self.low = (56, 82, 170)
            self.high = (180,271,258)

        if(color == "blue"):
            self.low = (55,132,142)
            self.high = (114,273,273)

        
        self.robot = ((0,0),(0,0), 0)
        self.contour = []
        self.heading = 0
        self.dir = "fwd"
        
        self.rLoc = (0,0)
        self.goal = (0,0)
        
        self.goalFound = False
        self.displayGoals = False
        self.displayGoalLoc = False
        self._finished = False
        
        self.gs = gridSpace
        

        self.m = Manager()
        self.lock = Lock()

        self.location = self.m.Value(c_char_p, b"(-5,-3)")
        self.direction = self.m.Value(c_char_p, b"Right")
        self.distanceTravelled = self.m.Value('i', 0)
          
                                                
        self.robotServer = SocketComm(5580)

        self.robotComm = Process(target=self.GetRobotResponse, args=(self.location,self.direction,self.distanceTravelled,))
        self.robotComm.e = Event()
        self.robotComm.daemon = True
        

        print("waiting to connect to robot...")
        if(self.robotServer.setupLine("") == True):
            print("connected to robot!")
            #print(self.robotServer.address)
            #print(self.robotServer.port)
            print(self.robotServer.connection)
            #print(self.robotServer.connected)
            #print(self.robotServer.finished)
        



    def GetRobotResponse(self, loc, _dir, dist):
        d = dict()
        while(not self.robotServer.finished.value):
            #print("size of inbox: " + str(self.robotServer.inbox.qsize()))
            sleep(1)
            if(not self.robotServer.inbox.empty()):
                temp = ast.literal_eval(self.robotServer.inbox.get())
                self.lock.acquire()
                try:
                    if("location" in temp):
                        loc.value = temp["location"].rstrip().encode('ascii')
                        dist.value = dist.value + 1
                        print("distance travelled: " + str(dist.value))
                        print("location: " + loc.value.decode('ascii'))
                    elif("direction" in temp):
                        _dir.value = temp["direction"].rstrip().encode('ascii')
                        print("direction: " + _dir.value.decode('ascii'))
                    else:
                        print("unknown: " + str(temp))
                finally:
                    self.lock.release()
        return


    def SendCommandSequence(self, seq):
        if(len(seq) == 1 and seq == "0"):
            self.robotServer.sendMessage("0")
            return
        else:
            d = dict()
            d["sequence"] = seq
            self.robotServer.sendMessage(str(d))
        return


    def SendObjective(self, objective):
        d = dict()
        d["objective"] = objective
        self.robotServer.sendMessage(str(d)) # i.e. objective is to drive to first quadrant
        print("sent: " + objective)
        return
        
    def SetGoal(self, goal):
        self.goal = goal
        return


    def Run(self):
        c = 0
        i = 0
        if(self.robotServer.connected):
            #self.P.start()
            self.robotCommThread.start()
            print("starting comm thread")
        print("starting...")
        while(not self._finished):
            #print("length of inbox in loop: " + str(len(self.robotServer.inbox)))
            self.gs.Update(self.FrameOverlay)
            #self.FindRobot()
            #cv2.imshow(self.gs.title, self.gs.window)
            
            key = cv2.waitKey(1) & 0xFF
            if(key == ord("q")):
                self.finished = True
            elif(key == ord("c")):
                cv2.imwrite("picture%i.jpg" %i, window)
                i += 1
                

        self.robotServer.e.set()
        self.robotServer.finished.value = True
        print("closing connection")
        self.robotServer.closeConnection()

            

    def FindRobot(self):
        contours = cv2.findContours(self.gs.processedFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if(len(contours) > 0):
            cont = max(contours, key=cv2.contourArea)
            if(cv2.contourArea(cont) > 200 and cv2.contourArea(cont) < 700):
                temp = cv2.minAreaRect(cont)
                if(abs(temp[0][0] - self.robot[0][0]) > .02 and abs(temp[0][1] - self.robot[0][1]) > .02):
                    self.contour = cont
                    self.robot = temp
        return


    def FrameOverlay(self): #TODO draw point, student name in text area
        if(self.displayGoals):
            self.DrawGoal(self.LocToCoord(self.goal), self.displayGoalLoc)
            
        if(len(self.contour) > 0):
            box = cv2.boxPoints(self.robot)
            box = np.int0(box)
            cv2.drawContours(self.gs.frame, [box], 0, (0, 255, 0), 2)
            
        return self.gs.frame


    def LocToCoord(self, location):
        return (location[0] - self.gs.frameCenter[0]) / 38, (self.gs.frameCenter[1] - location[1]) / 38
    
    
    def CoordToLoc(self, coordinates):
        return (int(coordinates[0] *38 + self.gs.frameCenter[0])), (int(-coordinates[1]*38 + self.gs.frameCenter[1]))

    
    def DrawGoal(self, goal, showXY):
        cv2.circle(self.frame,(goal[0], goal[1]), 2, (220,80,80), 2)
        cv2.circle(self.frame,(goal[0], goal[1]), 7, (220,80,80), 2)
        cv2.circle(self.frame,(goal[0], goal[1]), 12, (220,80,80), 2)
        if(showXY):
            cv2.putText(self.frame, str(self.CoordToLoc(goal)), (goal[0]+10, goal[1]+10), cv2.FONT_HERSHEY_PLAIN, .95, (50,100,200), 2)


    def DrawLine(self, point1, point2):
        cv2.line(self.frame, point1, point2, (255,50,155), 4)
        pass


    def DrawPolygon(self, startPoint, sideLength, numberOfSides):
        pass


    def GetHeading(self, frame):
        pass








    
