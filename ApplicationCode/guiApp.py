# -*- coding: utf-8 -*-
from teachablerobots.src.RobotTracker import *
from teachablerobots.src.GUI import *


# ************************* MAIN ************************* #


def InitialCondition(a):
    a.robotIP = "192.168.1.41"
    a.problemStage = 2
    a.w.rangeSensorButton.setEnabled(True)
    a.w.Start()
    a.ConnectRobot()
    return

if(__name__ == "__main__"):
    a = App()
    InitialCondition(a)
    a.Run()


