from PyQt5 import QtCore, QtGui, uic, QtWidgets
from teachablerobots.src.GridSpace import *
from teachablerobots.ApplicationCode.RobotTracker import *
import sys
import cv2
import numpy as np
import threading
from multiprocessing import Process, Queue, Event
import time
import argparse


formXML = uic.loadUiType("robotGUI.ui")[0]




class App():
    def __init__(self,color,mode):
        self.app = QtWidgets.QApplication(sys.argv)
        self.gs = GridSpace("gui")
        self.r = Robot(self.gs, color, mode)
        self.w = MainWindow(self, mode)
        self.w.setWindowTitle("GUI Test")
        self.running = False
        self.counter = 0
        self.t1 = time.time()
        
        self.updateThread = threading.Thread(target=self.Update)
        
    def Run(self):
        self.w.show()
        self.app.exec_()



    def Update(self):
        while(self.running):
            self.gs.Update(lambda: self.gs.ProcessFrame(self.r.low, self.r.high))
            self.r.FindRobot()
            #self.r.FrameOverlay()
            self.counter += 1


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



class MainWindow(QtWidgets.QMainWindow, formXML):
    def __init__(self, parentApp, mode, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.parentApp = parentApp
        self.gs = parentApp.gs
        self.r = parentApp.r

        self.mode = mode

        self.InputText = MyTextEdit(QtWidgets.QTextEdit, self.InputGroupBox)
        self.InputText.setGeometry(QtCore.QRect(10, 30, 371, 61))
        self.InputText.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.InputText.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.InputText.setObjectName("InputText")

        self.ToggleAltButton.clicked.connect(self.ShowMaze)

        self.startButton.clicked.connect(self.start_clicked)
        self.TextSubmitButton.clicked.connect(self.SendCommands)

        self.HColorSliderLow.setValue(self.r.low[0])
        self.SColorSliderLow.setValue(self.r.low[1])
        self.VColorSliderLow.setValue(self.r.low[2])
        self.HColorSliderHigh.setValue(self.r.high[0])
        self.SColorSliderHigh.setValue(self.r.high[1])
        self.VColorSliderHigh.setValue(self.r.high[2])
        self.lowRangeLabel.setText("Low Range: " + str(self.r.low))
        self.highRangeLabel.setText("High Range: " + str(self.r.high))
        
        self.HColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(1))
        self.SColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(2))
        self.VColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(3))
        self.HColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(4))
        self.SColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(5))
        self.VColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(6))

        
        self.window_width = self.AppFeed.frameSize().width()
        self.window_height = self.AppFeed.frameSize().height()
        self.AppFeed = ImageWidget(self.AppFeed)
        self.AppFeedAlt = ImageWidget(self.AppFeedAlt)

        self.ProblemDescription.parent = self.tab
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Run)
        self.timer.start(1)
        
        if(self.r.robotServer.connected):
            self.r.robotComm.start()
            print("robot online.")

    def ShowMaze(self):
        if(self.gs.showMaze):
            self.gs.showMaze = False
        else:
            self.gs.showMaze = True

    def UpdateColors(self, val):
        if(val == 1):
            self.self.r.low = (int(self.HColorSliderLow.value()), self.self.r.low[1], self.self.r.low[2])
        if(val == 2):
            self.self.r.low = (self.self.r.low[0], int(self.SColorSliderLow.value()), self.self.r.low[2])
        if(val == 3):
            self.self.r.low = (self.self.r.low[0], self.self.r.low[1], int(self.VColorSliderLow.value()))
        if(val == 4):
            self.self.r.high = (int(self.HColorSliderHigh.value()), self.self.r.high[1], self.self.r.high[2])
        if(val == 5):
            self.self.r.high = (self.self.r.high[0], int(self.SColorSliderHigh.value()), self.r.high[2])
        if(val == 6):
            self.self.r.high = (self.self.r.high[0], self.r.high[1], int(self.VColorSliderHigh.value()))

        self.lowRangeLabel.setText("Low Range: " + str(self.r.low))
        self.highRangeLabel.setText("High Range: " + str(self.r.high))



    def SendCommands(self):
        if(self.mode == "connected"):
            self.r.SendCommandSequence(self.InputText.toPlainText())
            self.ProblemDescription.setText(self.InputText.toPlainText())
            self.InputText.setText("")
   
    def start_clicked(self):
        self.parentApp.running = True
        self.parentApp.updateThread.start()
        self.startButton.setEnabled(False)
        self.startButton.setText('Starting...')
        self.parentApp.t1 = time.time()
        return
        


    def Run(self):
        if(self.parentApp.running):
            t2 = time.time()
            self.startButton.setText("Camera is live")

            img = self.r.FrameOverlay()
            
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

            h,w,b = self.gs.frameCopy.shape

            try:
                image1 = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
                image2 = QtGui.QImage(self.gs.frameCopy, w, h, (b*w), QtGui.QImage.Format_RGB888)

                self.AppFeed.setImage(image1)
                self.AppFeedAlt.setImage(image2)
                self.locationLabel.setText(str(self.r.location.value.decode('ascii')))
                self.directionLabel.setText(str(self.r.direction.value.decode('ascii')))
                self.distanceTravelledLabel.setText(str(self.r.distanceTravelled.value))
            except Exception as e:
                pass


    def closeEvent(self, event):
        self.parentApp.running = False
        self.r.SendCommandSequence("Q")
        time.sleep(1.2)
        self.r._finished = True
        self.r.robotServer.e.set()
        self.r.robotServer.finished.value = True
        if(self.r.robotComm.is_alive()):
            self.r.robotComm.e.set()
            self.r.robotComm.terminate()
            self.r.robotComm.join()
        self.r.robotServer.closeConnection()
        return


# ************************* MAIN ************************* #

if(__name__ == "__main__"):
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--color", required=True, help="color of robot")
    ap.add_argument("-m", "--mode", required=True, help="mode (standalone or with robot)")
    args = vars(ap.parse_args())
    
    a = App(str(args["color"]), str(args["mode"]))
    a.Run()























