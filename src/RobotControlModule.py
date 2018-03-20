
import serial
import time
import threading
import sys
import traceback
from teachablerobots.src.Communicate import AppComm
from teachablerobots.src.Sense import Sense
from teachablerobots.src.Hardware import *
import ast
from multiprocessing import Process, Queue, Event, Value, Lock, Manager
from ctypes import c_char_p


def TryParseInt(val):
    try:
        return int(val)
    except ValueError:
        return False




class Controller(object):
    def __init__(self, port, withApp=True):


        self.m = Manager()
        self.userInput = self.m.Value(c_char_p, b"")
        self.lock = Lock()
        self.tokens = []
        self.cmds = []
        self.sequence = ""
        self.finished = False
        self.validSequence = False
        self.withApp = withApp

        self.sensors = Sense()
        
        #   This is how the robot connects to the application
        if(self.withApp):
            self.appComm = AppComm(self, "192.168.1.91", 5580)
        
            self.appResponseProcess = Process(target=self.GetAppResponse, args=(self.userInput,))
            #self.appResponseProcess.daemon = True
            self.appResponseProcess.e = Event()
        
        #   arduino communication
        self.arduino = serial.Serial(port, 9600)
        self.arduinoResponseThread = threading.Thread(target=self.GetArduinoResponse)
        self.arduinoResponseThread.e = threading.Event()


        self.rangeProcess = Process(target=self.WatchRange, args=(self.sensors.currentRange,))
        self.rangeProcess.e = Event()

        
        self.mode = 0 #0 for auto, 1 for manual used for char display on terminal

        
        #   updated from arduino
        self.numSpacesMoved = 0

        #   updated from sequence
        self.direction = "right" #   "left", "up", "down" are other valid options

        #   updates from application in the form of a mathematical expression
        self.objective = ""

        #   updates form UpdateLocation function
        self.location = (-5, -3)

        #   (will succeed, number of spaces moved, ending location, distance from goal)
        self.evaluation = (True, 4, (0,0), (0,0))



    def WatchRange(self, r):
        '''monitors the robot's range and stops it if necessary'''
        while(not self.finished):
            #print(r.value)
            time.sleep(1)
            self.appComm.SendRange()
            if(r.value > 0 and r.value < 20):
                TriggerInterrupt()
                print("Too Close!")
                while(r.value < 20):
                    pass
        


    def UpdateDirection(self, val):
        if(val == '0'):
            self.direction = "right"
        elif(val == '1'):
            self.direction = "up"
        elif(val == '2'):
            self.direction = "left"
        elif(val == '3'):
            self.direction = "down"
        self.appComm.SendDirection()
        return

    def UpdateLocation(self):
        #print("updating location")
        if(self.direction == "right"):
            self.location = (self.location[0]+1, self.location[1])
        elif(self.direction == "left"):
            self.location = (self.location[0]-1, self.location[1])
        elif(self.direction == "up"):
            self.location = (self.location[0], self.location[1]+1)
        else:
            self.location = (self.location[0], self.location[1]-1)
        self.appComm.SendLocation()
        return

    def EvaluateSequence(self):
        #TODO Evaluates sequence
        pass


    #   from application
    def GetAppResponse(self, userInput):
        time.sleep(1)
        while(not self.appComm.appClient.finished.value):
            #print("checking app response")
            time.sleep(.5)
            if(not self.appComm.appClient.inbox.empty()):
                #print("new message!")
                temp = ast.literal_eval(self.appComm.appClient.inbox.get())
                if("objective" in temp):
                    self.objective = temp["objective"]
                    print(self.objective)
                elif("sequence" in temp):
                    self.lock.acquire()
                    try:
                        userInput.value = temp["sequence"].rstrip().encode('ascii')
                        print("user input is: " + userInput.value.decode('ascii'))
                    finally:
                        self.lock.release()
                    #self.robot().arduino.write(bytes(self.sequence.encode('ascii')))
        print("finished")   
        return

        
    #   from arduino
    def GetArduinoResponse(self):
        ardIn = ""
        while(not self.finished):
            if(self.arduino.inWaiting() > 0):
                #print("arduino sent a message!")
                ardIn = self.Read(False)
                print(ardIn)
                if(ardIn == '~'):
                    time.sleep(.25)
                    ardIn = self.Read(True)
                #    print(ardIn)
                elif(ardIn == '+'):
                    time.sleep(.25)
                    self.numSpacesMoved += 1
                    if(self.withApp):
                        self.UpdateLocation()
                #    print("+")
                #    print(self.numSpacesMoved)
                elif(ardIn == '$'):
                    time.sleep(.25)
                    ardIn = self.Read(False)
                    if(self.withApp):
                        self.UpdateDirection(ardIn)
                elif(ardIn != ""):
                #    print("   ^ " + ardIn + " ^")
                    if(self.mode == 0):
                        print(":", end = "")
                    else:
                        print(">", end = "");
                    sys.stdout.flush()
        return


    #   from terminal
    def GenerateCommandSequence(self, userIn):
        if(userIn == ""):
            print("returning")
            return
        for a in userIn.split(','):
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
            elif("stop" in val):
                x = "*"
            elif(TryParseInt(val) != False and int(val) < 10):
                x = val + "_"
            else:
                print(val)
                print("couldn't parse the commands. check your entry.")
                self.validSequence = False
                return False
            self.cmds.append(x)
        self.sequence = "".join(self.cmds)
        print("valid sequence")
        self.validSequence = True
        return True


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


    def ManualMode(self):
        while(True):
            time.sleep(.1)
            self.userInput.value = input(">")
            time.sleep(.1)
            self.arduino.write(bytes(self.userInput.value.encode('ascii')))
            if(self.userInput.value == "q"):
                self.userInput.value = ""
                break
        return


    #   from arduino
    def Read(self, line):
        temp = ""
        try:
            if(line):
                temp = self.arduino.readline().decode("ascii")
            else:
                temp = self.arduino.read().decode("ascii")
            temp = temp.replace("\r", "")
            temp = temp.replace("\n", "")
        except UnicodeDecodeError as e:
            print("ignoring decode error.")
        return temp


    #   to arduino
    def Write(self, toWrite):
        self.arduino.write(bytes(toWrite.encode('ascii')))
        return
    
        
    def Run(self):
        userIn = ""
        condition = ""
        
        if(self.withApp):
            if(self.appComm.appOnline):
                print("app comm online")
                self.appResponseProcess.start()
                print(self.appComm.appClient.connection)
                #print("inbox at: " + str(id(self.appComm.appClient.inbox)))
                condition = "not self.finished and not self.appComm.appClient.finished.value"
            else:
                return
        else:
            condition = "not self.finished"

        self.sensors.rangeProcess.start()
        self.rangeProcess.start()
        self.arduinoResponseThread.start()
        self.Write("ml") #load parameters before beginning
        
        while(eval(condition)):
            self.lock.acquire()
            if(not self.withApp):
                self.userInput.value = input(":").encode('ascii')
            try:
                userIn = self.userInput.value.decode('ascii')
            finally:
                self.lock.release()
                
            if(userIn == "mm"):
                self.mode = 1
                self.arduino.write(bytes(userIn.encode('ascii')))
                time.sleep(.5)
                self.ManualMode()
                self.mode = 0
            elif(userIn == "mv" or userIn == "md" or userIn == "mr" or userIn == "ml" or userIn == "ms"):
                self.arduino.write(bytes(userIn.encode('ascii')))
                self.lock.acquire()
                try:
                    self.userInput.value = b""
                finally:
                    self.lock.release()
            elif(userIn == "cd"): #   prints values from the sonic range sensor
                for i in range(0,5):
                    print(self.sensors._getRange())
                    time.sleep(.05)
            
            elif(userIn == "Q"):
                self.finished = True
                print("ending the program.")
                break

            elif(userIn != "" and userIn != "Q" and "m" not in userIn):
                print("user input is: " + userIn)
                if(self.GenerateCommandSequence(userIn)):
                    #print("sent: " + self.sequence)
                    self.arduino.write(bytes(self.sequence.encode('ascii')))
                    self.lock.acquire()
                    try:
                        self.userInput.value = b""
                    finally:
                        self.lock.release()
                    self.sequence = ""
                    self.tokens = []
                    self.cmds = []
            else:
                pass
            #print("resetting userIn")
            userIn = ""

        self.Stop()
        return




    def Stop(self):
        try:
            self.finished = True
            self.sensors.finished.value = True
            if(self.sensors.rangeProcess.is_alive()):
                self.sensors.rangeProcess.e.set()
                self.sensors.rangeProcess.terminate()
                self.sensors.rangeProcess.join()
            if(self.rangeProcess.is_alive()):
                self.rangeProcess.e.set()
                self.rangeProcess.terminate()
                self.rangeProcess.join()
            self.appComm.appClient.finished.value = True #process
            self.appComm.appClient.closeConnection()
            if(self.appResponseProcess.is_alive()):
                print("joining app response process ")
                self.appResponseProcess.e.set()
                self.appResponseProcess.join()
            #if(self.appResponseThread.isAlive()):
            #    self.appResponseThread.e.set()
            #    self.appResponseThread.join()
                print("app thread joined.")
            if(self.arduinoResponseThread.isAlive()):
                self.arduinoResponseThread.e.set()
                self.arduinoResponseThread.join()
      #      if(self.inputThread.isAlive()):
      #          self.inputThread.e.set()
      #          self.inputThread.join()
                print("arduino thread joined.")
            self.Write("ms") #save parameters before finishing
            self.arduino.close()
            #self.tcpServer.closeConnection()
            #print("tcp server closed.")
        except Exception as e:
            #print("An exception during program exit occured.")
            #print(str(e))
            #traceback.print_exc()
            pass
        HardwareCleanup()
        print("finished.")



















        
    
