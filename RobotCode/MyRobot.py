
import traceback
from teachablerobots.src.RobotControlModule import *


    

if (__name__ == "__main__"):
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
        #c.GMEdemo()
    except Exception as e:
        print("error.")
        print(str(e))
        traceback.print_exc()
    finally:
        try:
            if(c.tcpWatcher.isAlive()):
                c.tcpWatcher.join()
            print("tcp watcher thread joined.")
            if(c.responseThread.isAlive()):
                c.responseThread.join()
            print("response thread joined.")
            c.Write("ms") #save parameters before finishing
            c.arduino.close()
            c.tcpServer.closeConnection()
            print("tcp server closed.")
            c.appComm.finished = True
            c.appComm.appClient.closeConnection()
            print("appcomm closed.")
        except Exception as e:
            print("An exception during program exit occured.")
            print(str(e))
            traceback.print_exc()
        print("finished.")





