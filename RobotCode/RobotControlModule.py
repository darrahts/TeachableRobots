
import serial
import time
import threading
import sys
import traceback
from Communicate import *

def TryParseInt(val):
    try:
        return int(val)
    except ValueError:
        return False



class Controller(object):
    def __init__(self, port):
        self.appComm = threading.Thread(target=self.GetObjective)
        self.tcpWatcher = threading.Thread(target=self.GetCommandSequence)
        self.responseThread = threading.Thread(target=self.GetResponse)
        self.arduino = serial.Serial(port, 9600)
        self.mode = 0 #0 for auto, 1 for manual
        self.userInput = ""
        self.tokens = []
        self.cmds = []
        self.sequence = ""
        self.finished = False
        self.validSequence = False
        self.tcpServer = Communicate()
        self.appClient = Communicate()

        #   updated from arduino
        self.numSpacesMoved = 0

        #   updated from sequence
        self.direction = 0 

        #   updates from application in the form of a mathematical expression
        self.objective = ""

        #   updates form UpdateLocation function
        self.location = (0,0)

        #   (will succeed, number of spaces moved, ending location, distance from goal)
        self.evaluation = (True, 4, (0,0), (0,0))


    def UpdateDirection(self):
        #TODO update from sequence
        pass

    def UpdateLocation(self):
        #TODO update location from current location plus number of spaces in what direction
        pass

    def EvaluateSequence(self):
        #TODO Evaluates sequence
        pass

    def SendEvaluation(self):
        #TODO send eval to application
        pass

    def SendLocation(self):
        #TODO send location to application
        pass

    #   from application
    def GetObjective(self):
        #TODO for receiving objective from application
        pass
    

    #   from arduino
    def GetResponse(self):
        ardIn = ""
        while(not self.finished):
            if(self.arduino.inWaiting() > 0):
                ardIn = self.arduino.read().decode("ascii")
                ardIn = ardIn.replace("\r", "")
                ardIn = ardIn.replace("\n", "")
                if(ardIn == '~'):
                    time.sleep(.25)
                    ardIn = self.arduino.readline().decode("ascii")
                    ardIn = ardIn.replace("\r", "")
                    ardIn = ardIn.replace("\n", "")
                elif(ardIn == '$'):
                    time.sleep(.25)
                    self.numSpacesMoved += 1
                    
                elif(ardIn != ""):
                    print("   ^ " + ardIn + " ^")
                    if(self.mode == 0):
                        print(":", end = "")
                    else:
                        print(">", end = "");
                    sys.stdout.flush()
        return


    #   from gme or other 3rd party application using tcpWatcher thread
    def GetCommandSequence(self):
        while(not self.finished):
            if(len(self.tcpServer.inbox) > 0):
                self.sequence = self.tcpServer.inbox.pop()
                if(self.sequence == "0"):
                    self.finished = True
                    self.validSequence = False
                    print("finished!")
                else:
                    self.validSequence = True
                    print(self.sequence)
            if(self.tcpServer.finished):
                break
        return

    #   from terminal
    def GenerateCommandSequence(self):
        userIn = self.userInput.split(',')
        for a in userIn:
            t = a.split(' ')
            for b in t:
                if b is not "":
                    self.tokens.append(b)
        for val in self.tokens:
            x = ""
            if(val == "forward"):
                x = "1-"
            elif(val == "back"):
                x = "2-"
            elif(val == "left"):
                x = "3-90_"
            elif(val == "right"):
                x = "4-90_"
            elif(val == "stop"):
                x = "*"
            elif(TryParseInt(val) != False):
                x = val + "_"
            else:
                print("couldn't parse the commands. check your entry.")
                self.validSequence = False
                return
            self.cmds.append(x)
        self.sequence = "".join(self.cmds)
        self.validSequence = True
        return


    #   run with gme or other 3rd party application
    def GMEdemo(self):
        print("awaiting connection...")
        self.tcpServer.setupLine("")
        self.tcpWatcher.start()
        while(not self.finished):
            if(self.sequence != "" and self.validSequence):
                self.arduino.write(bytes(self.sequence.encode('ascii')))
                self.sequence = ""
        return


    def ManualMode(self):
        while(True):
            time.sleep(.1)
            self.userInput = input(">")
            time.sleep(.1)
            self.arduino.write(bytes(self.userInput.encode('ascii')))
            if(self.userInput == "q"):
                self.userInput = ""
                break


    #   to arduino
    def Write(self, toWrite):
        self.arduino.write(bytes(toWrite.encode('ascii')))
        return
    
        
    def Run(self):
        self.responseThread.start()
        self.Write("ml") #load parameters before beginning
        while(not self.finished):
            self.userInput = input(":")
            if(self.userInput == "mm"):
                self.mode = 1
                self.arduino.write(bytes(self.userInput.encode('ascii')))
                time.sleep(.5)
                self.ManualMode()
                self.mode = 0
            elif(self.userInput == "mv" or self.userInput == "md" or self.userInput == "mr" or self.userInput == "ml" or self.userInput == "ms"):
                self.arduino.write(bytes(self.userInput.encode('ascii')))
            elif(self.userInput == "G"):
                self.GMEdemo()
                self.finished = False
            elif(self.userInput == "Q"):
                self.finished = True
                self.responseThread.join()
                break
            else:
                self.GenerateCommandSequence()
                if(self.validSequence):
                    #print("sent: " + self.sequence)
                    self.arduino.write(bytes(self.sequence.encode('ascii')))
            self.userInput = ""
            self.sequence = ""
            self.tokens = []
            self.cmds = []
                    


    

if (__name__ == "__main__"):
    try:
        try:
            c = Controller("/dev/ttyACM0")
        except:
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
        except:
            pass
        print("finished.")




