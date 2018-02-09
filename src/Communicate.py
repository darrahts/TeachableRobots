import socket
from collections import deque
from threading import Thread, Event
import weakref
import time


#this class manages the communication between the robot and the application
class AppComm(object):
    def __init__(self, parent, ipAdr, port):
        #self.appCommThread = Thread(target=self.GetAppResponse)
        self.appClient = SocketComm()
        self.appClient.port = port
        self.appOnline = True
        self.robot = weakref.ref(parent)
        
        try:
            self.appClient.setupLine(ipAdr)
            self.appClient.finished = False
            print("connected!")
        except:
            print("app offline.")
            self.appOnline = False

    def SendEvaluation(self):
        if(self.appOnline):
            self.appClient.sendMessage({"evaluation" : self.robot().evaluation})
        return

    def SendDirection(self):
        if(self.appOnline):
            d = dict()
            d["direction"] = self.robot().direction
            self.appClient.sendMessage(str(d))
        return
        

    def SendLocation(self):
        if(self.appOnline):
            d = dict()
            d["location"] = str(self.robot().location)
            print("sent: " + str(self.robot().location))
            self.appClient.sendMessage(str(d))
        return

    def SendMessage(self, message):
        if(self.appOnline):
            d = dict()
            d["message"] = message
            self.appClient.sendMessage(str(d))
        return

    #   from application
    def GetAppResponse(self):
        time.sleep(1)
        while(not self.robot().finished):
            if(len(self.appClient.inbox) > 0):
                temp = ast.literal_eval(self.appClient.inbox.pop())
                if("objective" in temp):
                    self.robot().objective = temp["objective"]
                print(self.objective)
        self.appClient.finished = True
        return




class SocketComm(object):
    def __init__(self):
        self.address = ""
        self.port = 5580
        self.finished = False
        self.inbox = deque()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.getMessagesThread = Thread(target=self.getMessages)
        self.getMessagesThread._stop_event = Event()
        self.getMessagesThread.daemon = True
        self.e = Event()
        self.connected = False
        return
    
    def setupLine(self, addr):
        self.address = addr
        if self.address is "": #i.e. server on raspberry pi
            try:
                self.connection.settimeout(10)
                self.connection.bind((self.address, self.port))
                self.connection.listen(1)
                self.connection, otherAddress = self.connection.accept()
                print("connected to: " + otherAddress[0])
            except socket.error as e:
                self.connected = False
                self.finished = True
                return False
        else:
            try:
                self.connection.connect((self.address, self.port)) # i.e. client
                print("line setup.")
            except socket.error as e:
                self.connected = False
                self.finished = True
                return False
                
        self.getMessagesThread.start()
        self.connected = True
        return True

    def sendMessage(self, msg):
        if(self.finished):
            print("i am finished.")
        if not self.finished:
            try:
                self.connection.send(str.encode(msg))
                print("sent: " + str.encode(msg))
            except:
                print("endpoint closed.")
        return

    def getMessages(self):
        self.connection.settimeout(1)
        while not self.finished:
            try:
                received = self.connection.recv(1024)
                decoded = received.decode('utf-8')
                if len(decoded) > 0:
                    if decoded == "end":
                        self.finished = True
                    else:
                        self.inbox.appendleft(decoded)
            except socket.error as e:
                if(type(e).__name__ == "timeout"):
                    pass
                else:
                    print("endpoint closed.")
                self.finished = True
        return

    def closeConnection(self):
        if(self.connected):
            self.finished = True
            self.e.set()
            self.getMessagesThread._stop_event.set()
            self.sendMessage("end")
            try:
                self.getMessagesThread.join()
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












    
