# -*- coding: utf-8 -*-

from RobotTracker import *
import time
from threading import Thread, Event




def Problem3():
    repeatCounter = 0
    time.sleep(1)
    counter = 0

    oneFound = False
    twoFound = False
    threeFound = False
    fourFound = False
    ############################################################################################
    #   drive to point

    r.displayGoals = True
    t1 = time.time()

    cv2.putText(r.textArea, "Amazon is adding new drone routes to Nashville! They need", (0, 40), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "coordinates for some of the locations, help them out by", (0, 55), 2, .5, (100,200,100), 1)
    cv2.putText(r.textArea, "driving the robot to each new location in one sequence.", (0, 70), 2, .5, (100,200,100), 1)

    print("first, enter the coordinates for the Amazon Warehouse, location 1")
    print("ex, if the coordinates are (5,5), enter 5,5 without parentheses")
    userIn = input("> ")
    while(userIn != "2,-2"):
        if(repeatCounter == 0):
            print("double check your entry...")
            repeatCounter += 1
        elif(repeatCounter == 1):
            print("x is positive and y is negative...")
            repeatCounter += 1
        elif(repeatCounter == 2):
            print("maybe you need some extra assistance...")
        userIn = input("> ")
    print("Great!")

    print("enter the coordinates for the office1, location 2")
    userIn = input("> ")
    while(userIn != "2,1"):
        if(repeatCounter == 0):
            print("double check your entry...")
            repeatCounter += 1
        elif(repeatCounter == 1):
            print("x is positive and y is positive...")
            repeatCounter += 1
        elif(repeatCounter == 2):
            print("maybe you need some extra assistance...")
        userIn = input("> ")

    print("enter the coordinates for the office2, location 3")
    userIn = input("> ")
    while(userIn != "-2,1"):
        if(repeatCounter == 0):
            print("double check your entry...")
            repeatCounter += 1
        elif(repeatCounter == 1):
            print("x is negative and y is positive...")
            repeatCounter += 1
        elif(repeatCounter == 2):
            print("maybe you need some extra assistance...")
        userIn = input("> ")

    print("enter the coordinates for the office3, location 4")
    userIn = input("> ")
    while(userIn != "1,4"):
        if(repeatCounter == 0):
            print("double check your entry...")
            repeatCounter += 1
        elif(repeatCounter == 1):
            print("x is positive and y is positive...")
            repeatCounter += 1
        elif(repeatCounter == 2):
            print("maybe you need some extra assistance...")
        userIn = input("> ")

    r.displayGoalLoc = True
    while(counter != 4):
        time.sleep(2)
        if(r.location == str(r.points[0]) and oneFound == False):
            counter += 1
            oneFound = True
        if(r.location == str(r.points[1]) and twoFound == False):
            counter += 1
            twoFound = True
        if(r.location == str(r.points[2]) and threeFound == False):
            counter += 1
            threeFound = True
        if(r.location == str(r.points[3]) and fourFound == False):
            counter += 1
            fourFound = True
        

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

    

    
