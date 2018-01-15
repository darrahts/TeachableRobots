# -*- coding: utf-8 -*-

from RobotTracker import *
import time
from threading import Thread, Event




def Problem2():
    repeatCounter = 0
    time.sleep(1)    
    ############################################################################################
    #   drive to point

    r.SetGoal((-3,1))
    cv2.putText(r.textArea, "drive the robot to (-3,1)", (0, 40), 2, .5, (100,200,100), 1)
    t1 = time.time()
    while(abs(r.rLoc[0] - r.goal[0]) > .6 or abs(r.rLoc[1] - r.goal[1]) > .6):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "points are given in (x,y) format", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            elif(repeatCounter == 1):
                cv2.putText(r.textArea, "The point is 3 units to the left of the origin and 1 unit up", (0, 175), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            elif(repeatCounter == 2):
                cv2.putText(r.textArea, "Drive to the point shown", (0, 190), 2, .5, (100,200,100), 1)
                r.displayGoals = True
                r.displayGoalLoc = True
                t1 = t2
                repeatCounter += 1
            elif(repeatCounter == 3):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 205), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Nice Work!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.displayGoals = False
    r.displayGoalLoc = False
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)

    ############################################################################################
    #   drive to point

    r.SetGoal((2,-4))
    r.displayGoals = True
    cv2.putText(r.textArea, "drive the robot to the point shown", (0, 40), 2, .5, (100,200,100), 1)
    t1 = time.time()
    while(abs(r.rLoc[0] - r.goal[0]) > .6 or abs(r.rLoc[1] - r.goal[1] > .6)):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "'x' should be positive, 'y' should be negative", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            elif(repeatCounter == 1):
                cv2.putText(r.textArea, "'y' = -4", (0, 175), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            elif(repeatCounter == 2):
                cv2.putText(r.textArea, "Drive to (2,-4)", (0, 190), 2, .5, (100,200,100), 1)
                r.displayGoalLoc = True
                t1 = t2
                repeatCounter += 1
            elif(repeatCounter == 3):
                cv2.putText(r.textArea, "maybe you need some extra assistance", (0, 205), 2, .5, (100,200,100), 1)
                x = input()
                if(x == "continue"):
                    break

    cv2.putText(r.textArea, "Nice Work!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)
    r.displayGoals = False
    r.finished = True


if (__name__ == "__main__"):
    
    r = Robot()
    r.displayGoals = False

    problemThread = Thread(target=Problem2)
    problemThread.isDaemon = True
    e = Event()
    problemThread.start()

    r.Run()    

    e.set()
    problemThread.join()    

    

    
