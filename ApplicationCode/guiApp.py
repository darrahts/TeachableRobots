# -*- coding: utf-8 -*-
from teachablerobots.src.RobotTracker import *
from teachablerobots.src.GUI import *
import argparse

# ************************* MAIN ************************* #


def InitialCondition(a):
    a.robotIP = "192.168.1.41"
    a.problemStage = 2
    a.w.rangeSensorButton.setEnabled(True)
    a.w.Start()
    a.ConnectRobot()
    return

if(__name__ == "__main__"):
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--resume", required=False, help="resume previous")
    args = vars(ap.parse_args())
    
    a = App()
    if(args["resume"] == "true"):
        InitialCondition(a)
    a.Run()


