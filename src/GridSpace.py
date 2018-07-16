# -*- coding: utf-8 -*-

from teachablerobots.src.Vision import *
import cv2
import numpy as np


class GridSpace(object):
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
    def __init__(self, mode="gui"):

        if(mode == ""):
            self.title = "Robot Grid Space"
            cv2.namedWindow(self.title)
        elif(mode == "gui"):
            pass
        
        self.vs = WebcamVideoStream(-1).start()
        self.frame = self.vs.read()[27:467, 125:565]
        self.frameCenter = ((self.frame.shape[1] // 2), (self.frame.shape[0] // 2) + 5)

        self.frameCopy = self.frame
        self.processedFrame = self.frame
        
        self.square = np.ndarray([4,2], dtype=int)
        self.square[0] = [10, 10]
        self.square[1] = [10, 435]
        self.square[2] = [425, 435]
        self.square[3] = [425, 10]
        self.showMaze = False
        self.showWaypoints = False

        self._finished = False

        self.i = 0 #picture counter 


    def FrameOverlay(self):
        ''' Builds the general output window.

    '''
        cv2.drawContours(self.frame, [self.square], -1, (0, 255, 0), 2)
        cv2.circle(self.frame, (self.frameCenter[0],self.frameCenter[1]), 15, (0,255,255), 2)

      #self.textArea = np.zeros((self.frame.shape[0],440,3),dtype=np.uint8)

        #   draw the axis tick marks

        n1 = 222
        n2 = 232

        n3 = 214
        n4 = 224

        j = 28
        for i in range(0, 5):
            cv2.line(self.frame, (j, n1), (j, n2), (0, 255, 255), 3)
            j += 38

        k = 258
        for i in range(0, 5):
            cv2.line(self.frame, (k, n1), (k, n2), (0, 255, 255), 3)
            k += 38

        j = 26
        for i in range(0, 5):
            cv2.line(self.frame, (n3, j), (n4, j), (0, 255, 255), 3)
            j += 39

        k = 264
        for i in range(0, 5):
            cv2.line(self.frame, (n3, k), (n4, k), (0, 255, 255), 3)
            k += 38

        if(self.showMaze):
            self.DrawMaze(self.frameCopy)
            #self.DrawMaze(self.frame)
        if(self.showWaypoints):
            self.DrawWaypoints(self.frameCopy)
            
        return 


    def DrawWaypoints(self, frame):
        color1 = (0,0,255)
        cv2.circle(frame, (140, 340), 5, color1, 2)
        cv2.circle(frame, (19, 305), 5, color1, 2)
        cv2.circle(frame, (64, 266), 5, color1, 2)
        cv2.circle(frame, (210, 380), 5, color1, 2)
        cv2.circle(frame, (293, 340), 5, color1, 2)
        cv2.circle(frame, (260, 232), 5, color1, 2)
        cv2.circle(frame, (338, 265), 5, color1, 2)
        cv2.circle(frame, (292, 380), 5, color1, 2)
        cv2.circle(frame, (140, 33), 5, color1, 2)
        cv2.circle(frame, (180, 65), 5, color1, 2)
        cv2.circle(frame, (105, 110), 5, color1, 2)
        cv2.circle(frame, (220, 110), 5, color1, 2)
        cv2.circle(frame, (293, 110), 5, color1, 2)
        cv2.circle(frame, (19, 150), 5, color1, 2)
        cv2.circle(frame, (220, 190), 5, color1, 2)
        cv2.circle(frame, (180, 190), 5, color1, 2)
        cv2.circle(frame, (338, 30), 5, color1, 2)
        cv2.circle(frame, (380, 380), 5, color1, 2)
        cv2.circle(frame, (370, 70), 5, color1, 2)
        

    def DrawMaze(self, frame):

        color1 = (0, 0, 255)
        color2 = (0, 255, 0)
        color3 = (255, 0, 0)


        j = 41
        k = 49

        #   scale marks
        cv2.line(frame, (j+13,k+300), (j+13, k+310), color3, 2)
        cv2.line(frame, (j+54,k+300), (j+54, k+310), color3, 2)

        #   VERTICAL LINES

        #-5,5 to -5,3
        cv2.line(frame, (j+2, k), (j+4, 131), color2, 2)

        #-5,2 to -5,-2
        cv2.line(frame, (j+2, 170), (j+2, 287), color2, 2)

        #-4,5 to -4,6
        cv2.line(frame, (j+38, k), (j+38, 10), color2, 2)
        
        #-4,4 to -4,-1
        cv2.line(frame, (j+39, k+40), (j+42, k+200), color2, 2)

        #-3,1 to -3,3
        cv2.line(frame, (j+80,k+81), (j+80, k+157), color2, 2)

        #-3,-2 -3,-3
        cv2.line(frame, (j+82,k+237), (j+82, k+275), color2, 2)

        #-3,-5 to -3,-6
        cv2.line(frame, (j+84,k+347), (j+84, k+385), color2, 2)

        #-2,-1 to -2,-2
        cv2.line(frame, (j+119, k+199), (j+119,k+238), color2, 2)

        #-2,-3 to -2,-4
        cv2.line(frame, (j+119, k+275), (j+119,k+312), color2, 2)
                        
        #-1,5 to -1,2
        cv2.line(frame, (j+155, k), (j+156,k+116), color2, 2)

        #-1,-1 to -1,-4
        cv2.line(frame, (j+158, k+199), (j+158, k+310), color2, 2)

        #1,4 to 1,2
        cv2.line(frame, (j+196, k+39), (j+196, k+116), color2, 2)

        #1,-1 to 1,-3
        cv2.line(frame, (j+197, k+199), (j+197,k+272), color2, 2)

        #1,-4 to 1,-5
        cv2.line(frame, (j+197,k+310), (j+197, k+348), color2, 2)

        #2,-1 to 2,-2
        cv2.line(frame, (j+236, k+199), (j+236, k+238), color2, 2)

        #2,-3 to 2,-4
        cv2.line(frame, (j+236, k+272), (j+236, k+310), color2, 2)

        #2,6 to 2,5
        cv2.line(frame, (j+234, k), (j+234, 10), color2, 2)

        #3,2 to 3,-1
        cv2.line(frame, (j+275, k+116), (j+275, k+199), color2, 2)

        #3,-2 to 3,-3
        cv2.line(frame, (j+275, k+238), (j+275, k+272), color2, 2)

        #4,4 to 4,-1
        cv2.line(frame, (j+314, k+40), (j+314, k+199), color2, 2)

        #5,5 to 5,3
        cv2.line(frame, (j+354, k-1), (j+352, k+72), color2, 2)

        #5,2 to 5,1
        cv2.line(frame, (j+353, k+118), (j+353, k+157), color2, 2)

        #5,-2 to 5,-4
        cv2.line(frame, (j+351,k+238), (j+351,k+310), color2, 2)

        

        #   HORIZONTAL LINES
        

        #-3,-5 to 2,-5
        cv2.line(frame, (j+84,k+348), (j+236,k+348), color2, 2)

        #3,-5 to 5,-5
        cv2.line(frame, (j+275, k+348), (j+351,k+348), color2, 2)

        #1,-4 to 4,-4
        cv2.line(frame, (j+197, k+310), (j+314, k+310), color2, 2)

        #-6,-4 to -2,-4
        cv2.line(frame, (10, k+310), (j+119, k+310), color2, 2)

        #-6,-3 to -4,-3
        cv2.line(frame, (10, k+276), (j+48, k+276), color2, 2)

        #3,-3 to 5,-3
        cv2.line(frame, (j+274, k+275), (j+351, k+275), color2, 2)

        #-5,-2 to -3,-2
        cv2.line(frame, (j, k+238), (j+84, k+238), color2, 2)

        #-4,-1 to 1,-1
        cv2.line(frame, (j+42, k+199), (j+197, k+199), color2, 2)

        #2,-1 to 3,-1
        cv2.line(frame, (j+234, k+199), (j+275, k+199), color2, 2)

        #4,-1 to 6,-1
        cv2.line(frame, (j+316, k+199), (j+386, k+199), color2, 2)

        #-3,1 to 2,1
        cv2.line(frame, (j+81, k+157), (j+236, k+157), color2, 2)

        #3,1 to 4,1
        cv2.line(frame, (j+276, k+157), (j+312, k+157), color2, 2)

        #5,1 to 6,1
        cv2.line(frame, (j+354, k+157), (j+384, k+157), color2, 2)

        #1,2 to 3,2
        cv2.line(frame, (j+198, k+116), (j+275, k+116), color2, 2)

        #-3,3 to -2,3
        cv2.line(frame, (j+81, k+82), (j+116, k+82), color2, 2)

        #2,3 to 4,3
        cv2.line(frame, (j+234,k+78), (j+312, k+78), color2, 2)

        #-4,4 to -2,4
        cv2.line(frame, (j+40, k+40), (j+116, k+40), color2, 2)

        #1,4 to 2,4
        cv2.line(frame, (j+196, k+40), (j+234, k+40), color2, 2)

        #3,4 to 4,4
        cv2.line(frame, (j+276, k+40), (j+312, k+40), color2, 2)

        #-5,5 to -3,5
        cv2.line(frame, (j, k), (j+77, k-1), color2, 2)

        #-2,5 to 3,5        
        cv2.line(frame, (j+116, k), (j+275, k), color2, 2)
    
        #4,5 to 5,5
        cv2.line(frame, (j+316, k), (j+352, k), color2, 2)


        n1 = 222
        n2 = 232

        n3 = 214
        n4 = 224

        j = 28
        for i in range(0, 5):
            cv2.line(self.frame, (j, n1), (j, n2), (0, 255, 255), 3)
            j += 38

        k = 258
        for i in range(0, 5):
            cv2.line(self.frame, (k, n1), (k, n2), (0, 255, 255), 3)
            k += 38

        j = 26
        for i in range(0, 5):
            cv2.line(self.frame, (n3, j), (n4, j), (0, 255, 255), 3)
            j += 39

        k = 264
        for i in range(0, 5):
            cv2.line(self.frame, (n3, k), (n4, k), (0, 255, 255), 3)
            k += 38



        cv2.putText(frame, "START", (10, 374), 2, .5, color1, 2)
        cv2.putText(frame, "END", (400, 262), 2, .5, color1, 2)
        cv2.putText(frame, "*distance travelled in 1 move", (175, 435), 2, .35, color3, 1)
        
        return

    def Update(self, callback):

        self.frame = self.vs.read()[27:467, 125:565]
        self.FrameOverlay()
        callback()

        return

    def NullFunction(self):
        return

    def ShowFrame(self,title):
        cv2.imshow(title, self.frame)

        key = cv2.waitKey(1) & 0xFF
        if(key == ord("q")):
            self._finished = True
        elif(key == ord("c")):
            cv2.imwrite("picture%i.jpg" %self.i, self.frame)
            self.i += 1
        return


    def CaptureFrame(self):
        cv2.imwrite("picture&i.jpg" %self.i, self.frame)
        i += 1
        return


    def ProcessFrame(self, low, high):
        ''' Converts the frame to HSV, then masks the frame with the
        chosen color, and finally performs erosion and dialation.

            Args:

                frame: The frame to process

                low: The minimum HSV value to match

                high: The maximum HSV value to match

            Returns:

                The processed frame
    '''

        hsv = cv2.cvtColor(self.vs.read()[27:467,125:565], cv2.COLOR_BGR2HSV)
        #color = cv2.inRange(self.vs.read()[27:467, 125:565], low, high)
        color = cv2.inRange(hsv, low, high)
        erode = cv2.erode(color, None, iterations=2)
        self.processedFrame = cv2.dilate(erode, None, iterations=2)
        #self.frameCopy = color
        #self.frameCopy = cv2.cvtColor(color, cv2.COLOR_GRAY2BGR)
        self.frameCopy = cv2.cvtColor(self.processedFrame, cv2.COLOR_GRAY2BGR)
        return




















