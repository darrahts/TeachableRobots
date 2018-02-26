
import traceback
from teachablerobots.src.RobotControlModule import *


    

if (__name__ == "__main__"):
    c = object
    try:
        try:
            c = Controller("/dev/ttyACM0")
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            try:
                c = Controller("/dev/ttyACM1")
            except:
                print("couldnt open arduino port.")

        c.Run()
    except Exception as e:
        print("error.")
        print(str(e))
        traceback.print_exc()
    finally:
        c.Stop()





