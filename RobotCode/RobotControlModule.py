
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

        self.appComm = threading.Thread(target=self.GetObjective)
        self.appClient = Communicate()
        self.appClient.port = 5680
        self.appOnline = True
        try:
            self.appClient.setupLine("192.168.1.91")
            print("connected!")
        except:
            print("app offline.")
            self.appOnline = False

        
        #   updated from arduino
        self.numSpacesMoved = 0

        #   updated from sequence
        self.direction = "right" #   "left", "up", "down" are other valid options

        #   updates from application in the form of a mathematical expression
        self.objective = ""

        #   updates form UpdateLocation function
        self.location = (-5. -3)

        #   (will succeed, number of spaces moved, ending location, distance from goal)
        self.evaluation = (True, 4, (0,0), (0,0))


    def UpdateDirection(self, val):
        if(val == '0'):
            self.direction = "right"
        elif(val == '1'):
            self.direction = "up"
        elif(val == '2'):
            self.direction = "left"
        elif(val == '3'):
            self.direction = "down"
        return

    def UpdateLocation(self):
        if(self.direction == "right"):
            self.location[0] = self.location[0] + 1
        elif(self.direction == "left"):
            self.location[0] = self.location[0] - 1
        elif(self.direction == "up"):
            self.location[1] = self.location[1] + 1
        else:
            self.location[1] = self.location[1] - 1
        return

    def EvaluateSequence(self):
        #TODO Evaluates sequence
        pass

    def SendEvaluation(self):
        if(appOnline):
            self.appClient.sendMessage({"evaluation" : self.evaluation})
        else:
            print("app offline")
        return

    def SendDirection(self):
        if(appOnline):
            self.appClient.sendMessage({"direction" : self.direction })
        else:
            print("app offline")
        return
        

    def SendLocation(self):
        if(appOnline):
            self.appClient.sendMessage({"location" : self.location })
        else:
            print("app offline")
        return

    #   from application
    def GetResponse(self):
        #TODO for receiving objective from application
        while(not self.finished):
            if(len(self.appClient.inbox) > 0):
                temp = self.appClient.inbox.pop()
                if("objective" in temp):
                    self.objective = temp["objective"]
                print(self.objective)
        self.appClient.finished = True
        return

        
    #   from arduino
    def GetResponse(self):
        ardIn = ""
        while(not self.finished):
            if(self.arduino.inWaiting() > 0):
                ardIn = self.Read(False)
                print(ardIn)
                if(ardIn == '~'):
                    time.sleep(.25)
                    ardIn = self.Read(True)
                    print(ardIn)
                elif(ardIn == '+'):
                    time.sleep(.25)
                    self.numSpacesMoved += 1
                    self.UpdateLocation()
                    print(self.numSpacesMoved)
                elif(ardIn == '$'):
                    time.sleep(.25)
                    ardIn = self.Read(False)
                    self.UpdateDirection(ardIn)
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
        return


    #   from arduino
    def Read(self, line):
        temp = ""
        if(line):
            temp = self.arduino.readline().decode("ascii")
        else:
            temp = self.arduino.readline().decode("ascii")
        temp = temp.replace("\r", "")
        temp = temp.replace("\n", "")
        return temp


    #   to arduino
    def Write(self, toWrite):
        self.arduino.write(bytes(toWrite.encode('ascii')))
        return
    
        
    def Run(self):
        self.responseThread.start()
        if(self.appOnline):
            self.appComm.start()
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
        return
                    


    

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
            c.appCom.finished = True
            c.appComm.closeConnection()
        except:
            pass
        print("finished.")




