import socket
from collections import deque
from threading import Thread, Event
from multiprocessing import Process, Queue, Event, Value
import weakref
import time
import traceback
import ast


#this class manages the communication between the robot and the application
class AppComm(object):
    def __init__(self, parent, ipAdr, port):
        self.appClient = SocketComm(port)
        self.appOnline = False
        self.robot = weakref.ref(parent)
        
        try:
            print("waiting to connect to application...")
            while(not self.appOnline):
                try:
                    if(self.appClient.setupLine(ipAdr)):
                        self.appClient.finished.value = False
                        self.appOnline = True
                        print("connected!")
                        break
                except Exception as e:
                    pass

        except:
            print("app offline.")

    def SendEvaluation(self):
        if(self.appOnline):
            self.appClient.sendMessage({"evaluation" : self.robot().evaluation})
        return

    def SendDirection(self):
        if(self.appOnline):
            d = dict()
            d["direction"] = self.robot().direction
            #print("direction: " + str(self.robot().direction))
            self.appClient.sendMessage(str(d))
        return
        

    def SendLocation(self):
        if(self.appOnline):
            d = dict()
            d["location"] = str(self.robot().location)
            #print("location: " + str(self.robot().location))
            self.appClient.sendMessage(str(d))
        return

    def SendMessage(self, message):
        if(self.appOnline):
            d = dict()
            d["message"] = message
            self.appClient.sendMessage(str(d))
        return




class SocketComm(object):
    def __init__(self,port):
        self.address = ""
        self.otherAddress = object
        self.port = port
        self.finished = Value("b", True)
        self.inbox = Queue()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.getMessagesProcess = Process(target=self.getMessages)
        self.getMessagesProcess._stop_event = Event()
        self.getMessagesProcess.daemon = True
        
        self.e = Event()
        self.connected = False
        self.timeout = 3
        return
    
    def setupLine(self, addr):
        self.address = addr
        if self.address is "": #i.e. server on raspberry pi
            try:
                self.connection.settimeout(self.timeout)
                self.connection.bind((self.address, self.port))
                print("binding with port: " + str(self.port))
                self.connection.listen(1)
                self.connection, self.otherAddress = self.connection.accept()
                print("connected to client at: " + self.otherAddress[0])
            except socket.error as e:
                print(str(e))
                return False
        else:
            try:
                #print("connecting to port: " + str(self.port))
                self.connection.connect((self.address, self.port)) # i.e. client
                print("connected to server")
            except socket.error as e:
                #print(str(e))
                return False
                
        self.getMessagesProcess.start()
        self.connected = True
        self.finished.value = False
        print("inbox at: " + str(id(self.inbox)))
        return True

    def sendMessage(self, msg):
        try:
            self.connection.send(str.encode(msg))
            print("sent: " + str(msg))
        except Exception as e:
            #print(str(e))
            #traceback.print_exc()
            print("exception caught.")
        return

    def getMessages(self):
        print("getting messages now")
        self.connection.settimeout(1)
        while(not self.finished.value):
            #print("checking inbox")
            #print("inbox length: " + str(len(self.inbox)))
            try:
                received = self.connection.recv(1024)
                decoded = received.decode('utf-8')
                if len(decoded) > 0:
                    if(decoded == "end"):
                        self.finished.value = True
                    else:
                        self.inbox.put(decoded)
                        print("received: " + str(decoded))
            except socket.error as e:
                if(type(e).__name__ == "timeout"):
                    pass
                else:
                    print("endpoint closed.")
                    self.finished.value = True
        return

    def closeConnection(self):
        if(self.connected):
            self.finished.value = True
            self.e.set()
            self.getMessagesProcess._stop_event.set()
            self.sendMessage("end")
            try:
                self.getMessagesProcess.join()
            except:
                pass
            self.connection.close()
        return



##if(__name__ == "__main__"):
##    robotClient = Communicate()
##    robotClient.setupLine("127.0.0.1")
##    while(True):
##        val = input("enter something: ")
##        robotClient.sendMessage(val)


##if(__name__ == "__main__"):
##    try:
##        robotServer = Communicate()
##        print("waiting for client to connect...")
##        robotServer.setupLine("")
##        print("connected!")
##        while(True):
##            if(len(robotServer.inbox) > 0):
##                print(robotServer.inbox.pop())
##            if(robotServer.finished):
##                break
##                #robotServer.closeConnection()
##    except:
##        pass
##    finally:
##        robotServer.closeConnection()












    
