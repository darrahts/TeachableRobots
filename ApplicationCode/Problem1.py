# -*- coding: utf-8 -*-

from RobotTracker import *
import time
from threading import Thread, Event


if (__name__ == "__main__"):
    
    r = Robot()
    #r.SetGoal((2,2))
    r.displayGoals = False

    repeatCounter = 0

    runThread = Thread(target=r.Run)
    e = Event()
    runThread.start()
    
    #r.Run()

    ############################################################################################
    #   origin

    r.setGoal((0,0))
    cv2.putText(r.textArea, "drive the robot to the origin", (0, 40), 2, .5, (100,200,100), 1)
    t1 = time.time()
    while(abs(r.rLoc[0] - r.goal[0]) > .6 and abs(r.rLoc[1] - r.goal[1] > .6)):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "the origin is where the 'X' and 'Y' axis intersect.", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 160), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Nice Work!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################
    #   first quadrant
    
    r.setGoal((0,0))
    cv2.putText(r.textArea, "drive the robot into the first quadrant.", (0, 40), 2, .5, (100,200,100), 1)
    t1 = time.time()
    while(abs(r.rLoc[0] - r.goal[0]) < .6 and abs(r.rLoc[1] - r.goal[1] < .6)):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "the first quadrant is top-right.", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 160), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Awesome!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################
    #   x axis
    
    r.setGoal((5,0))
    cv2.putText(r.textArea, "drive the robot to any point on the 'X' axis", (0, 40), 2, .5, (100,200,100), 1)
    t1 = time.time()
    while(abs(r.rLoc[1] - r.goal[1]) > .6):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "the 'X' axis is horizontal.", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 160), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Great!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################
    #   y axis
    
    r.setGoal((0,5))
    cv2.putText(r.textArea, "drive the robot to any point on the 'y' axis", (0, 40), 2, .5, (100,200,100), 1)
    t1 = time.time()
    while(abs(r.rLoc[0] - r.goal[0]) > .6):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "the 'Y' axis is vertical.", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 160), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Good Job!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################
    #   pos or neg y values
    
    negY = True
    r.setGoal((0,0))
    if(r.rLoc[1] > 0):
        cv2.putText(r.textArea, "drive the robot to an area with negative 'y' values", (0, 40), 2, .5, (100,200,100), 1)
    else:
        cv2.putText(r.textArea, "drive the robot to an area with positive 'y' values", (0, 40), 2, .5, (100,200,100), 1)
        negY = False
        
    t1 = time.time()

    expression = ""
    if(negY):
        expression = "r.rLoc[1] > 0"
    else:
        expression = "r.rLoc[1] < 0"
        
    while(eval(expression)):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                if(negY):
                    cv2.putText(r.textArea, "positive 'y' values are above the origin.", (0, 160), 2, .5, (100,200,100), 1)
                else:
                    cv2.putText(r.textArea, "negative 'y' values are below the origin.", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 160), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Excellent!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################
    #   pos x and pos/neg y
    
#TODO finish this for random quadrant
    quadrant = 1
    expression = ""
    r.setGoal((0,0))
    if(r.rLoc[1] > 0):
        if(r.rLoc[0] > 0):
            cv2.putText(r.textArea, "drive the robot to an area with negative 'y' and 'x' values", (0, 40), 2, .5, (100,200,100), 1)
            quadrant = 3
            expression = "r.rLoc[0] > 0 and r.rLoc[1] > 0"
        if(r.rLoc[0] < 0):
            cv2.putText(r.textArea, "drive the robot to an area with negative 'y' and positive 'x' values", (0, 40), 2, .5, (100,200,100), 1)
            quadrant = 4
            expression = "r.rLoc[0] < 0 and r.rLoc[1] > 0"
    else:
        if(r.rLoc[0] > 0):
            cv2.putText(r.textArea, "drive the robot to an area with positive 'y' and negative 'x' values", (0, 40), 2, .5, (100,200,100), 1)
            quadrant = 2
            expression = "r.rLoc[0] > 0 and r.rLoc[1] < 0"
        if(r.rLoc[0] < 0):
            cv2.putText(r.textArea, "drive the robot to an area with positive 'y' and 'x' values", (0, 40), 2, .5, (100,200,100), 1)
            quadrant = 1
            expression = "r.rLoc[0] < 0 and r.rLoc[1] < 0"

    t1 = time.time()

    while(eval(expression)):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                if(quadrant == 1):
                    cv2.putText(r.textArea, "All 'x' and 'y' values are positive in quadrant 1", (0, 160), 2, .5, (100,200,100), 1)
                if(quadrant == 2):
                    cv2.putText(r.textArea, "the quadrant with positive 'y' values and negative 'x' values", (0, 160), 2, .5, (100,200,100), 1)
                    cv2.putText(r.textArea, "is in the top half of the coordinate plane", (0, 175), 2, .5, (100,200,100), 1)
                if(quadrant == 3):
                    cv2.putText(r.textArea, "the quadrant with all negative 'x' and 'y' values", (0, 160), 2, .5, (100,200,100), 1)
                    cv2.putText(r.textArea, "is one that is to the left of the origin", (0, 175), 2, .5, (100,200,100), 1)
                if(quadrant == 4):
                    cv2.putText(r.textArea, "the quadrant with negative 'y' values and positive 'x' values", (0, 160), 2, .5, (100,200,100), 1)
                    cv2.putText(r.textArea, "is in the bottom half of the coordinate plane", (0, 175), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 160), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Well Done!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################


    #e.set()
    #runThread.join()
    

    








    
