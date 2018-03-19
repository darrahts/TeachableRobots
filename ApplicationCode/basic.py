# -*- coding: utf-8 -*-

from teachablerobots.src.GridSpace import *
import cv2
import time


def Show(gs):
    while(not gs._finished):
        gs.Update(lambda: None)
        gs.ShowFrame()



def Capture(gs):
    i = 0
    t1 = time.time()
    while(i < 240):
        gs.Update(lambda: None)
        cv2.imwrite("picture%i.jpg" %i, gs.frame)
        i += 1
        #gs.ShowFrame()
    t2 = time.time()
    print(t2-t1)


if(__name__=="__main__"):
    gs = GridSpace("")
    #Show(gs)
    Capture(gs)
