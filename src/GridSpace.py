# -*- coding: utf-8 -*-

from teachablerobots.src.Vision import *
import cv2
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
    frame = vs.read()[27:467, 125:565]
    frameCenter = ((frame.shape[1] // 2), (frame.shape[0] // 2) + 5)
    #textArea = np.zeros((frame.shape[0],550,3),dtype=np.uint8)
    #textAreaCopy = textArea
    frameCopy = frame
    #window = np.hstack([frame,textArea])
    window = np.hstack([frame,frameCopy])
    
    square = np.ndarray([4,2], dtype=int)
    square[0] = [10, 10]
    square[1] = [10, 425]
    square[2] = [425, 435]
    square[3] = [435, 10]


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

        return 

    def Update(self, callback):
        self.frame = self.vs.read()[27:467, 125:565]
        callback()
        #self.textArea = self.textAreaCopy
        #self.window = np.hstack([self.frame,self.textArea])
        self.window = np.hstack([self.frame,self.frameCopy])
        return

    def ShowFrame(self, fullWindow):
        if(fullWindow):
            cv2.imshow(self.title, self.window)
        else:
            cv2.imshow(self.title, self.frame)

        key = cv2.waitKey(1) & 0xFF
        if(key == ord("q")):
            self.finished = True
        elif(key == ord("c")):
            cv2.imwrite("picture%i.jpg" %i, window)
            i += 1
        return









##G = GridSpace()
##
##while(True):
##    G.Update(G.FrameOverlay)
##    G.ShowFrame(True)













