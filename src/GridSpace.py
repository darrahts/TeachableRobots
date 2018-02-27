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
    def __init__(self, mode):

        if(mode == ""):
            self.title = "Robot Grid Space"
            cv2.namedWindow(self.title)
        elif(mode == "gui"):
            pass
        
        self.vs = WebcamVideoStream(0).start()
        self.frame = self.vs.read()[27:467, 125:565]
        self.frameCenter = ((self.frame.shape[1] // 2), (self.frame.shape[0] // 2) + 5)
        #textArea = np.zeros((frame.shape[0],550,3),dtype=np.uint8)
        #textAreaCopy = textArea
        self.frameCopy = self.frame
        #window = np.hstack([frame,textArea])
        #window = np.hstack([frame,frameCopy])
        
        self.square = np.ndarray([4,2], dtype=int)
        self.square[0] = [10, 10]
        self.square[1] = [10, 425]
        self.square[2] = [425, 435]
        self.square[3] = [435, 10]
        self.showMaze = True

        self._finished = False


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
            self.DrawMaze(self.frame)

        return 


    def DrawMaze(self, frame):

        color1 = (0, 0, 255)
        color2 = (0, 255, 0)


        j = 41
        k = 49

        #   VERTICAL LINES

        #-5,5 to -5,3
        cv2.line(frame, (j, k), (j+2, 131), color2, 2)

        #-5,2 to -5,-2
        cv2.line(frame, (j+2, 170), (j+5, 287), color2, 2)

        #-4,5 to -4,6
        cv2.line(frame, (j+38, k), (j+38, 10), color2, 2)
        
        #-4,4 to -4,-1
        cv2.line(frame, (j+39, k+40), (j+42, k+200), color2, 2)

        #-3,1 to -3,3
        cv2.line(frame, (j+80,k+81), (j+80, k+157), color2, 2)

        #-3,-2 -3,-3
        cv2.line(frame, (j+82,k+237), (j+82, k+275), color2, 2)

        #-3,-5 to -3,-6
        cv2.line(frame, (j+84,k+348), (j+84, k+376), color2, 2)

        #-2,-1 to -2,-2
        cv2.line(frame, (j+119, k+199), (j+119,k+238), color2, 2)

        #-2,-3 to -2,-4
        cv2.line(frame, (j+119, k+275), (j+119,k+312), color2, 2)
                        
        #-1,5 to -1,1
        cv2.line(frame, (j+155, k), (j+156,k+152), color2, 2)

        #-1,-1 to -1,-3
        cv2.line(frame, (j+158, k+199), (j+158, k+272), color2, 2)

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
        cv2.line(frame, (j+353, k+118), (j+353, k+154), color2, 2)

        #5,-3 to 5,-4
        cv2.line(frame, (j+352,k+238), (j+350,k+310), color2, 2)

        

        #   HORIZONTAL LINES
        
        #-5,5 to -3,5
        cv2.line(frame, (j, k), (j+77, k-1), color2, 2)

        #-2,5 to 3,5        
        cv2.line(frame, (j+116, k), (j+275, k), color2, 2)
    
        #4,5 to 5,5
        cv2.line(frame, (j+316, k), (j+352, k), color2, 2)
        return

    def Update(self, callback):

        self.frame = self.vs.read()[27:467, 125:565]
        callback()
        #self.textArea = self.textAreaCopy
        #self.window = np.hstack([self.frame,self.textArea])
        #self.window = np.hstack([self.frame,self.frameCopy])
        #self.ProcessFrame((33, 77, 0),(165, 215, 75))
        return

    def ShowFrame(self, fullWindow):
        i = 0
        if(fullWindow):
            cv2.imshow(self.title, self.window)
        else:
            cv2.imshow(self.title, self.frame)

        key = cv2.waitKey(1) & 0xFF
        if(key == ord("q")):
            self._finished = True
        elif(key == ord("c")):
            cv2.imwrite("picture%i.jpg" %i, window)
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
       # print("low: " + str(low))
       # print("high: " + str(high))
       # print("***********************************")
        hsv = cv2.cvtColor(self.vs.read()[27:467,125:565], cv2.COLOR_BGR2HSV)
        #color = cv2.inRange(self.vs.read()[27:467, 125:565], low, high)
        color = cv2.inRange(hsv, low, high)
        erode = cv2.erode(color, None, iterations=2)
        dialate = cv2.dilate(erode, None, iterations=2)
        #self.frameCopy = color
        #self.frameCopy = cv2.cvtColor(color, cv2.COLOR_GRAY2BGR)
        self.frameCopy = cv2.cvtColor(dialate, cv2.COLOR_GRAY2BGR)
        return dialate




















