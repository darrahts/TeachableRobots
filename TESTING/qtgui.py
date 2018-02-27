from PyQt5 import QtCore, QtGui, uic, QtWidgets
from teachablerobots.src.GridSpace import *
from teachablerobots.ApplicationCode.RobotTracker import *
#from teachablerobots.src.Communicate import SocketComm
import sys
import cv2
import numpy as np
import threading
from multiprocessing import Process, Queue, Event
import time
import queue

running = False
capture_thread = None
form_class = uic.loadUiType("simple.ui")[0]
q = queue.Queue()
gs = GridSpace("gui")
r = Robot(gs, "pink")

counter = 0

t1 = time.time()


#   reimplement text edit class to override keyPressEvent to capture the enter key
class MyTextEdit(QtWidgets.QTextEdit, QtWidgets.QGroupBox):
    def __init__(self, parent, parent2):
        super(MyTextEdit, self).__init__(parent2)

    def keyPressEvent(self, event):
        super(MyTextEdit, self).keyPressEvent(event)
        if(event.key() == QtCore.Qt.Key_Return):
            self.parent().parent().parent().SendCommands()



class ImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()



class MyWindowClass(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.InputText = MyTextEdit(QtWidgets.QTextEdit, self.InputGroupBox)
        self.InputText.setGeometry(QtCore.QRect(10, 30, 371, 61))
        self.InputText.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.InputText.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.InputText.setObjectName("InputText")

        self.ToggleAltButton.clicked.connect(self.ShowMaze)

        self.startButton.clicked.connect(self.start_clicked)
        self.TextSubmitButton.clicked.connect(self.SendCommands)

        self.HColorSliderLow.setValue(r.low[0])
        self.SColorSliderLow.setValue(r.low[1])
        self.VColorSliderLow.setValue(r.low[2])
        self.HColorSliderHigh.setValue(r.high[0])
        self.SColorSliderHigh.setValue(r.high[1])
        self.VColorSliderHigh.setValue(r.high[2])
        self.lowRangeLabel.setText("Low Range: " + str(r.low))
        self.highRangeLabel.setText("High Range: " + str(r.high))
        
        self.HColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(1))
        self.SColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(2))
        self.VColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(3))
        self.HColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(4))
        self.SColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(5))
        self.VColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(6))
        #self.SColorSlider.valueChanged.connect(robot.low[1])
        #self.VColorSlider.valueChanged.connect(robot.low[2])
        
        self.window_width = self.AppFeed.frameSize().width()
        self.window_height = self.AppFeed.frameSize().height()
        self.AppFeed = ImageWidget(self.AppFeed)
        self.AppFeedAlt = ImageWidget(self.AppFeedAlt)

        self.ProblemDescription.parent = self.tab
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Run)
        self.timer.start(1)
        
        if(r.robotServer.connected):
            #r.robotCommThread.start()
            r.robotComm.start()
            print("robot online.")

    def ShowMaze(self):
        if(gs.showMaze):
            gs.showMaze = False
        else:
            gs.showMaze = True

    def UpdateColors(self, val):
        if(val == 1):
            r.low = (int(self.HColorSliderLow.value()), r.low[1], r.low[2])
        if(val == 2):
            r.low = (r.low[0], int(self.SColorSliderLow.value()), r.low[2])
        if(val == 3):
            r.low = (r.low[0], r.low[1], int(self.VColorSliderLow.value()))
        if(val == 4):
            r.high = (int(self.HColorSliderHigh.value()), r.high[1], r.high[2])
        if(val == 5):
            r.high = (r.high[0], int(self.SColorSliderHigh.value()), r.high[2])
        if(val == 6):
            r.high = (r.high[0], r.high[1], int(self.VColorSliderHigh.value()))

        self.lowRangeLabel.setText("Low Range: " + str(r.low))
        self.highRangeLabel.setText("High Range: " + str(r.high))
        #print("low: " + str(r.low))
        #print("high: " + str(r.high))
        #print("***********************************")


    def SendCommands(self):
        r.SendCommandSequence(self.InputText.toPlainText())
        self.ProblemDescription.setText(self.InputText.toPlainText())
        self.InputText.setText("")
   
    def start_clicked(self):
        global running,t1
        running = True
        capture_thread.start()
        self.startButton.setEnabled(False)
        self.startButton.setText('Starting...')
        t1 = time.time()
        return
        


    def Run(self):

        #if not q.empty():
        #self.startButton.setText('Camera is live')
        
        global running,counter, t1
        if(running):
            t2 = time.time()
            self.startButton.setText("Camera is live")
            #print("length of inbox in loop: " + str(len(r.robotServer.inbox)))
            #img = q.get()
            img = r.FrameOverlay()
            
            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1
            
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width

            h,w,b = gs.frameCopy.shape

            try:
                image1 = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
                image2 = QtGui.QImage(gs.frameCopy, w, h, (b*w), QtGui.QImage.Format_RGB888)

                self.AppFeed.setImage(image1)
                self.AppFeedAlt.setImage(image2)
                self.locationLabel.setText(str(r.location.value.decode('ascii')))
                self.directionLabel.setText(str(r.direction.value.decode('ascii')))
                self.distanceTravelledLabel.setText(str(r.distanceTravelled.value))
            except Exception as e:
                pass

          #  if(t2 - t1 > .95 and t2 - t1 < 1.05):
          #      print("fps: " + str(counter))

    def closeEvent(self, event):
        global running
        running = False
        r.SendCommandSequence("Q")
        time.sleep(1.2)
        r._finished = True
        r.robotServer.e.set()
        r.robotServer.finished.value = True
        #if(r.robotCommThread.isAlive()):
        #    r.robotCommThread.e.set()
        #    r.robotCommThread.join()
        if(r.robotComm.is_alive()):
            r.robotComm.e.set()
            r.robotComm.terminate()
            r.robotComm.join()
            
        r.robotServer.closeConnection()
        return

    #def keyPressEvent(self, qKeyEvent):
    #    print(qKeyEvent.key())
    #    if(qKeyEvent.key() == qtCore.Qt.Key_Return):
    #       print("enter pressed.")



def grab(cam, queue, width, height, fps):
    global running,counter
    #capture = cv2.VideoCapture(cam)
    #capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #capture.set(cv2.CAP_PROP_FPS, fps)
    
    while(running):
        gs.Update(gs.FrameOverlay)
        r.frame = gs.frame
        r.FindRobot(gs.ProcessFrame(r.low, r.high))
        counter += 1
        #f = r.FrameOverlay()
        
        #r.FindRobot
        #frame = {}        
        #capture.grab()
        #retval, img = capture.retrieve(0)
        #frame["img"] = img
        #print(type(frame))

        #if q.qsize() < 10:
        #    q.put(f)
            #q.put(gs.frame)
            #q.put(frame)
        #else:
        #    pass
            #print (queue.qsize())

        

capture_thread = threading.Thread(target=grab, args = (0, q, 1920, 1080, 30))

app = QtWidgets.QApplication(sys.argv)
w = MyWindowClass()
w.setWindowTitle('GUI Test')
w.show()
app.exec_()
























