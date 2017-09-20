#from __future__ import print_function
import sys

sys.path.insert(0, "/home/pi/csrbot/robot-api")

from Vision import FaceDetector
from multiprocessing.pool import ThreadPool
#from multiprocessing import Queue
from VideoStream import VideoStream
import imutils
import numpy as np
import argparse
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--face", required=True, help="try something like /home/<user>/opencv-<version>/data/haarcascades/haarcascade_frontalface_default.xml")
ap.add_argument("-i", "--image", help="path to image")
ap.add_argument("-p", "--picamera", type=int, default=1, help="use piCam? 1 for yes, 0 for no")
#ap.add_argument("-v", "--video", help="path to video")

args = vars(ap.parse_args())

fd = cv2.CascadeClassifier(args["face"])

def fdet(gray):
    return fd.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(48,48))

def detectStream():
    i = 0
    t1 = time.time()
    t2 = time.time()
    pool = ThreadPool(processes=1)
    
    stream = VideoStream().start()
    time.sleep(.5)
    try:
        while(True):
            frame = stream.read()
            frame = imutils.resize(frame, width=600, height=400)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            async_result = pool.apply_async(fdet, (gray,))
            faceRects = async_result.get()            

            for (x,y,w,h) in faceRects:
                if w > 0:
                    cv2.rectangle(frame, (x,y), (x+int(1.25*w), y+int(1.25*h)), (0,255,0), 2)
                    t2 = time.time()
                    if(t2 - t1 > 1):
                        cv2.imwrite("face%d.jpg" %i, frame)
                        i = i + 1
                        t1  = t2

            cv2.imshow("frame", frame)

            if(cv2.waitKey(1) & 0xFF == ord("q")):
                break
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        stream.stop()
        print("ending routine...")

def detectImage():
    image = cv2.imread(args["image"])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    fd = FaceDetector(args["face"])
    #fd = FaceDetector("~/opencv-tmp/opencv-3/data/haarcascades/haarcascade_frontalface_default.xml")
    
    faceRects = fd.detect(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
    
    print("found {} face(s)".format(len(faceRects)))

    for (x,y,w,h) in faceRects:
        cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("Faces", image)
    cv2.waitKey(0)

if args["image"] is not None:
    detectImage()
else:
    detectStream()


