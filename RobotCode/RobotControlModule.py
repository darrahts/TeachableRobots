
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


    #   run with gme or other 3rd party application
    def GMEdemo(self):  
        self.tcpServer.setupLine("")
        self.responseThread.start()
        self.tcpWatcher.start()
        while(not self.finished):
            if(self.sequence != "" and self.validSequence):
                self.arduino.write(bytes(self.sequence.encode('ascii')))
                self.sequence = ""
        return
    

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
                if(ardIn != ""):
                    print("   ^ " + ardIn + " ^")
                    if(self.mode == 0):
                        print(":", end = "")
                    else:
                        print(">", end = "");
                    sys.stdout.flush()
        return


    def Write(self, toWrite):
        self.arduino.write(bytes(toWrite.encode('ascii')))
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

        
    def Run(self):
        self.tcpServer.setupLine("")
        self.responseThread.start()
        self.tcpWatcher.start()
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
            elif(self.userInput == "Q"):
                self.finished = True
                self.responseThread.join()
                self.tcpServer.closeConnection()
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




if (__name__ == "__main__"):
    try:
        try:
            c = Controller("/dev/ttyACM0")
        except:
            try:
                c = Controller("/dev/ttyACM1")
            except:
                print("couldnt open arduino port.")

        #c.Run()
        c.GMEdemo()
    except Exception as e:
        print("error.")
        print(str(e))
        traceback.print_exc()
    finally:
        try:
            c.finished = True
            if(c.tcpWatcher.isAlive()):
                c.tcpWatcher.join()
            if(c.responseThread.isAlive()):
                c.responseThread.join()
            c.Write("ms") #save parameters before finishing
            c.arduino.close()
        except:
            pass
        print("finished.")




