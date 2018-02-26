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
    
    def __init__(self, gridSpace):
        self.low = (33, 77, 0)
        self.high = (165, 215, 75)
        self.robot = 0,0,0,0
        self.contour = []
        self.ellipse = ((0,0),(0,0), 0)
        self.heading = 0
        self.dir = "fwd"
        
        self.rLoc = (0,0)
        self.goal = (0,0)
        
        self.goalFound = False
        self.displayGoals = False
        self.displayGoalLoc = False
        self._finished = False
        self.frame = gridSpace.frame
        self.frameCenter = gridSpace.frameCenter
        
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
        

##        self.points = [(2,-2), (2,1), (-2,1), (1,4)]
        
##
##        amazon = cv2.imread("icons/amazon.png")
##        office = cv2.imread("icons/office.png")
##        office2 = cv2.imread("icons/office2.png")
##        office3 = cv2.imread("icons/office3.png")
##
##
        



    def GetRobotResponse(self, loc, _dir, dist):
        #print("watching inbox")
        #print(self.robotServer.address)
        #print(self.robotServer.port)
        #print(self.robotServer.connection)
        #print(self.robotServer.otherAddress)
        #print(self.robotServer.connected)
        #print(self.robotServer.finished)
        #print("inbox at: " + str(id(self.robotServer.inbox)))
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
            
##            key = cv2.waitKey(1) & 0xFF
##            if(key == ord("q")):
##                self.finished = True
##            elif(key == ord("c")):
##                cv2.imwrite("picture%i.jpg" %i, window)
##                i += 1
                
        #self.P.e.set()
        #self.P.terminate()
        #self.P.join()
        self.robotServer.e.set()
        self.robotServer.finished.value = True
        print("closing connection")
        self.robotServer.closeConnection()

            

    def FindRobot(self, frame):
        #frame = self.ProcessFrame(self.low, self.high)
        contours = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if(len(contours) > 0):
            cont = max(contours, key=cv2.contourArea)
            if(cv2.contourArea(cont) > 200 and cv2.contourArea(cont) < 700):
                rect = cv2.boundingRect(cont)
                self.robot = rect
                self.contour = cont
                #self.moments = cv2.moments(cont)
            else:
                return -1
        else:
            return -1


    def FrameOverlay(self): #TODO draw point, student name in text area
        #super().FrameOverlay()
        if(self.displayGoals):
            self.DrawGoal(self.LocationToCoordinates(self.goal), self.displayGoalLoc)


        self.rLoc = self.CoordinatesToLocation(self.robot)
            
        cv2.putText(self.frame, "(0,0)", (self.frameCenter[0],self.frameCenter[1]+30), cv2.FONT_HERSHEY_PLAIN, .95, (0,255,250), 2)
        #cv2.putText(self.frame, "(%.1f" % self.rLoc[0] + ", %.1f)" %self.rLoc[1], (self.robot[0]+15,self.robot[1]+30), cv2.FONT_HERSHEY_PLAIN, .95, (50,100,200), 2)
        
        #cv2.putText(self.textArea, "Heading: %.2f" % self.ellipse[2], (10, 20), 3, .7, (100,200,100), 1)
        #cv2.circle(self.textArea, (208,8), 2, (100,200,100), 1)

        #cv2.putText(self.textArea, "Direction: " + self.direction, (0, 20), 3, .5, (100,200,100), 1)
        #cv2.putText(self.textArea, "Location: " + self.location, (200, 20), 3, .5, (100,200,100), 1)
        #cv2.putText(self.textArea, "Move Count: " + str(self.distanceTravelled), (400, 20), 3, .5, (100,200,100), 1)
        
        
        if(len(self.contour) > 0):
            self.ellipse = cv2.fitEllipse(self.contour)
            w = self.ellipse[1][0] * 1.25
            l = self.ellipse[1][1] * 1.25
            cv2.ellipse(self.frame, (self.ellipse[0],(w,l),self.ellipse[2]), (0,255,0), 2)

        #if(self.goalFound):
        #    cv2.putText(self.textArea, "Goal Found!", (10, 100), 3, .7, (100,200,100), 1)
        
        return self.frame


    def LocationToCoordinates(self, location):
        return (int(location[0] *38 + self.frameCenter[0])), (int(-location[1]*38 + self.frameCenter[1]))


    def CoordinatesToLocation(self, coordinates):
        return (coordinates[0] - self.frameCenter[0]) / 38, (self.frameCenter[1] - coordinates[1]) / 38
    

    def DrawGoal(self, goal, showXY):
        cv2.circle(self.frame,(goal[0], goal[1]), 2, (220,80,80), 2)
        cv2.circle(self.frame,(goal[0], goal[1]), 7, (220,80,80), 2)
        cv2.circle(self.frame,(goal[0], goal[1]), 12, (220,80,80), 2)
        if(showXY):
            cv2.putText(self.frame, str(self.CoordinatesToLocation(goal)), (goal[0]+10, goal[1]+10), cv2.FONT_HERSHEY_PLAIN, .95, (50,100,200), 2)


    def DrawLine(self, point1, point2):
        cv2.line(self.frame, point1, point2, (255,50,155), 4)
        pass


    def DrawPolygon(self, startPoint, sideLength, numberOfSides):
        pass


    def GetHeading(self, frame):
        pass


#gs = GridSpace()

#r = Robot(gs)
#r.Run()







    
