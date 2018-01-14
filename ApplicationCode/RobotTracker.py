# -*- coding: utf-8 -*-

from VideoStream import *
import cv2
import imutils
import numpy as np
import math
from time import sleep


class GridSpace:
    ''' This class builds the grid area for the robot and overlays basic
    features such as the center, a bounding box, and a text area.

    Attributes:

        title: Title of the window

        vs: Video stream, 0 is for webcam

        frame: grabbed frame from the stream

        frameCenter: the manually computed center for the grid space

        textArea: Space on the right of the window for generated text

    Functions:

        FrameOverlay(self, frame)

        ProcessFrame(self, frame, low, high)
'''
    
    title = "Robot Grid Space"
    cv2.namedWindow(title)
    vs = WebcamVideoStream(0).start()
    frame = vs.read()
    frame = imutils.resize(frame, width=640, height=480) 
    frameCenter = ((frame.shape[1] // 2) + 21, (frame.shape[0] // 2) + 11)
    textArea = np.zeros((frame.shape[0],550,3),dtype=np.uint8)

    square = np.ndarray([4,2], dtype=int)
    square[0] = [130, 40]
    square[1] = [130, 455]
    square[2] = [550, 455]
    square[3] = [550, 40]


    def FrameOverlay(self, frame):
        ''' Builds the general output window.

        Args:

            frame: the frame to modify
    '''

        cv2.drawContours(self.frame, [self.square], -1, (0, 255, 0), 2)
        cv2.circle(self.frame, (self.frameCenter[0],self.frameCenter[1]), 15, (0,255,255), 2)
        
        #   draw the axis tick marks
        j = 152
        for i in range(0, 5):
            cv2.line(self.frame, (j, 245), (j, 255), (0, 255, 255), 3)
            j += 37

        k = 379
        for i in range(0, 5):
            cv2.line(self.frame, (k, 245), (k, 255), (0, 255, 255), 3)
            k += 38

        j = 53
        for i in range(0, 5):
            cv2.line(self.frame, (334, j), (344, j), (0, 255, 255), 3)
            j += 39

        k = 290
        for i in range(0, 5):
            cv2.line(self.frame, (334, k), (344, k), (0, 255, 255), 3)
            k += 36

        maskk = frame.copy()
        for i in range(0, len(frame[0])):
            for j in range(0, len(frame)):
                if(i < 125 or i > 555 or j < 32 or j > 460):
                    maskk[j][i] = (0,0,0)

        cv2.bitwise_and(maskk, self.frame, self.frame, mask=None)

        return 


    def ProcessFrame(self, frame, low, high):
        ''' Converts the frame to HSV, then masks the frame with the
        chosen color, and finally performs erosion and dialation.

            Args:

                frame: The frame to process

                low: The minimum HSV value to match

                high: The maximum HSV value to match

            Returns:

                The processed frame
    '''
        #lower = np.array([100,100,100])
        #upper = np.array([255,255,255])
        #mask = cv2.inRange(frame, lower, upper)
        #res = cv2.bitwise_and(frame, frame, mask=mask)
        #cv2.imshow("result", res)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = cv2.inRange(frame, low, high)
        erode = cv2.erode(color, None, iterations=2)
        dialate = cv2.dilate(erode, None, iterations=2)
        return dialate



class Robot(GridSpace):
    ''' This class inherits from GridSpace and is used to track a robot
    on said gridspace.

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
    
    def __init__(self):
        self.lowColor = (65, 115, 0)
        self.highColor = (150, 200, 60)
        #self.lowColor = (60, 140, 0)
        #self.highColor = (157, 200, 130)        
        #self.lowColor = (111,150,48)
        #self.highColor = (145,185,128)        
        #self.lowColor = (77,162,102)
        #self.highColor = (139, 204,138)        
        #self.lowColor = (66, 113, 62)
        #self.highColor = (125, 150, 104)        
        #self.lowColor = (60, 120, 50)
        #self.highColor = (125, 170, 100)
        #self.lowColor = (86, 143, 76)
        #self.highColor = (142, 183, 133)
        self.robot = 0,0,0,0
        self.contour = []
        self.ellipse = ((0,0),(0,0), 0)
        self.heading = 0
        self.dir = "fwd"
        
        self.rLoc = (0,0)
        self.goal = (0,0)
        self.goalFound = False
        self.displayGoals = False

        
    def SetGoal(self, goal):
        self.goal = goal


    def Run(self):
        c = 0
        i = 0
        while(True):
            self.frame = self.vs.read()
            self.frame = imutils.resize(self.frame, width=640, height=480)
            self.frameCopy = self.frame.copy()
           
            f = super().ProcessFrame(self.frame, self.lowColor, self.highColor)
            moments = self.FindRobot(f)
            #if(abs(self.rLoc[0] - self.goal[0]) < .5 and abs(self.rLoc[1] - self.goal[1] < .5)):
            #    self.goalFound = True
            #    c +=1

            self.FrameOverlay(self.frame, "", "")
            window = np.hstack([self.frame,self.textArea])
            #window = self.frame
            cv2.imshow(self.title, window)

##            if(self.goalFound and c == 10):
##                x = input("pick a new goal in the form x,y or q to quit: ")
##                if(x == "q"):
##                    break
##                y = x.split(",")
##                self.goal = (int(y[0]), int(y[1]))
##                self.goalFound = False
##                c = 0


            key = cv2.waitKey(1) & 0xFF
            if(key == ord("q")):
                break
            elif(key == ord("c")):
                cv2.imwrite("picture%i.jpg" %i, window)
                i += 1
            

    def FindRobot(self, frame):
        contours = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if(len(contours) > 0):
            cont = max(contours, key=cv2.contourArea)
            if(cv2.contourArea(cont) > 80 and cv2.contourArea(cont) < 700):
                rect = cv2.boundingRect(cont)
                if(abs(self.robot[0] - rect[0]) < 2 or abs(self.robot[1] - rect[1]) < 2):
                    return 0
                else:
                    self.robot = rect
                    self.contour = cont
                    M = cv2.moments(cont)
                return M
            else:
                return -1
        else:
            return -1


    def FrameOverlay(self, frame, msg, loc): #TODO draw point, student name in text area
        super().FrameOverlay(self.frame)
        goal = self.LocationToCoordinates(self.goal)
        if(self.displayGoals):
            self.DrawGoal(goal)
        #self.DrawGoal(self.LocationToCoordinates((3,2)))
        #self.DrawGoal(self.LocationToCoordinates((-3, 1)))
        #self.DrawGoal(self.LocationToCoordinates((1, 4)))
        self.rLoc = self.CoordinatesToLocation(self.robot)
            
        cv2.putText(self.frame, "(0,0)", (self.frameCenter[0],self.frameCenter[1]+30), cv2.FONT_HERSHEY_PLAIN, .95, (0,255,250), 2)
        #cv2.putText(self.frame, "(%.1f" % self.rLoc[0] + ", %.1f)" %self.rLoc[1], (self.robot[0]+15,self.robot[1]+30), cv2.FONT_HERSHEY_PLAIN, .95, (50,100,200), 2)
        
        #cv2.putText(self.textArea, "Heading: %.2f" % self.ellipse[2], (10, 20), 3, .7, (100,200,100), 1)
        #cv2.circle(self.textArea, (208,8), 2, (100,200,100), 1)

        #cv2.putText(self.textArea, "Goal: " + str(self.goal), (10, 50), 3, .7, (100,200,100), 1)

        if(len(self.contour) > 0):
            self.ellipse = cv2.fitEllipse(self.contour)
            w = self.ellipse[1][0] * 1.25
            l = self.ellipse[1][1] * 1.25
            cv2.ellipse(self.frame, (self.ellipse[0],(w,l),self.ellipse[2]), (0,255,0), 2)

        #if(self.goalFound):
        #    cv2.putText(self.textArea, "Goal Found!", (10, 100), 3, .7, (100,200,100), 1)
        
        return


    def LocationToCoordinates(self, location):
        return (int(location[0] *38 + self.frameCenter[0])), (int(-location[1]*38 + self.frameCenter[1]))


    def CoordinatesToLocation(self, coordinates):
        return (coordinates[0] - self.frameCenter[0]) / 38, (self.frameCenter[1] - coordinates[1]) / 38
    

    def DrawGoal(self, goal):
        cv2.circle(self.frame,(goal[0], goal[1]), 2, (220,80,80), 2)
        cv2.circle(self.frame,(goal[0], goal[1]), 7, (220,80,80), 2)
        cv2.circle(self.frame,(goal[0], goal[1]), 12, (220,80,80), 2)
        cv2.putText(self.frame, str(self.CoordinatesToLocation(goal)), (goal[0]+10, goal[1]+10), cv2.FONT_HERSHEY_PLAIN, .95, (50,100,200), 2)
        pass


    def DrawLine(self, point1, point2):
        cv2.line(self.frame, point1, point2, (255,50,155), 4)
        pass


    def DrawPolygon(self, startPoint, sideLength, numberOfSides):
        pass


    def GetHeading(self, frame):
        pass












    
