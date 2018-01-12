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




    #e.set()
    #runThread.join()
    

    

    '''

    cv2.putText(r.textArea, "drive the robot to any point on the 'X' axis", (0, 60), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "drive the robot to any point on the 'Y' axis", (0, 80), 2, .5, (100,200,100), 1)

    cv2.putText(r.textArea, "drive the robot to an area with negative 'Y' values", (0, 100), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "drive the robot to an area with both positive 'X' and 'Y' values", (0,120), 2, .5, (100,200,100), 1)
    

    cv2.putText(r.textArea, "the origin is where the 'X' and 'Y' axis intersect.", (0, 160), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "the 'X' axis is horizontal, try again.", (0, 180), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "the 'Y' axis is horizontal, try again.", (0, 200), 2, .5, (100,200,100), 1)
    
    cv2.putText(r.textArea, "positive 'Y' values are above the origin... (try again)", (0, 220), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "if negative 'X' values are left of the origin... (try again)", (0, 240), 2, .5, (100,200,100), 1)
    

    cv2.putText(r.textArea, "Nice Work!", (0, 300), 4, 1.2, (100,200,100), 1)
    cv2.putText(r.textArea, "Great!", (0, 340), 4, 1.2, (100,200,100), 1)
    cv2.putText(r.textArea, "Good Job!", (0, 380), 4, 1.2, (100,200,100), 1)
    cv2.putText(r.textArea, "Excellent!", (0, 420), 4, 1.2, (100,200,100), 1)
    cv2.putText(r.textArea, "Well Done!", (0, 460), 4, 1.2, (100,200,100), 1)


'''











    
