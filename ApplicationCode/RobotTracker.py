# -*- coding: utf-8 -*-

from teachablerobots.src.Communicate import SocketComm
from teachablerobots.src.GridSpace import *
import math
from time import sleep
import threading
import ast





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
        self.lowColor = (40, 90, 0)
        self.highColor = (150, 200, 60)
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
        self.finished = False


                                                
        self.robotCommThread = threading.Thread(target=self.GetResponse)
        self.robotCommThread.e = threading.Event()
        self.robotServer = SocketComm()
        self.robotServer.port = 5680

        print("waiting to connect to robot...")
        if(self.robotServer.setupLine("") == True):
            print("connecteddd!")
        
        self.location = "(-5,-3)"
        self.direction = "Right"
        self.message = ""
        self.distanceTravelled = 0

        self.points = [(2,-2), (2,1), (-2,1), (1,4)]
        

        amazon = cv2.imread("icons/amazon.png")
        office = cv2.imread("icons/office.png")
        office2 = cv2.imread("icons/office2.png")
        office3 = cv2.imread("icons/office3.png")


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
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = cv2.inRange(frame, low, high)
        erode = cv2.erode(color, None, iterations=2)
        dialate = cv2.dilate(erode, None, iterations=2)
        return dialate



    def GetResponse(self):
        print("comm opened.")
        while(not self.robotServer.finished):
            print("here")
            if(len(self.robotServer.inbox) > 0):
                temp = ast.literal_eval(self.robotServer.inbox.pop())
                if("location" in temp):
                    print("location: " + temp["location"])
                    self.location = temp["location"]
                    self.distanceTravelled += 1
                    print("distance travelled: " + str(self.distanceTravelled))
                if("direction" in temp):
                    print("direction: " + temp["direction"])
                    self.direction = temp["direction"]
                if("message" in temp):
                    print("message: " + temp["message"])
                    self.message = temp["message"]
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
            self.robotCommThread.start()
            #self.SendObjective("rLoc[0] > 0 and rLoc[1] > 0")
        print("starting...")
        while(not self.finished):
            self.Update(lambda: None)
            #self.frame = self.vs.read()
            #self.frame = imutils.resize(self.frame, width=640, height=480)
            #self.frame = cv2.UMat(self.frame)
            #self.frameCopy = self.frame.copy()
           
            f = self.ProcessFrame(self.frame, self.lowColor, self.highColor)
            moments = self.FindRobot(f)
            #if(abs(self.rLoc[0] - self.goal[0]) < .5 and abs(self.rLoc[1] - self.goal[1] < .5)):
            #    self.goalFound = True
            #    c +=1

            self.FrameOverlay()
            #self.frame = cv2.UMat.get(self.frame)
            self.window = np.hstack([self.frame,self.textArea])
            #window = self.frame
            cv2.imshow(self.title, self.window)


            key = cv2.waitKey(1) & 0xFF
            if(key == ord("q")):
                self.finished = True
            elif(key == ord("c")):
                cv2.imwrite("picture%i.jpg" %i, window)
                i += 1
        self.robotServer.e.set()
        self.robotServer.finished = True
        print("closing connection")
        self.robotServer.closeConnection()

            

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
                    self.moments = cv2.moments(cont)
            else:
                return -1
        else:
            return -1


    def FrameOverlay(self): #TODO draw point, student name in text area
        super().FrameOverlay()
        #amazon = self.LocationToCoordinates(self.points[0])
        #office1 = self.LocationToCoordinates(self.points[1])
        #office2 = self.LocationToCoordinates(self.points[2])
        #office3 = self.LocationToCoordinates(self.points[3])
        if(self.displayGoals):
            self.DrawGoal(self.LocationToCoordinates(self.goal), self.displayGoalLoc)
            #self.DrawGoal(amazon, self.displayGoalLoc)
            #self.DrawGoal(office1, self.displayGoalLoc)
            #self.DrawGoal(office2, self.displayGoalLoc)
            #self.DrawGoal(office3, self.displayGoalLoc)

        self.rLoc = self.CoordinatesToLocation(self.robot)
            
        cv2.putText(self.frame, "(0,0)", (self.frameCenter[0],self.frameCenter[1]+30), cv2.FONT_HERSHEY_PLAIN, .95, (0,255,250), 2)
        #cv2.putText(self.frame, "(%.1f" % self.rLoc[0] + ", %.1f)" %self.rLoc[1], (self.robot[0]+15,self.robot[1]+30), cv2.FONT_HERSHEY_PLAIN, .95, (50,100,200), 2)
        
        #cv2.putText(self.textArea, "Heading: %.2f" % self.ellipse[2], (10, 20), 3, .7, (100,200,100), 1)
        #cv2.circle(self.textArea, (208,8), 2, (100,200,100), 1)

        cv2.putText(self.textArea, "Direction: " + self.direction, (0, 20), 3, .5, (100,200,100), 1)
        cv2.putText(self.textArea, "Location: " + self.location, (200, 20), 3, .5, (100,200,100), 1)
        cv2.putText(self.textArea, "Move Count: " + str(self.distanceTravelled), (400, 20), 3, .5, (100,200,100), 1)
        
        
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


r = Robot()
r.Run()







    
