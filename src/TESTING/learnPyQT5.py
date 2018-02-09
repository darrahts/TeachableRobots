#!/usr/bin/python3
# -*- coding: utf-8 -*-

#***************************************************
#                        IMPORTS
#***************************************************                   

import sys
import csv
import os
from PyQt5.QtWidgets import  qApp, QMessageBox, QLineEdit, QMainWindow, QAction, QLineEdit, QApplication, QWidget, QToolTip, QPushButton, QDesktopWidget
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication, pyqtSlot
from time import sleep
import threading
import cv2
import numpy as np
#from teachablerobots.src.GridSpace import *


#***************************************************
#                   MAIN FORM CLASS
#
# This class is for display only and contains all
# functions related to the GUI of the intelligent
# scheduling agent. This class utilizes the
# DataHandler class to get/set information from the
# SchedulingAgent class. Inherits from QWidget class.
#***************************************************                    
class MainForm(QMainWindow):
    nameBox = ""
    readOnly = False
    
    #Constructor
    def __init__(self):
        super().__init__()
        self.InitUI()
        QToolTip.setFont(QFont('SansSerif', 10))
        
	
    
    #Initialize general window properties 
    def InitUI(self):
        self.setFixedSize(1600, 900)
        #self.CenterWindow()
        self.setWindowTitle("Intelligent Scheduling Agent")
        self.setWindowIcon(QIcon('web.png'))
        self.setToolTip('This is a <b>QWidget</b> widget')
        self.statusBar()

        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(self.MenuActions("Exit"))
        fileMenu.addAction(self.MenuActions("Open"))

    #Gets dimensions of desktop and window to center window
    def CenterWindow(self):
        fg = self.frameGeometry()
        ag = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(ag)
        self.move(fg.topLeft())

    #Creates textboxes
    def AddTextBoxes(self):
        self.nameBox = QLineEdit(self)
        self.nameBox.move(20, self.nameBox.height() + 20)
        self.nameBox.resize(180, 25)
        self.nameBox.setText("Student's Name")

        #classBox = QLineEdit(self)
        
        

    #Creates buttons 
    def AddButtons(self):

        startButton = QPushButton("start", self)
        startButton.move(200,500)
        startButton.clicked.connect(lambda: self.DummyFunction())

        
        tBtn = QPushButton("Test", self)
        tBtn.setToolTip("This is a <b>QPushButton</b> widget")
        tBtn.resize(tBtn.sizeHint())
        tBtn.clicked.connect(lambda: self.ButtonClickEvents(tBtn))
        tBtn.move(50,500)

        qBtn = QPushButton("Quit", self)
        qBtn.clicked.connect(self.close)
        qBtn.resize(qBtn.sizeHint())
        qBtn.move(1580-qBtn.width(),880-qBtn.height())
        
    def DummyFunction(self):
        return 1

    #Returns a menu item for the desired action passed
    def MenuActions(self, action):
        if(action == "Exit"):
            exitAct = QAction(QIcon("exit.png"), "&Exit", self)
            exitAct.setShortcut("Ctrl+Q")
            exitAct.setStatusTip("exit Application")
            exitAct.triggered.connect(self.close)
            return exitAct
        elif(action == "Open"):
            openAct = QAction(QIcon("exit.png"), "&Open", self)
            openAct.setShortcut("Ctrl+O")
            openAct.setStatusTip("Open File")
            openAct.triggered.connect(self.open)
            return openAct
        else:
            return
        

    #Implements the various button click events
    def ButtonClickEvents(self, button):
        if button.text() == "Test":
            if (self.readOnly == False):
                print("false")
                self.nameBox.setReadOnly(True)
                self.nameBox.setStyleSheet("color: grey")
                self.readOnly = True
            else:
                print("true")
                self.nameBox.setReadOnly(False)
                self.nameBox.setStyleSheet("color: black")
                self.readOnly = False
                
                
    #Adds all created controls to the form
    def PopulateForm(self):
        self.AddButtons()
        self.AddTextBoxes()

    def open(self):
        os.system('xdg-open "~/home/"')
        return
    #Overrides inherited close event to display a dialog box
        
##    def closeEvent(self, event):
##        reply = QMessageBox.question(self, 'Message',
##            "Are you sure to quit?", QMessageBox.Yes | 
##            QMessageBox.No, QMessageBox.No)
##
##        if reply == QMessageBox.Yes:
##            event.accept()
##        else:
##            event.ignore()
            



if __name__ == '__main__':
    os.system('xdg-open "~/home/"')
    app = QApplication(sys.argv)
    
    form = MainForm()
    form.PopulateForm()
    form.show()





    sys.exit(app.exec_())
