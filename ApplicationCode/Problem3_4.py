# -*- coding: utf-8 -*-

from RobotTracker import *
import time
from threading import Thread, Event




def Problem3():
    repeatCounter = 0
    time.sleep(1)
    counter = 0
    ############################################################################################
    #   drive to point

    r.SetGoal((-3,1))
    cv2.putText(r.textArea, "Amazon is adding new drone routes to Nashville! They need", (0, 40), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "coordinates for some of the locations, help them out by", (0, 55), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "driving the robot to each new location in one sequence.", (0, 70), 2, .5, (100,200,100), 1)

    r.displayGoals = True
    t1 = time.time()
    while(counter != 4):
        time.sleep(2)
        counter += 1
        r.displayGoalLoc = True

    cv2.putText(r.textArea, "Nice Work!", (0, 300), 4, 1.2, (100,200,100), 1)
    repeatCounter = 0
    time.sleep(3)
    r.displayGoals = False
    r.displayGoalLoc = False
    r.textArea = np.zeros((r.frame.shape[0],550,3),dtype=np.uint8)
    r.finished = True


if (__name__ == "__main__"):
    
    r = Robot()
    r.displayGoals = False

    problemThread = Thread(target=Problem3)
    problemThread.isDaemon = True
    problemThread.e = Event()
    problemThread.start()

    r.Run()    
    problemThread.e.set()
    problemThread.join()

    

    
