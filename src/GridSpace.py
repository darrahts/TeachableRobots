# -*- coding: utf-8 -*-

from teachablerobots.src.Vision import *
import cv2
import imutils
import numpy as np


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
        #self.textArea = np.zeros((frame.shape[0],550,3),dtype=np.uint8)
        
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

##        maskk = frame.copy()
##        for i in range(0, len(frame[0])):
##            for j in range(0, len(frame)):
##                if(i < 125 or i > 555 or j < 32 or j > 460):
##                    maskk[j][i] = (0,0,0)

##        cv2.bitwise_and(maskk, self.frame, self.frame, mask=None)

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
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = cv2.inRange(frame, low, high)
        erode = cv2.erode(color, None, iterations=2)
        dialate = cv2.dilate(erode, None, iterations=2)
        return dialate



