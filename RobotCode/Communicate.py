import socket
from collections import deque
from threading import Thread, Event

class Communicate(object):
    def __init__(self):
        self.address = ""
        self.port = 5580
        self.finished = False
        self.inbox = deque()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.getMessagesThread = Thread(target=self.getMessages)
        self.getMessagesThread.daemon = True
        self.e = Event()
        print(self.address)
        return
    
    def setupLine(self, addr):
        self.address = addr
        if self.address is "": #i.e. server on raspberry pi
            try:
                self.connection.bind((self.address, self.port))
                self.connection.listen(1)
                self.connection, otherAddress = self.connection.accept()
                print("connected to: " + otherAddress[0])
            except socket.error as msg:
                print(msg)
        else:
            self.connection.connect((self.address, self.port)) # i.e. client
        self.getMessagesThread.start()
        return

    def sendMessage(self, msg):
        self.connection.send(str.encode(msg))
        return

    def getMessages(self):
        while not self.finished:
            received = self.connection.recv(1024)
            decoded = received.decode('utf-8')
            if len(decoded) > 0:
                if decoded == "connection closed.":
                    print("connection closed.")
                if decoded == "client disconnected.":
                    self.finished = True
                else:
                    self.inbox.appendleft(decoded)
        return

    def closeConnection(self):
        self.finished = True
        self.e.set()
        self.getMessagesThread.join()
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












    
