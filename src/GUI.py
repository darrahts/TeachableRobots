from PyQt5 import QtCore, QtGui, uic, QtWidgets
from teachablerobots.src.GridSpace import *
from teachablerobots.src.RobotTracker import *
import sys
import cv2
import numpy as np
import threading
from multiprocessing import Process, Queue, Event
import time
import socket
import subprocess

formXML = uic.loadUiType("/home/tdarrah/Documents/teachablerobots/src/robotGUI1.ui")[0]



class App():
    '''The parent application that runs the window and actual GUI'''
    def __init__(self):
        '''Initializes the application and dependancies.'''
        self.app = QtWidgets.QApplication(sys.argv)
        self.gs = GridSpace()
        self.r = object
        self.w = MainWindow(self)
        self.w.setWindowTitle("Robot Command Interface")
        self.running = False
        self.robotIP = ""
        self.problemStage = 0 
        
        self.updateThread = threading.Thread(target=self.Update)
        self.commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def Run(self):
        '''The entry point into the program. This actually calls the Run function
           in the MainWindow class.'''
        self.w.show()
        self.app.exec_()


    def Update(self):
        '''This handles the gridspace camerafeed, and always updates the gs.frame which
           is what is displayed in the app.'''
        while(self.running):
            if(type(self.r) == Robot):
                self.gs.Update(lambda: self.gs.ProcessFrame(self.r.low, self.r.high))
                self.r.FindRobot()
                self.r.FrameOverlay()
            else:
                self.gs.Update(lambda: self.gs.ProcessFrame((0,0,0), (180,360,360)))

    def ConnectRobot(self):
        '''This connects to the robot'''
        if(self.problemStage == 0):
            if(self.w.colorSelection.currentText() == "robot color"):
                QtWidgets.QMessageBox.about(self.w, "Error", "you must select a color first.")
                return
            
        print(self.robotIP)
        self.w.outputTextBox.setText("attempting to connect...")
        self.w.outputTextBox.repaint()
        self.commSocket.sendto("start robot".encode("ascii"), (self.robotIP, 6789))
        time.sleep(.25)
        if(self.problemStage == 0):
            self.r = Robot(self.gs, self.w.colorSelection.currentText())
        else:
            self.r = Robot(self.gs, "green")
        self.r.robotServer.allow_reuse_address = True
        self.w.r = self.r
        self.w.InitSliders()
        if(self.r.robotServer.setupLine("") == True):
            self.w.connectButton.setText("connected")
            self.w.connectButton.setEnabled(False)
            self.w.colorSelection.setEnabled(False)
            self.r.robotComm.start()
            self.w.outputTextBox.setText("robot online\n" + str(self.r.robotServer.connection))
            for r in self.w.radialButtons:
                r.setVisible(False)
            self.w.scanNetworkButton.setVisible(False)
            self.w.radialSubmitButton.setVisible(False)
            self.w.networkLabel.setVisible(False)
            self.w.robotIPadrLabel.setText(self.robotIP)
            if(self.problemStage == 0):
                self.problemStage = 1
        else:
            self.w.outputTextBox.setText("Couldn't connect to robot.\nCheck the robotIP address.")
            self.r.robotServer.connection.close()
            return


class MyTextEdit(QtWidgets.QTextEdit, QtWidgets.QGroupBox):
    '''reimplement text edit class to override keyPressEvent to capture the enter key.'''
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
    def __init__(self, parentApp, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.parentApp = parentApp
        self.gs = parentApp.gs
        self.r = parentApp.r
        self.showRange = False

        self.window_width = self.AppFeed.frameSize().width()
        self.window_height = self.AppFeed.frameSize().height()
        self.AppFeed = ImageWidget(self.AppFeed)
        self.AppFeedAlt = ImageWidget(self.AppFeedAlt)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.Run)
        self.timer.start(1)

        self.colorSelection.addItem("robot color")
        self.colorSelection.addItem("green")
        self.colorSelection.addItem("pink")
        self.colorSelection.addItem("blue")
 
        ########################################
        #####            INPUT             #####
        ########################################
        self.InputText = MyTextEdit(QtWidgets.QTextEdit, self.InputGroupBox)
        self.InputText.setGeometry(QtCore.QRect(10, 30, 371, 61))
        self.InputText.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.InputText.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.InputText.setObjectName("InputText")

        ########################################
        #####           BUTTONS            #####
        ########################################
        self.showMazeButton.clicked.connect(self.ShowMaze)
        self.showWaypointsButton.clicked.connect(self.ShowWaypoints)
        self.startButton.clicked.connect(self.Start)
        self.textSubmitButton.clicked.connect(self.SendCommands)
        self.connectButton.clicked.connect(self.parentApp.ConnectRobot)
        self.radialSubmitButton.clicked.connect(self.SetRobotIP)
        self.scanNetworkButton.clicked.connect(self.ScanNetwork)
        self.rangeSensorButton.clicked.connect(self.StartRangeSensor)
        
        ########################################
        #####           SLIDERS            #####
        ########################################                
        self.HColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(1))
        self.SColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(2))
        self.VColorSliderLow.valueChanged.connect(lambda: self.UpdateColors(3))
        self.HColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(4))
        self.SColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(5))
        self.VColorSliderHigh.valueChanged.connect(lambda: self.UpdateColors(6))

        ########################################
        #####        RADIAL BUTTONS        #####
        ########################################
        self.radialButtons = []
        self.radialButtons.append(self.radioButton_1)
        self.radialButtons.append(self.radioButton_2)
        self.radialButtons.append(self.radioButton_3)
        self.radialButtons.append(self.radioButton_4)
        self.radialButtons.append(self.radioButton_5)
        for r in self.radialButtons:
            r.setEnabled(False)

        ########################################
        #####          CHECK BOXES         #####
        ########################################
        self.checkBoxes = []
        self.checkBoxes.append(self.checkBox_1)
        self.checkBoxes.append(self.checkBox_2)
        self.checkBoxes.append(self.checkBox_3)
        self.checkBoxes.append(self.checkBox_4)
        self.checkBoxes.append(self.checkBox_5)
        for c in self.checkBoxes:
            c.setVisible(False)

        ########################################
        #####           IMG ALGOS          #####
        ########################################        
        self.imgBoxes = []
        self.imgBoxes.append(self.imgAlgorithm_1)
        self.imgBoxes.append(self.imgAlgorithm_2)
        self.imgBoxes.append(self.imgAlgorithm_3)
        self.imgBoxes.append(self.imgAlgorithm_4)
        for i in self.imgBoxes:
            i.setVisible(False)
        
        return

    def StartRangeSensor(self):
        self.showRange = True
        self.rangeSensorButton.setEnabled(False)
        return


    def SetRobotIP(self):
        for r in self.radialButtons:
            if(r.isChecked()):
               self.parentApp.robotIP = r.text()
               self.robotIPadrLabel.setText(self.parentApp.robotIP)

    def ScanNetwork(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("which network should we scan?")
        msgBox.setWindowTitle("select a network to scan")
        msgBox.setDetailedText("To determine your IP address, you can open a browser and go to www.whatismyipaddress.com; alternatively, open a terminal (press ctrl+alt+t) and type in a certain command to determine your computer's IP address...")
        msgBox.addButton("192.168.1.0", 0)
        msgBox.addButton("10.10.1.0", 0)
        msgBox.addButton("129.59.105.0", 0)
        self.outputTextBox.setText("scanning...")
        res = msgBox.exec_()
        if(res == 0):
            result = subprocess.check_output(["nmap", "-sn", "192.168.1.0/24"])
            for r in self.radialButtons:
                r.setEnabled(True)
        elif(res == 1):
            result = subprocess.check_output(["nmap", "-sn", "10.10.1.0/24"])
        else:
            result = subprocess.check_output(["nmap", "-sn", "129.59.105.0/24"])
        self.outputTextBox.setText(result.decode("ascii"))
        

    def InitSliders(self):
        self.HColorSliderLow.setValue(self.r.low[0])
        self.SColorSliderLow.setValue(self.r.low[1])
        self.VColorSliderLow.setValue(self.r.low[2])
        self.HColorSliderHigh.setValue(self.r.high[0])
        self.SColorSliderHigh.setValue(self.r.high[1])
        self.VColorSliderHigh.setValue(self.r.high[2])
        self.lowRangeLabel.setText("Low Range: " + str(self.r.low))
        self.highRangeLabel.setText("High Range: " + str(self.r.high))
        pass
        

    def ShowMaze(self):
        if(self.gs.showMaze):
            self.gs.showMaze = False
        else:
            self.gs.showMaze = True

    def ShowWaypoints(self):
        if(self.gs.showWaypoints):
            self.gs.showWaypoints = False
        else:
            self.gs.showWaypoints = True

    def UpdateColors(self, val):
        if(val == 1):
            self.r.low = (int(self.HColorSliderLow.value()), self.r.low[1], self.r.low[2])
        if(val == 2):
            self.r.low = (self.r.low[0], int(self.SColorSliderLow.value()), self.r.low[2])
        if(val == 3):
            self.r.low = (self.r.low[0], self.r.low[1], int(self.VColorSliderLow.value()))
        if(val == 4):
            self.r.high = (int(self.HColorSliderHigh.value()), self.r.high[1], self.r.high[2])
        if(val == 5):
            self.r.high = (self.r.high[0], int(self.SColorSliderHigh.value()), self.r.high[2])
        if(val == 6):
            self.r.high = (self.r.high[0], self.r.high[1], int(self.VColorSliderHigh.value()))

        self.lowRangeLabel.setText("Low Range: " + str(self.r.low))
        self.highRangeLabel.setText("High Range: " + str(self.r.high))


    def SendCommands(self):
        if(self.r.robotServer.connected):
            self.r.SendCommandSequence(self.InputText.toPlainText())
            self.commandHistory.setText(self.commandHistory.toPlainText() + self.InputText.toPlainText())
            self.InputText.setText("")
   
    def Start(self):
        self.parentApp.running = True
        self.parentApp.updateThread.start()
        self.startButton.setEnabled(False)
        self.startButton.setText('Starting...')
        self.parentApp.t1 = time.time()
        return
        


    def Run(self):
        if(self.parentApp.problemStage == 0):
            self.problemDescription.setText("Establish a connection with the robot.")
        elif(self.parentApp.problemStage == 1):
            self.problemDescription.setText("navigate your way through the maze. Use the waypoints and short command sequences.")
        elif(self.parentApp.problemStage == 2):
            self.problemDescription.setText("Now that the robot can navigate through a virtual " +
                                            "world, it's ready to navigate the real word. But " +
                                            "first, ensure it won't run into any obstacles!\n\n" +
                                            "HINT: use the wall...")
        else:
            self.problemDescription.setText("")
        
        if(self.showRange):
            self.rangeLabel.setText(str(self.parentApp.r.range.value))


        if(self.parentApp.running):
            self.startButton.setText("Camera is live")


            if(type(self.r) == Robot):
                img = self.r.FrameOverlay()
            else:
                img = self.gs.frame

            
            
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
                if(not self.r.mazeFinished and self.r.goalFound == True):
                    self.outputTextBox.setText("Good Job!!")
                    self.r.mazeFinished = True
                    self.r.goalFound = False
                    self.parentApp.problemStage = 2
                    self.rangeSensorButton.setEnabled(True)
            except Exception as e:
                pass


    def closeEvent(self, event):
        self.parentApp.running = False
        if(type(self.r) == Robot):
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























