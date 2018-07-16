import sys
sys.path.append("/home/pi/")
sys.path.append("/home/pi/teachablerobots/")
sys.path.append("/home/pi/teachablerobots")
sys.path.append("/home/pi")
import traceback
from teachablerobots.src.RobotControlModule import *
import argparse

    

if (__name__ == "__main__"):

    #ap = argparse.ArgumentParser()
    #ap.add_argument("-m", "--mode", required=True, help="mode")
    #args = vars(ap.parse_args())
    
    c = object
    try:
        try:
            c = Controller("/dev/ttyACM1") #, eval(args["mode"]))
        except Exception as e:
            print("exception")
            #print(str(e))
            #traceback.print_exc()
            try:
                c = Controller("/dev/ttyACM0")
            except:
                print("couldnt open arduino port.")

        c.Run()
    except Exception as e:
        print("error.")
        print(str(e))
        traceback.print_exc()
    finally:
        c.Stop()





