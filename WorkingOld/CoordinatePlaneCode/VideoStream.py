from threading import Thread
#from picamera.array import PiRGBArray
#from picamera import PiCamera
import cv2
#import time
import datetime
import uuid
import os

#This class is used to approximate the processing frames per second
#This class has no functional purpose per se, strictly for information
class FPS:
    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        return(self._end - self._start).total_seconds()

    def fps(self):
        return self._numFrames / self.elapsed()

#This class threads the camera read
class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while(True):
            if(self.stopped):
                return
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


class Demo:
    def __init__(self, src, numFrames, display):
        self.numFrames = numFrames
        self.display = display
        self.src = src

    def StartRegular(self):
        print("[INFO] sampling frames from webcam...")
        stream = cv2.VideoCapture(self.src)
        fps = FPS().start()

        # loop over some frames
        while fps._numFrames < self.numFrames:
            # grab the frame from the stream and resize it to have a maximum
            # width of 400 pixels
            (grabbed, frame) = stream.read()
            #frame = imutils.resize(frame, width=480)
 
            # check to see if the frame should be displayed to our screen
            if self.display == True:
                cv2.imshow("Frame", frame)
                key = (cv2.waitKey(1) & 0xFF)

            # update the FPS counter
            fps.update()
 
        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
        # do a bit of cleanup
        stream.release()
        cv2.destroyAllWindows()

    def StartThreaded(self):
        # created a *threaded* video stream, allow the camera sensor to warmup,
        # and start the FPS counter
        print("[INFO] sampling THREADED frames from webcam...")
        vs = WebcamVideoStream(self.src).start()
        fps = FPS().start()
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 640, 480)
 
        # loop over some frames...this time using the threaded stream
        while fps._numFrames < self.numFrames:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            frame = vs.read()
            #frame = imutils.resize(frame, width=480)
            #frame = cv2.resize(frame, (640,480))
 
            # check to see if the frame should be displayed to our screen
            if self.display == True:
                cv2.imshow('image', frame)
                key = cv2.waitKey(1) & 0xFF

            # update the FPS counter
            fps.update()
 
        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()


class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False

    def start(self):
        #self.update()
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)

            if(self.stopped):
               self.stream.close()
               self.rawCapture.close()
               self.camera.close()
               return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


class VideoStream:
    def __init__(self, src, usePiCamera, resolution=(320, 240), framerate=32):
        if usePiCamera:
            self.stream = PiVideoStream(resolution=resolution, framerate=framerate)
        else:
            self.stream = WebcamVideoStream(src=src)
        
    def start(self):
        return self.stream.start()

    def update(self):
        self.stream.update()

    def read(self):
        return self.stream.read()

    def stop(self):
        self.stream.stop()

class TempImage:
	def __init__(self, basePath="./", ext=".jpg"):
		# construct the file path
		self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
			rand=str(uuid.uuid4()), ext=ext)
 
	def cleanup(self):
		# remove the file
		os.remove(self.path)









    
