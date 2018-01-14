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
    #   drive to point
    
    t1 = time.time()
    while(abs(r.rLoc[0] - r.goal[0]) > .6 and abs(r.rLoc[1] - r.goal[1]) > .6):
        t2 = time.time()
        if(t2 - t1 > 60):
            if(repeatCounter == 0):
                cv2.putText(r.textArea, "points are given in (x,y) format", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 1):
                cv2.putText(r.textArea, "The point is 3 units to the left of the origin and 1 unit up", (0, 160), 2, .5, (100,200,100), 1)
                t1 = t2
                repeatCounter += 1
            if(repeatCounter == 2):
                cv2.putText(r.textArea, "Drive to the point shown", (0, 160), 2, .5, (100,200,100), 1)
                #TODO draw point on frame
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



    #e.set()
    #runThread.join()
    

    
