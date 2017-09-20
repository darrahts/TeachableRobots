import cv2
import picamera
import datetime
from time import sleep
from Hardware import *
import os

class Vision(object):
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.path = "/home/pi/Pictures/"

    def setPath(self, path):
        self.assertDirectory(path)
        self.path = path
        return

    def assertDirectory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        return

    def preview(self):
        self.camera.start_preview(fullscreen=False, window=(10, 24, 640, 480))
        return

    def stopPreview(self):
        self.camera.stop_preview()
        return

    def capture(self, path):
        if path == -1 and self.path == "":
            print("must set path first.")
            return
        else:
            dateNow = str(datetime.date.today())
            timeNow = str(datetime.datetime.now().strftime("%H:%M:%S"))
            fileName = dateNow + "_" + timeNow
        if path == -1:
            self.camera.capture(self.path + "/" + fileName + ".jpg")
        else:
            self.assertDirectory(path)
            self.camera.capture(path + "/" + fileName + ".jpg")
        return


class FaceDetector:
	def __init__(self, faceCascadePath):
		self.faceCascade = cv2.CascadeClassifier(faceCascadePath)
	
	def detect(self, image, scaleFactor =1.1, minNeighbors=5, minSize=(30,30)):
		rects = self.faceCascade.detectMultiScale(image, scaleFactor=scaleFactor, minNeighbors=minNeighbors, minSize=minSize, flags=cv2.CASCADE_SCALE_IMAGE)
		return rects

	def test(self):
		print("yes")



##v = Vision()
##v.detectFaces()
##v.preview()
##sleep(2)
##v.capture(-1)
##sleep(3)
##v.stopPreview()


